"use client";

import { useEffect, useState, type FormEvent } from "react";
import { incidentTypesApi, ApiError, type IncidentType } from "../../../lib/api";

export default function IncidentTypesPage() {
  const [types, setTypes] = useState<IncidentType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [name, setName] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);

  async function loadTypes() {
    setIsLoading(true);
    try {
      setTypes(await incidentTypesApi.list());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Falha ao carregar tipos.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadTypes();
  }, []);

  function startCreate() {
    setEditingId(null);
    setName("");
    setIsFormOpen(true);
  }

  function startEdit(type: IncidentType) {
    setEditingId(type.id);
    setName(type.name);
    setIsFormOpen(true);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      if (editingId) {
        await incidentTypesApi.update(editingId, { name });
      } else {
        await incidentTypesApi.create({ name });
      }
      setIsFormOpen(false);
      await loadTypes();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Falha ao salvar tipo.");
    }
  }

  async function toggleActive(type: IncidentType) {
    setError(null);
    try {
      if (type.is_active) {
        await incidentTypesApi.deactivate(type.id);
      } else {
        await incidentTypesApi.update(type.id, { is_active: true });
      }
      await loadTypes();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Falha ao atualizar tipo.");
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="font-display text-xl font-semibold text-white">Tipos de incidente</h1>
        <button
          onClick={startCreate}
          className="rounded-md bg-blue-mid px-4 py-2 font-display text-sm font-medium text-white hover:bg-blue"
        >
          + Novo tipo
        </button>
      </div>

      {error && <p className="mt-4 text-sm text-red-400">{error}</p>}

      {isFormOpen && (
        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4 border-t border-navy-light pt-6">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs text-mid-gray">Nome</label>
            <input
              required
              maxLength={100}
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="rounded-md border border-navy-light bg-navy-light px-3 py-2 text-sm text-white outline-none focus:border-cyan"
            />
          </div>
          <div className="flex gap-3">
            <button
              type="submit"
              className="rounded-md bg-blue-mid px-4 py-2 font-display text-sm font-medium text-white hover:bg-blue"
            >
              Salvar
            </button>
            <button
              type="button"
              onClick={() => setIsFormOpen(false)}
              className="px-4 py-2 text-sm text-mid-gray hover:text-off-white"
            >
              Cancelar
            </button>
          </div>
        </form>
      )}

      {isLoading ? (
        <p className="mt-6 text-sm text-mid-gray">Carregando...</p>
      ) : (
        <table className="mt-6 w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-navy-light text-left text-xs text-mid-gray">
              <th className="py-2 font-normal">Nome</th>
              <th className="py-2 font-normal">Status</th>
              <th className="py-2 font-normal" />
            </tr>
          </thead>
          <tbody>
            {types.map((type) => (
              <tr key={type.id} className="border-b border-navy-light">
                <td className="py-3 capitalize">{type.name.replace(/_/g, " ")}</td>
                <td className="py-3">
                  <span className={type.is_active ? "text-success" : "text-mid-gray"}>
                    {type.is_active ? "Ativo" : "Inativo"}
                  </span>
                </td>
                <td className="py-3 text-right">
                  <button onClick={() => startEdit(type)} className="mr-4 text-light-gray hover:text-cyan">
                    Editar
                  </button>
                  <button onClick={() => toggleActive(type)} className="text-light-gray hover:text-cyan">
                    {type.is_active ? "Desativar" : "Ativar"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
