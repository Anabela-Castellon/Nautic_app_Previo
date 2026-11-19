import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AdminLayout from "../components/AdminLayout";
import { listSports, toggleSportStatus, uploadSportIcon, deleteSport, SportInfo } from "../api/admin";

export default function SportsManagementPage() {
  const [sports, setSports] = useState<SportInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const [iconTick, setIconTick] = useState(0); // fuerza a recargar los iconos tras guardar
  const apiBase = import.meta.env.VITE_API_URL || "http://localhost:8000";

  // Iconos elegidos que todavia no se guardaron: id del deporte -> archivo + vista previa
  const [pendingIcons, setPendingIcons] = useState<Record<number, { file: File; preview: string }>>({});
  const [saving, setSaving] = useState(false);
  const pendingCount = Object.keys(pendingIcons).length;

  const handleIcon = (id: number, file?: File | null) => {
    if (!file) return;
    setPendingIcons((prev) => {
      if (prev[id]) URL.revokeObjectURL(prev[id].preview);
      return { ...prev, [id]: { file, preview: URL.createObjectURL(file) } };
    });
  };

  const discardChanges = () => {
    Object.values(pendingIcons).forEach((p) => URL.revokeObjectURL(p.preview));
    setPendingIcons({});
  };

  const saveChanges = async () => {
    setSaving(true);
    const failed: string[] = [];
    const remaining: Record<number, { file: File; preview: string }> = {};
    for (const [idStr, pending] of Object.entries(pendingIcons)) {
      const id = Number(idStr);
      try {
        await uploadSportIcon(id, pending.file);
        URL.revokeObjectURL(pending.preview);
      } catch (err) {
        remaining[id] = pending; // queda pendiente para reintentar
        failed.push(`${sports.find((s) => s.id === id)?.nombre ?? id}: ${(err as Error).message}`);
      }
    }
    setPendingIcons(remaining);
    setIconTick((t) => t + 1);
    setSaving(false);
    alert(failed.length ? "No se pudieron guardar algunos íconos:\n" + failed.join("\n") : "¡Cambios guardados!");
  };

  const fetchSports = async () => {
    setLoading(true);
    try {
      const data = await listSports();
      setSports(data);
    } catch (err) {
      console.error("Error al cargar deportes:", err);
      alert("No se pudieron cargar los deportes.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSports();
  }, []);

  const handleToggle = async (id: number) => {
    if (
      !confirm("¿Estás seguro de que quieres cambiar el estado de este deporte?")
    ) {
      return;
    }
    try {
      await toggleSportStatus(id);
      // Recarga la lista para mostrar el nuevo estado
      fetchSports();
    } catch (err) {
      alert("No se pudo actualizar el estado.");
    }
  };

  const handleDelete = async (sport: SportInfo) => {
    if (
      !confirm(
        `¿Eliminar el deporte "${sport.nombre}"?\n\nSe borrarán también sus condiciones de pronóstico, sus puntajes y su ícono. Esta acción no se puede deshacer.`
      )
    ) {
      return;
    }
    try {
      await deleteSport(sport.id);
      // Si tenía un ícono elegido sin guardar, se descarta
      setPendingIcons((prev) => {
        if (!prev[sport.id]) return prev;
        URL.revokeObjectURL(prev[sport.id].preview);
        const rest = { ...prev };
        delete rest[sport.id];
        return rest;
      });
      fetchSports();
    } catch (err) {
      alert("No se pudo eliminar el deporte.");
    }
  };

  return (
    <AdminLayout>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-[#0b2849] mb-2">
            Gestionar Deportes
          </h2>
          <p className="text-gray-500">
            Activa, desactiva o crea nuevos deportes en la plataforma.
          </p>
        </div>
        <button
          onClick={() => navigate("/admin/crear-deporte")}
          className="bg-[#0b2849] text-white font-semibold px-5 py-2 rounded-md hover:bg-[#143b6b] transition"
        >
          Crear Nuevo Deporte
        </button>
      </div>

      {/* === Tabla de Deportes === */}
      <div className="bg-white rounded-xl shadow border border-gray-200">
        <table className="w-full table-auto">
          <thead className="border-b border-gray-200">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">
                Nombre del Deporte
              </th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">
                Ícono
              </th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">
                Estado
              </th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={4} className="px-6 py-10 text-center text-gray-500">
                  Cargando...
                </td>
              </tr>
            )}
            {!loading && sports.length === 0 && (
              <tr>
                <td colSpan={4} className="px-6 py-10 text-center text-gray-500">
                  No se encontraron deportes.
                </td>
              </tr>
            )}
            {sports.map((sport) => (
              <tr key={sport.id} className="border-b border-gray-100">
                <td className="px-6 py-4 font-medium text-[#0b2849]">
                  {sport.nombre}
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    {pendingIcons[sport.id] ? (
                      <img
                        src={pendingIcons[sport.id].preview}
                        alt="Vista previa"
                        className="w-8 h-8 object-contain"
                      />
                    ) : (
                      <img
                        src={`${apiBase}/deporte/icono/${sport.id}?t=${iconTick}`}
                        alt=""
                        className="w-8 h-8 object-contain"
                        onError={(e) => ((e.currentTarget as HTMLImageElement).style.display = "none")}
                        onLoad={(e) => ((e.currentTarget as HTMLImageElement).style.display = "block")}
                      />
                    )}
                    <label className="cursor-pointer text-sm text-[#0b2849] underline">
                      Cambiar
                      {pendingIcons[sport.id] && (
                        <span className="ml-2 no-underline text-xs text-amber-600 font-medium">
                          sin guardar
                        </span>
                      )}
                      <input
                        type="file"
                        accept="image/png"
                        className="hidden"
                        onChange={(e) => {
                          handleIcon(sport.id, e.target.files?.[0]);
                          e.target.value = "";
                        }}
                      />
                    </label>
                  </div>
                </td>
                <td className="px-6 py-4">
                  {sport.activo ? (
                    <span className="px-3 py-1 rounded-full bg-green-100 text-green-700 text-xs font-medium">
                      Activo
                    </span>
                  ) : (
                    <span className="px-3 py-1 rounded-full bg-gray-100 text-gray-600 text-xs font-medium">
                      Inactivo
                    </span>
                  )}
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleToggle(sport.id)}
                      className="bg-gray-100 text-gray-700 font-semibold px-4 py-2 rounded-md hover:bg-gray-200 transition text-sm"
                    >
                      {sport.activo ? "Desactivar" : "Activar"}
                    </button>
                    <button
                      onClick={() => handleDelete(sport)}
                      className="bg-red-50 text-red-700 font-semibold px-4 py-2 rounded-md hover:bg-red-100 transition text-sm"
                    >
                      Eliminar
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* === Guardar cambios (iconos) === */}
      <div className="mt-6 flex items-center justify-end gap-3">
        {pendingCount > 0 && (
          <span className="text-sm text-amber-600 mr-auto">
            Tenés {pendingCount} {pendingCount === 1 ? "cambio" : "cambios"} sin guardar.
          </span>
        )}
        <button
          onClick={discardChanges}
          disabled={pendingCount === 0 || saving}
          className="bg-gray-100 text-gray-700 font-semibold px-5 py-2 rounded-md hover:bg-gray-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Descartar
        </button>
        <button
          onClick={saveChanges}
          disabled={pendingCount === 0 || saving}
          className="bg-[#0b2849] text-white font-semibold px-5 py-2 rounded-md hover:bg-[#143b6b] transition disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {saving ? "Guardando..." : "Guardar cambios"}
        </button>
      </div>
    </AdminLayout>
  );
}