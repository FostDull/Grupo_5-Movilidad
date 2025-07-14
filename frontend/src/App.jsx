import React from "react";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navbar */}
      <nav className="bg-purple-700 text-white flex items-center px-6 py-3">
        <img src="/public/kuntur_logo.png" alt="Logo" className="h-10 mr-3" />
        <span className="font-bold text-xl">KUNTUR MOBILITY</span>
        <div className="ml-auto space-x-6">
          <a href="#" className="hover:underline">Monitoreo</a>
          <a href="#" className="hover:underline">Alertas</a>
        </div>
      </nav>

      {/* Contenido principal */}
      <main className="max-w-7xl mx-auto p-6 grid md:grid-cols-3 gap-6">
        {/* Video / Streaming */}
        <section className="md:col-span-2 bg-white rounded shadow p-4">
          <h2 className="text-lg font-semibold mb-4">Video en Vivo</h2>
          {/* Si tienes un stream puedes usar <video> en lugar de <img> */}
          <img
            src="http://192.168.100.204:8080/video"
            alt="Video en vivo"
            className="w-full rounded"
            crossOrigin="anonymous"
          />
        </section>

        {/* Métricas y estado */}
        <section className="space-y-6">
          <div className="bg-white rounded shadow p-4">
            <h3 className="font-semibold mb-4">Métricas de Detección</h3>
            <div className="grid gap-4">
              <div className="bg-gray-100 rounded p-4 text-center">
                <p className="text-gray-600">Amenazas</p>
                <p className="text-3xl font-bold text-purple-700">0</p>
              </div>
              <div className="bg-gray-100 rounded p-4 text-center">
                <p className="text-gray-600">Armas</p>
                <p className="text-3xl font-bold text-purple-700">0</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded shadow p-4">
            <h3 className="font-semibold mb-4">Estado del Sistema</h3>
            <p>El sistema está operando normalmente.</p>
          </div>
        </section>
      </main>
    </div>
  );
}
