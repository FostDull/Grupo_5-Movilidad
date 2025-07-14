import { useEffect, useRef, useState } from "react";

const App = () => {
  const imgRef = useRef(null);
  const canvasRef = useRef(null);
  const [status, setStatus] = useState("Cámara activa");
  const [recording, setRecording] = useState(false);

  useEffect(() => {
    if (imgRef.current) {
      imgRef.current.src = "http://192.168.100.204:8080/video";
    }
  }, []);

  const startRecording = async () => {
    setStatus("Iniciando grabación...");
    setRecording(true);
    // Aquí puedes poner el código de grabación usando `canvasRef.current`, etc.
  };

  return (
    <div style={{ fontFamily: "Arial", padding: 20 }}>
      <h1>Cámara IP en Vivo</h1>
      <img ref={imgRef} width="640" height="480" alt="Cámara IP" crossOrigin="anonymous" />
      <br />
      <button
        onClick={startRecording}
        disabled={recording}
        style={{
          padding: "12px 24px",
          background: recording ? "#f44336" : "#4CAF50",
          color: "white",
          fontSize: 18,
          border: "none",
          borderRadius: 4,
          cursor: "pointer"
        }}
      >
        {recording ? "🔴 Grabando..." : "Iniciar Grabación"}
      </button>
      <div style={{ marginTop: 10, background: "#f0f0f0", padding: 10 }}>{status}</div>
      <canvas ref={canvasRef} width="640" height="480" style={{ display: "none" }}></canvas>
    </div>
  );
};

export default App;
