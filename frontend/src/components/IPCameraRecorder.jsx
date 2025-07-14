import React, { useEffect, useRef, useState } from "react";

export default function IPCameraRecorder() {
  const ipCamUrl = "http://192.168.100.204:8080/video";
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isRecording, setIsRecording] = useState(false);
  const [status, setStatus] = useState("Estado: Cámara activa");
  const [chunks, setChunks] = useState([]);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [framesCaptured, setFramesCaptured] = useState(0);
  const captureIntervalRef = useRef(null);
  const mimeTypeRef = useRef("video/mp4");

  useEffect(() => {
    if (!window.MediaRecorder) {
      setStatus("Tu navegador no soporta MediaRecorder API");
      return;
    }
    if (!MediaRecorder.isTypeSupported("video/mp4")) {
      setStatus("MP4 no soportado. Usando WebM como alternativa.");
      mimeTypeRef.current = "video/webm";
    }
  }, []);

  const captureFrame = () => {
    if (!isRecording) return;
    const ctx = canvasRef.current.getContext("2d");
    try {
      ctx.drawImage(videoRef.current, 0, 0, 640, 480);
      setFramesCaptured(prev => prev + 1);
    } catch (e) {
      setStatus(`Error capturando frame: ${e.message}`);
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    clearInterval(captureIntervalRef.current);
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
    }
    setStatus("Grabación detenida");
  };

  const uploadVideo = async (videoChunks) => {
    const blob = new Blob(videoChunks, { type: mimeTypeRef.current });
    const fileExtension = mimeTypeRef.current.includes("mp4") ? "mp4" : "webm";
    const fileName = `video_${Date.now()}.${fileExtension}`;

    if (blob.size === 0) {
      setStatus("El video está vacío");
      return;
    }

    const formData = new FormData();
    const file = new File([blob], fileName, { type: mimeTypeRef.current });
    formData.append("file", file, fileName);
    formData.append("descripcion", "Video generado desde IPCameraRecorder");
    formData.append("ubicacion", "Desconocida");

    try {
      const response = await fetch("http://localhost:8001/upload-video/", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      setStatus(`✅ Video subido: ${result.mensaje}`);
    } catch (err) {
      setStatus(`❌ Error al subir: ${err.message}`);
    }
  };

  const startRecording = () => {
    if (isRecording) return;

    setChunks([]);
    setFramesCaptured(0);
    setIsRecording(true);
    setStatus("Iniciando captura de frames...");

    captureIntervalRef.current = setInterval(captureFrame, 100);

    setTimeout(() => {
      if (framesCaptured === 0) {
        setStatus("No se capturaron frames. Verifique la cámara.");
        stopRecording();
        return;
      }

      const stream = canvasRef.current.captureStream(10);
      const recorder = new MediaRecorder(stream, {
        mimeType: mimeTypeRef.current,
      });

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) setChunks((prev) => [...prev, e.data]);
      };

      recorder.onstop = () => uploadVideo(chunks);
      recorder.onerror = (e) => {
        setStatus(`Error en grabación: ${e.error.name}`);
        stopRecording();
      };

      recorder.start(1000);
      setMediaRecorder(recorder);
      setStatus(`🎥 Grabando en formato: ${mimeTypeRef.current}`);

      setTimeout(() => {
        if (recorder && recorder.state === "recording") {
          recorder.stop();
        }
      }, 10000);
    }, 500);
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Cámara IP en Vivo</h1>
      <img
        ref={videoRef}
        src={ipCamUrl}
        alt="Cámara IP"
        width="640"
        height="480"
        crossOrigin="anonymous"
        className="rounded border"
      />
      <canvas ref={canvasRef} width="640" height="480" className="hidden" />

      <button
        onClick={startRecording}
        disabled={isRecording}
        className={`mt-4 px-6 py-2 text-white rounded ${
          isRecording ? "bg-gray-400" : "bg-green-600 hover:bg-green-700"
        }`}
      >
        {isRecording ? "🔴 Grabando..." : "Iniciar Grabación"}
      </button>

      <div className="mt-4 p-2 bg-gray-100 rounded text-sm text-gray-800">
        {status}
      </div>
    </div>
  );
}