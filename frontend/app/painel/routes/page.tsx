"use client";

import { useEffect, useState, type FormEvent } from "react";
import { routesApi, ApiError, type NetworkRoute } from "../../../lib/api";

const emptyForm = { name: "", description: "" };

export default function RoutesPage() {
  const [routes, setRoutes] = useState<NetworkRoute[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);

  async function loadRoutes() {
    setIsLoading(true);
    try {
      setRoutes(await routesApi.list());
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Falha ao carregar rotas.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadRoutes();
  }, []);

  function startCreate() {
    setEditingId(null);
    setForm(emptyForm);
    setIsFormOpen(true);
  }

  function startEdit(route: NetworkRoute) {
    setEditingId(route.id);
    setForm({ name: route.name, description: route.description ?? "" });
    setIsFormOpen(true);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      if (editingId) {
        await routesApi.update(editingId, form);
      } else {
        await routesApi.create(form);
      }
      setIsFormOpen(false);
      await loadRoutes();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Falha ao salvar rota.");
    }
  }

  async function toggleActive(route: NetworkRoute) {
    setError(null);
    try {
      if (route.is_active) {
        await routesApi.deactivate(route.id);
      } else {
        await routesApi.update(route.id, { is_active: true });
      }
      await loadRoutes();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Falha ao atualizar rota.",
      );
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="font-display text-xl font-semibold text-white">Rotas</h1>
        <button
          onClick={startCreate}
          className="rounded-md bg-blue-mid px-4 py-2 font-display text-sm font-medium text-white hover:bg-blue"
        >
          + Nova rota
        </button>
      </div>

      {error && <p className="mt-4 text-sm text-red-400">{error}</p>}

      {isFormOpen && (
        <form
          onSubmit={handleSubmit}
          className="mt-6 flex flex-col gap-4 border-t border-navy-light pt-6"
        >
          <div className="flex flex-col gap-1.5">
            <label className="text-xs text-mid-gray">Nome</label>
            <input
              required
              maxLength={150}
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="rounded-md border border-navy-light bg-navy-light px-3 py-2 text-sm text-white outline-none focus:border-cyan"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-xs text-mid-gray">Descrição</label>
            <textarea
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
              <th className="py-2 font-normal">Descrição</th>
              <th className="py-2 font-normal">Status</th>
              <th className="py-2 font-normal" />
            </tr>
          </thead>
          <tbody>
            {routes.map((route) => (
              <tr key={route.id} className="border-b border-navy-light">
                <td className="py-3">{route.name}</td>
                <td className="py-3 text-light-gray">
                  {route.description || "Sem descrição"}
                </td>
                <td className="py-3">
                  <span
                    className={
                      route.is_active ? "text-success" : "text-mid-gray"
                    }
                  >
                    {route.is_active ? "Ativa" : "Inativa"}
                  </span>
                </td>
                <td className="py-3 text-right">
                  <button
                    onClick={() => startEdit(route)}
                    className="mr-4 text-light-gray hover:text-cyan"
                  >
                    Editar
                  </button>
                  <button
                    onClick={() => toggleActive(route)}
                    className="text-light-gray hover:text-cyan"
                  >
                    {route.is_active ? "Desativar" : "Ativar"}
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
