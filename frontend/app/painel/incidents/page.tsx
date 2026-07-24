"use client";

import { useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import {
  incidentsApi,
  incidentTypesApi,
  routesApi,
  ApiError,
  type Incident,
  type IncidentType,
  type NetworkRoute,
} from "../../../lib/api";
import { statusColor } from "../../../lib/incidentStatus";
import { formatDateTime } from "../../../lib/format";

const emptyForm = { type_id: "", route_id: "", cep: "", description: "" };

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [types, setTypes] = useState<IncidentType[]>([]);
  const [routes, setRoutes] = useState<NetworkRoute[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [isSaving, setIsSaving] = useState(false);

  async function loadAll() {
    setIsLoading(true);
    try {
      const [incidentsRes, typesRes, routesRes] = await Promise.all([
        incidentsApi.list(),
        incidentTypesApi.list(),
        routesApi.list(),
      ]);
      setIncidents(
        [...incidentsRes].sort(
          (a, b) =>
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
        ),
      );
      setTypes(typesRes.filter((t) => t.is_active));
      setRoutes(routesRes.filter((r) => r.is_active));
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Falha ao carregar incidentes.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadAll();
  }, []);

  function startCreate() {
    setForm(emptyForm);
    setIsFormOpen(true);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSaving(true);
    try {
      await incidentsApi.create({
        type_id: Number(form.type_id),
        route_id: Number(form.route_id),
        cep: form.cep,
        description: form.description,
      });
      setIsFormOpen(false);
      await loadAll();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Falha ao criar incidente.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="font-display text-xl font-semibold text-white">
          Incidentes
        </h1>
        <button
          onClick={startCreate}
          className="rounded-md bg-blue-mid px-4 py-2 font-display text-sm font-medium text-white hover:bg-blue"
        >
          + Novo incidente
        </button>
      </div>

      {error && <p className="mt-4 text-sm text-red-400">{error}</p>}

      {isFormOpen && (
        <form
          onSubmit={handleSubmit}
          className="mt-6 flex flex-col gap-4 border-t border-navy-light pt-6"
        >
          <div className="flex flex-col gap-1.5">
            <label className="text-xs text-mid-gray">Tipo</label>
            <select
              required
              value={form.type_id}
              onChange={(e) => setForm({ ...form, type_id: e.target.value })}
              className="rounded-md border border-navy-light bg-navy-light px-3 py-2 text-sm text-white outline-none focus:border-cyan"
            >
              <option value="">Selecione...</option>
              {types.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-xs text-mid-gray">Rota</label>
            <select
              required
              value={form.route_id}
              onChange={(e) => setForm({ ...form, route_id: e.target.value })}
              className="rounded-md border border-navy-light bg-navy-light px-3 py-2 text-sm text-white outline-none focus:border-cyan"
            >
              <option value="">Selecione...</option>
              {routes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-xs text-mid-gray">CEP</label>
            <input
              required
              maxLength={9}
              placeholder="00000-000"
              value={form.cep}
              onChange={(e) => setForm({ ...form, cep: e.target.value })}
              className="rounded-md border border-navy-light bg-navy-light px-3 py-2 text-sm text-white outline-none focus:border-cyan"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-xs text-mid-gray">Descrição</label>
            <textarea
              required
              rows={3}
              value={form.description}
              onChange={(e) =>
                setForm({ ...form, description: e.target.value })
              }
              className="rounded-md border border-navy-light bg-navy-light px-3 py-2 text-sm text-white outline-none focus:border-cyan"
            />
          </div>
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={isSaving}
              className="rounded-md bg-blue-mid px-4 py-2 font-display text-sm font-medium text-white hover:bg-blue disabled:opacity-50"
            >
              {isSaving ? "Salvando..." : "Salvar"}
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
              <th className="py-2 font-normal">Status</th>
              <th className="py-2 font-normal">Tipo</th>
              <th className="py-2 font-normal">Rota</th>
              <th className="py-2 font-normal">Aberto em</th>
              <th className="py-2 font-normal" />
            </tr>
          </thead>
          <tbody>
            {incidents.map((incident) => (
              <tr key={incident.id} className="border-b border-navy-light">
                <td className="py-3">
                  <span className="flex items-center gap-2">
                    <span
                      className={`h-2 w-2 rounded-full ${statusColor(incident.status_name, incident.status_is_final)}`}
                    />
                    {incident.status_name}
                  </span>
                </td>
                <td className="py-3 text-light-gray">{incident.type_name}</td>
                <td className="py-3 text-light-gray">{incident.route_name}</td>
                <td className="py-3 text-light-gray">
                  {formatDateTime(incident.created_at)}
                </td>
                <td className="py-3 text-right">
                  <Link
                    href={`/painel/incidents/${incident.id}`}
                    className="text-light-gray hover:text-cyan"
                  >
                    Ver
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
