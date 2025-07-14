import React, { useEffect, useRef, useState } from "react";

const IPCameraRecorder = () => {
  const imgRef = useRef(null);
  const canvasRef = useRef(null);
  const [status, setStatus] = useState("Cámara activa");
  const [recording, setRecording] = useState(false);

  const ipCamUrl = "http://192.168.100.204:8080/video";

  useEffect(() => {
    if (imgRef.current) {
      imgRef.current.src = ipCamUrl;
    }
  }, []);

  const logStatus = (msg) => {
    setStatus(msg);
    console.log("[STATUS]", msg);
  };

  const startRecording = async () => {
    if (recording) return;
    setRecording(true);
    logStatus("Iniciando grabación...");

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const chunks = [];
    const stream = canvas.captureStream(10);
    const mimeType = MediaRecorder.isTypeSupported("video/mp4")
      ? "video/mp4"
      : "video/webm";

    const recorder = new MediaRecorder(stream, { mimeType });

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };

    recorder.onstop = async () => {
      const blob = new Blob(chunks, { type: mimeType });
      const fileName = `video_${Date.now()}.${mimeType.includes("mp4") ? "mp4" : "webm"}`;

      const file = new File([blob], fileName, { type: mimeType });
      const formData = new FormData();
      formData.append("file", file);
      formData.append("descripcion", "Grabación desde React");
      formData.append("ubicacion", "Interfaz Web");

      try {
        const res = await fetch("http://localhost:8001/upload-video/", {
          method: "POST",
          body: formData,
        });

        const result = await res.json();
        logStatus(`✅ Subido: ${result.url_video}`);
      } catch (err) {
        logStatus("❌ Error al subir: " + err.message);
      }

      setRecording(false);
    };

    const interval = setInterval(() => {
      try {
        ctx.drawImage(imgRef.current, 0, 0, 640, 480);
      } catch (e) {}
    }, 100);

    recorder.start();
    setTimeout(() => {
      recorder.stop();
      clearInterval(interval);
    }, 10000);
  };

  return (
    <div className="p-4 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Cámara IP en Vivo</h1>
      <img
        ref={imgRef}
        className="border mb-4 w-[640px] h-[480px]"
        alt="IP Camera"
        crossOrigin="anonymous"
      />
      <canvas ref={canvasRef} width="640" height="480" hidden></canvas>
      <button
        onClick={startRecording}
        disabled={recording}
        className={`px-4 py-2 text-white rounded ${
          recording ? "bg-red-500" : "bg-green-600"
        }`}
      >
        {recording ? "🔴 Grabando..." : "Iniciar Grabación"}
      </button>
      <div className="mt-3 text-sm text-gray-800">{status}</div>
    </div>
  );
};

export default IPCameraRecorder;
