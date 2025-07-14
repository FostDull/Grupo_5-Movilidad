import './App.css';
import { useEffect, useState, useRef, useCallback } from 'react';

function App() {
  // Estados para el monitoreo en vivo (contadores y estado general)
  const [threatCount, setThreatCount] = useState(0); 
  const [weaponCount, setWeaponCount] = useState(0); 
  const [status, setStatus] = useState('Todo en orden'); 

  // Estados para la alerta inmediata/temporal
  const [immediateAlertMessage, setImmediateAlertMessage] = useState(''); 
  const [isImmediateAlertActive, setIsImmediateAlertActive] = useState(false); 
  const immediateAlertTimeoutId = useRef(null); 

  // Estados para el panel de alertas registradas
  const [registeredAlerts, setRegisteredAlerts] = useState([]); 
  const [selectedAlert, setSelectedAlert] = useState(null); 
  const [alertVideoUrl, setAlertVideoUrl] = useState('');
  const [alertReport, setAlertReport] = useState('');

  // Ref para la instancia del WebSocket (para asegurar una única conexión)
  const wsRef = useRef(null); 

  // --- ESTADOS Y REFS PARA LA GRABACIÓN DE VIDEO ---
  const ipCamRecordingUrl = "http://192.168.100.204:8080/video"; 
  const ipCamRecordingImgRef = useRef(null); 
  const canvasRef = useRef(null); 
  const ctxRef = useRef(null); 

  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const captureIntervalRef = useRef(null);
  const framesCapturedRef = useRef(0);
  const mimeTypeRef = useRef('video/mp4'); 

  const [isRecording, setIsRecording] = useState(false); 
  const [recordingStatus, setRecordingStatus] = useState("Listo para grabar"); 
  const [recordingStatusType, setRecordingStatusType] = useState("info"); 

  // --- NUEVOS ESTADOS PARA EL FORMULARIO DE DENUNCIA ---
  const [denunciaDescripcion, setDenunciaDescripcion] = useState('');
  const [denunciaUbicacion, setDenunciaUbicacion] = useState('');
  const [denunciaLatitud, setDenunciaLatitud] = useState('');
  const [denunciaLongitud, setDenunciaLongitud] = useState('');
  const [denunciaArchivo, setDenunciaArchivo] = useState(null);
  const [denunciaStatus, setDenunciaStatus] = useState('');
  const [denunciaStatusType, setDenunciaStatusType] = useState('info');


  // Función para cargar alertas registradas del backend (desde el puerto 8000)
  const fetchRegisteredAlerts = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/alerts');
      if (response.ok) {
        const data = await response.json();
        setRegisteredAlerts(data.reverse()); 
      } else {
        console.error('Error al cargar alertas registradas:', response.statusText);
      }
    } catch (error) {
      console.error('Error de red al cargar alertas registradas:', error);
    }
  }, []);

  // Función para manejar clic en una alerta registrada
  const handleRegisteredAlertClick = async (alert) => {
    setSelectedAlert(alert);
    setAlertVideoUrl(`http://localhost:8000/alert_reports/${alert.video_file}`); 
    
    try {
      const response = await fetch(`http://localhost:8000/alert_reports/${alert.report_file}`); 
      if (response.ok) {
        const text = await response.text();
        setAlertReport(text);
      } else {
        setAlertReport('No se pudo cargar el reporte.');
        console.error('Error al cargar reporte:', response.statusText);
      }
    } catch (error) {
      setAlertReport('Error de red al cargar reporte.');
      console.error('Error de red al cargar reporte:', error);
    }
  };

  // --- Lógica de WebSocket (Monitoreo en vivo y Alertas) ---
  useEffect(() => {
    if (!wsRef.current) {
      const socket = new WebSocket("ws://localhost:8000/ws/alertas"); 
      wsRef.current = socket; 

      socket.onopen = () => {
        console.log('Conexión WebSocket establecida');
        fetchRegisteredAlerts(); 
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data); 
        console.log("Mensaje WebSocket recibido:", data); 

        if (data.type === 'metrics') {
          setThreatCount(data.threats);
          setWeaponCount(data.weapons);
          if (data.threats > 0 || data.weapons > 0) {
            setStatus('¡ACTIVIDAD ANÓMALA DETECTADA!');
          } else {
            setStatus('Todo en orden');
          }
        } else if (data.type === 'alert') {
          if (data.message !== immediateAlertMessage || !isImmediateAlertActive) {
            if (immediateAlertTimeoutId.current) {
              clearTimeout(immediateAlertTimeoutId.current);
            }
            setImmediateAlertMessage(data.message);
            setIsImmediateAlertActive(true);
            
            immediateAlertTimeoutId.current = setTimeout(() => {
              setImmediateAlertMessage('');
              setIsImmediateAlertActive(false);
            }, 8000); 
          }
        } else if (data.type === 'new_registered_alert') {
          console.log("Nueva alerta registrada recibida:", data.alert);
          // FIX: Cambiado 'previls' a 'prevAlerts'
          setRegisteredAlerts(prevAlerts => [data.alert, ...prevAlerts]); 
        }
      };

      socket.onclose = (event) => {
        console.log('Conexión WebSocket cerrada', event.code, event.reason);
        setStatus('Conexión perdida. Reintentando...');
        wsRef.current = null; 
        if (immediateAlertTimeoutId.current) {
          clearTimeout(immediateAlertTimeoutId.current);
        }
        setIsImmediateAlertActive(false);
        setImmediateAlertMessage('');
      };

      socket.onerror = (error) => {
        console.error('Error en WebSocket:', error);
        setStatus('Error de conexión. Reintentando...');
        wsRef.current = null; 
        if (immediateAlertTimeoutId.current) {
          clearTimeout(immediateAlertTimeoutId.current);
        }
        setIsImmediateAlertActive(false);
        setImmediateAlertMessage('');
      };
    } 

    return () => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
        wsRef.current = null; 
      }
      if (immediateAlertTimeoutId.current) {
        clearTimeout(immediateAlertTimeoutId.current);
      }
    };
  }, [fetchRegisteredAlerts, immediateAlertMessage, isImmediateAlertActive]); 

  // --- Lógica de Grabación de Video (Adaptada del HTML) ---

  const updateRecordingStatus = useCallback((message, type = "info") => {
    setRecordingStatus(message);
    setRecordingStatusType(type);
    console.log(`${type.toUpperCase()}: ${message}`);
  }, []);

  const checkMediaRecorderSupport = useCallback(() => {
    if (!window.MediaRecorder) {
      updateRecordingStatus("Tu navegador no soporta MediaRecorder API", "error");
      return false;
    }

    if (!MediaRecorder.isTypeSupported('video/mp4')) {
      updateRecordingStatus("MP4 no soportado. Usando WebM como alternativa.", "warning");
      mimeTypeRef.current = 'video/webm';
    } else {
      mimeTypeRef.current = 'video/mp4'; 
    }
    return true;
  }, [updateRecordingStatus]);

  // 5. Subir video (definida antes de start/stop si se llaman mutuamente)
  const uploadVideo = useCallback(async () => {
    if (chunksRef.current.length === 0) {
      updateRecordingStatus("No hay datos de video para subir", "warning");
      return;
    }

    try {
      const blob = new Blob(chunksRef.current, { type: mimeTypeRef.current });
      const fileExtension = mimeTypeRef.current.includes('mp4') ? 'mp4' : 'webm';

      updateRecordingStatus(`Video creado: ${blob.size} bytes, ${framesCapturedRef.current} frames`, "info");

      if (blob.size === 0) {
        updateRecordingStatus("El video está vacío", "warning");
        return;
      }

      const formData = new FormData();
      const fileName = `video_${Date.now()}.${fileExtension}`;
      const file = new File([blob], fileName, { type: mimeTypeRef.current });
      formData.append("file", file, fileName);

      updateRecordingStatus("Subiendo video al servidor...", "info");

      const response = await fetch("http://localhost:8001/upload-video/", { 
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }

      const result = await response.json();
      updateRecordingStatus(`✅ Video subido: ${result.mensaje}`, "success"); 

    } catch (err) {
      updateRecordingStatus(`❌ Error al subir: ${err.message}`, "error");
    } finally {
      chunksRef.current = []; 
      framesCapturedRef.current = 0; 
    }
  }, [updateRecordingStatus]);

  // 4. Detener grabación (DEFINIDA ANTES DE startRecording)
  const stopRecording = useCallback(() => {
    setIsRecording(false);
    if (captureIntervalRef.current) {
      clearInterval(captureIntervalRef.current);
      captureIntervalRef.current = null;
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
    }
    updateRecordingStatus("Grabación detenida.", "info");
  }, [updateRecordingStatus]);


  // 2. Iniciar captura de frames
  const captureFrame = useCallback(() => {
    if (!isRecording || !ctxRef.current || !ipCamRecordingImgRef.current) return;

    try {
      if (ipCamRecordingImgRef.current.naturalWidth > 0) {
        ctxRef.current.drawImage(ipCamRecordingImgRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);
        framesCapturedRef.current++;
      } else {
        // console.warn("Imagen de cámara IP no cargada para captura de frame.");
      }
    } catch (e) {
      updateRecordingStatus(`Error capturando frame: ${e.message}`, "error");
    }
  }, [isRecording, updateRecordingStatus]);

  // 3. Iniciar grabación (AHORA LLAMA A stopRecording QUE YA ESTÁ DEFINIDA)
  const startRecording = useCallback(() => {
    if (isRecording) return;

    framesCapturedRef.current = 0;
    chunksRef.current = [];
    setIsRecording(true);
    updateRecordingStatus("Iniciando captura de frames...", "info");

    if (!canvasRef.current) {
      canvasRef.current = document.createElement("canvas");
      canvasRef.current.width = 640; 
      canvasRef.current.height = 480;
    }
    if (!ctxRef.current) {
      ctxRef.current = canvasRef.current.getContext("2d");
    }

    captureIntervalRef.current = setInterval(captureFrame, 100); 

    setTimeout(() => {
      if (framesCapturedRef.current === 0) {
        updateRecordingStatus("No se capturaron frames. Verifique la cámara IP para grabación.", "error");
        stopRecording(); // stopRecording ya está definida
        return;
      }

      updateRecordingStatus(`${framesCapturedRef.current} frames capturados. Iniciando grabación...`, "info");

      try {
        const stream = canvasRef.current.captureStream(10); 

        mediaRecorderRef.current = new MediaRecorder(stream, {
          mimeType: mimeTypeRef.current
        });

        mediaRecorderRef.current.ondataavailable = e => {
          if (e.data.size > 0) {
            chunksRef.current.push(e.data);
          }
        };

        mediaRecorderRef.current.onstop = uploadVideo;
        mediaRecorderRef.current.onerror = e => {
          updateRecordingStatus(`Error en grabación: ${e.error.name}`, "error");
          stopRecording();
        };

        mediaRecorderRef.current.start(1000); 
        updateRecordingStatus(`🎥 Grabando en formato: ${mimeTypeRef.current}`, "success");

        setTimeout(() => {
          if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
            mediaRecorderRef.current.stop();
          }
        }, 10000); 

      } catch (e) {
        updateRecordingStatus(`Error al iniciar grabación: ${e.message}`, "error");
        stopRecording();
      }
    }, 500); 
  }, [isRecording, updateRecordingStatus, captureFrame, stopRecording, uploadVideo]); // Dependencias actualizadas

  useEffect(() => {
    checkMediaRecorderSupport();
  }, [checkMediaRecorderSupport]);

  // --- Lógica para el Formulario de Denuncia ---
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setDenunciaArchivo(e.target.files[0]);
    } else {
      setDenunciaArchivo(null);
    }
  };

  const handleDenunciaSubmit = async (e) => {
    e.preventDefault();
    setDenunciaStatus('Enviando denuncia...');
    setDenunciaStatusType('info');

    const formData = new FormData();
    formData.append('descripcion', denunciaDescripcion);
    formData.append('ubicacion', denunciaUbicacion);
    if (denunciaLatitud) formData.append('latitud', denunciaLatitud);
    if (denunciaLongitud) formData.append('longitud', denunciaLongitud);
    if (denunciaArchivo) formData.append('archivo', denunciaArchivo); 

    try {
      const response = await fetch('http://localhost:8001/denuncias/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }

      const result = await response.json();
      setDenunciaStatus(`✅ Denuncia registrada: ${result.mensaje}`);
      setDenunciaStatusType('success');

      setDenunciaDescripcion('');
      setDenunciaUbicacion('');
      setDenunciaLatitud('');
      setDenunciaLongitud('');
      setDenunciaArchivo(null);
      if (document.getElementById('denunciaArchivo')) {
        document.getElementById('denunciaArchivo').value = ''; 
      }

    } catch (error) {
      setDenunciaStatus(`❌ Error al registrar denuncia: ${error.message}`);
      setDenunciaStatusType('error');
      console.error('Error en denuncia:', error);
    }
  };


  return (
    <div className="App">
      <header className="app-header">
        <div className="header-left">
          {/* Imagen oculta para la grabación */}
          <img 
            ref={ipCamRecordingImgRef} 
            src={ipCamRecordingUrl} 
            alt="Cámara IP para Grabación (Oculta)" 
            style={{ display: 'none' }} 
            crossOrigin="anonymous" 
          />
          {/* Canvas oculto para la grabación */}
          <canvas ref={canvasRef} style={{ display: 'none' }}></canvas>

          <img src="http://localhost:8000/static/kuntur_logo.png" alt="Kuntur Mobility Logo" className="app-logo" />
          <h1 className="app-title">KUNTUR MOBILITY</h1> 
        </div>
        <nav className="main-nav">
          <ul>
            <li><a href="#monitoreo">Monitoreo</a></li>
            <li><a href="#alertas">Alertas</a></li>
            <li><a href="#denuncia">Denuncia</a></li> 
          </ul>
        </nav>
        <button className="config-button">Configurar</button>
      </header>

      <main className="dashboard-grid">
        {/* Card: Video en Vivo */}
        <section className="card video-card">
          <h2 className="card-title">Video en Vivo</h2>
          <div className="video-container">
            <img src="http://localhost:8000/video_feed" alt="Video en vivo" />
            {isImmediateAlertActive && <div className="alerta">{immediateAlertMessage}</div>}
          </div>
        </section>

        {/* Card: Métricas de Detección */}
        <section className="card metrics-card">
          <h2 className="card-title">Métricas de Detección</h2>
          <div className="metric-items">
            <div className="metric-item">
              <h3>Amenazas</h3>
              <p className="metric-count">{threatCount}</p>
            </div>
            <div className="metric-item">
              <h3>Armas</h3>
              <p className="metric-count">{weaponCount}</p>
            </div>
          </div>
        </section>

        {/* Card: Estado del Sistema */}
        <section className="card status-system-card">
          <h2 className="card-title">Estado del Sistema</h2>
          <div className={`status-box ${status.includes('ANÓMALA') ? 'status-alert' : 'status-normal'}`}>
            <p className="status-text">{status}</p>
          </div>
        </section>

        {/* Card: Control de Grabación */}
        <section className="card recording-control-card">
          <h2 className="card-title">Control de Grabación</h2>
          <button 
            onClick={isRecording ? stopRecording : startRecording} 
            className={`record-btn ${isRecording ? 'recording' : ''}`}
            disabled={!checkMediaRecorderSupport() && !isRecording} 
          >
            {isRecording ? "🔴 Grabando..." : "Iniciar Grabación"}
          </button>
          <div className={`recording-status ${recordingStatusType}`}>
            {recordingStatus}
          </div>
        </section>


        {/* Card: Panel de Alertas Registradas */}
        <section className="card registered-alerts-panel-card">
          <h2 className="card-title">Alertas Registradas</h2>
          <div className="alerts-list">
            {registeredAlerts.length === 0 ? (
              <p className="no-alerts-message">No hay alertas registradas aún.</p>
            ) : (
              registeredAlerts.slice(0, 5).map((alert) => ( 
                <div key={alert.id} className="alert-item" onClick={() => handleRegisteredAlertClick(alert)}>
                  <p><strong>{alert.message}</strong></p>
                  <p><small>{new Date(alert.timestamp).toLocaleString()}</small></p>
                </div>
              ))
            )}
          </div>
          {registeredAlerts.length > 5 && (
            <button className="view-all-alerts-button" onClick={() => setSelectedAlert('showAll')}>Ver todas las alertas</button>
          )}
        </section>

        {/* NUEVA CARD: Registrar Denuncia */}
        <section className="card register-denuncia-card" id="denuncia">
          <h2 className="card-title">Registrar Denuncia</h2>
          <form onSubmit={handleDenunciaSubmit} className="denuncia-form">
            <div className="form-group">
              <label htmlFor="denunciaDescripcion">Descripción:</label>
              <textarea 
                id="denunciaDescripcion" 
                value={denunciaDescripcion} 
                onChange={(e) => setDenunciaDescripcion(e.target.value)} 
                required 
                rows="3"
                placeholder="Detalles de la denuncia..."
              ></textarea>
            </div>
            <div className="form-group">
              <label htmlFor="denunciaUbicacion">Ubicación:</label>
              <input 
                type="text" 
                id="denunciaUbicacion" 
                value={denunciaUbicacion} 
                onChange={(e) => setDenunciaUbicacion(e.target.value)} 
                required 
                placeholder="Ej: Calle Principal 123"
              />
            </div>
            <div className="form-group-inline">
              <div className="form-group">
                <label htmlFor="denunciaLatitud">Latitud:</label>
                <input 
                  type="number" 
                  id="denunciaLatitud" 
                  value={denunciaLatitud} 
                  onChange={(e) => setDenunciaLatitud(e.target.value)} 
                  step="any" 
                  placeholder="Opcional"
                />
              </div>
              <div className="form-group">
                <label htmlFor="denunciaLongitud">Longitud:</label>
                <input 
                  type="number" 
                  id="denunciaLongitud" 
                  value={denunciaLongitud} 
                  onChange={(e) => setDenunciaLongitud(e.target.value)} 
                  step="any" 
                  placeholder="Opcional"
                />
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="denunciaArchivo">Adjuntar Video/Imagen (Opcional):</label>
              <input 
                type="file" 
                id="denunciaArchivo" 
                accept="video/*,image/*" 
                onChange={handleFileChange} 
              />
            </div>
            <button type="submit" className="submit-denuncia-btn">Registrar Denuncia</button>
          </form>
          {denunciaStatus && (
            <div className={`denuncia-status ${denunciaStatusType}`}>
              {denunciaStatus}
            </div>
          )}
        </section>
      </main>

      {/* Modal para detalles de alerta o para ver todas las alertas */}
      {selectedAlert && (
        <div className="alert-detail-modal">
          <div className="modal-content">
            <button className="close-modal-button" onClick={() => setSelectedAlert(null)}>✖</button>
            {selectedAlert === 'showAll' ? (
              <>
                <h3>Todas las Alertas Registradas</h3>
                <div className="alerts-list-full">
                  {registeredAlerts.length === 0 ? (
                    <p>No hay alertas registradas aún.</p>
                  ) : (
                    registeredAlerts.map((alert) => (
                      <div key={alert.id} className="alert-item" onClick={() => { handleRegisteredAlertClick(alert); }}>
                        <p><strong>{alert.message}</strong></p>
                        <p><small>{new Date(alert.timestamp).toLocaleString()}</small></p>
                      </div>
                    ))
                  )}
                </div>
              </>
            ) : (
              <>
                <h3>Detalles de Alerta: {selectedAlert.message}</h3>
                <p><strong>ID:</strong> {selectedAlert.id}</p>
                <p><strong>Tipo:</strong> {selectedAlert.type.replace('_', ' ')}</p>
                <p><strong>Fecha/Hora:</strong> {new Date(selectedAlert.timestamp).toLocaleString()}</p>
                <p><strong>Amenazas:</strong> {selectedAlert.threats}</p>
                <p><strong>Armas:</strong> {selectedAlert.weapons}</p>

                <h4>Video del Evento:</h4>
                {alertVideoUrl ? (
                  <video controls width="100%" className="alert-video">
                    <source src={alertVideoUrl} type="video/mp4" />
                    Tu navegador no soporta el tag de video.
                  </video>
                ) : (
                  <p>Cargando video...</p>
                )}

                <h4>Reporte Detallado:</h4>
                <pre className="alert-report-text">
                  {alertReport || 'Cargando reporte...'}
                </pre>

                <button onClick={() => setSelectedAlert(null)}>Cerrar</button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
