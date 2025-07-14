import React from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

export default function App() {
  const transportInfo = {
    unidad: "009",
    placa: "PCA-123",
    conductor: "Juan Chores",
    ruta: "Terminal Sur - Av. Colón",
    horario: "06:00 - 22:00",
  };

  const currentLocation = [-0.180653, -78.467834];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navbar */}
      <nav className="bg-purple-700 text-white flex items-center px-6 py-3">
        <img src="/kuntur_logo.png" alt="Kuntur - Movilidad" className="h-8 mr-3" />
        <span className="font-bold text-xl">Kuntur - Movilidad</span>
      </nav>

      {/* Layout: cámara a la izquierda, datos a la derecha */}
      <main className="max-w-7xl mx-auto p-6 flex flex-col md:flex-row gap-6">
        {/* Cámara */}
        <section className="bg-white rounded shadow p-4 w-full md:w-1/2">
          <h2 className="text-lg font-semibold mb-4">Cámara de Seguridad</h2>
          <div className="w-full h-64 overflow-hidden rounded-lg">
            <img
              src="http://192.168.100.204:8080/video"
              alt="Video en vivo"
              className="w-full h-64 object-cover rounded-lg block mx-0"
              crossOrigin="anonymous"
            />

          </div>
          <button className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded mt-4">
            Detener Grabación
          </button>
          <div className="mt-2 text-sm text-gray-600">
            <input type="checkbox" className="mr-1" />
            <span>Segmento subido: Video guardado (2407.9 KB en 0.01s)</span>
          </div>
        </section>

        {/* Info + Mapa */}
        <section className="flex flex-col gap-6 w-full md:w-1/2">
          <div className="bg-white rounded shadow p-4">
            <h3 className="text-lg font-semibold mb-4">Información del Transporte</h3>
            <div className="space-y-1">
              <p><strong>Unidad:</strong> {transportInfo.unidad}</p>
              <p><strong>Placa:</strong> {transportInfo.placa}</p>
              <p><strong>Conductor:</strong> {transportInfo.conductor}</p>
              <p><strong>Ruta:</strong> {transportInfo.ruta}</p>
              <p><strong>Horario:</strong> {transportInfo.horario}</p>
            </div>
          </div>

          <div className="bg-white rounded shadow p-4 flex-grow">
            <h3 className="text-lg font-semibold mb-4">Ubicación en Tiempo Real</h3>
            <div className="h-64 rounded overflow-hidden">
              <MapContainer center={currentLocation} zoom={13} style={{ height: "100%", width: "100%" }}>
                <TileLayer
                  attribution='&copy; OpenStreetMap contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <Marker position={currentLocation}>
                  <Popup>Ubicación actual</Popup>
                </Marker>
              </MapContainer>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
