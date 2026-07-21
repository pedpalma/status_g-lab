"use client";

import { useEffect, useState, type FormEvent } from "react";
import { usersApi, ApiError, type User, type Role } from "../../../lib/api";

const emptyForm = {
  name: "",
  email: "",
  password: "",
  role: "tecnico" as Role,
};

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);

  async function loadUsers() {
    setIsLoading(true);
    try {
      setUsers(await usersApi.list());
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Falha ao carregar usuários.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    // Carga inicial da lista ao montar a tela. Padrão necessário sem uma
    // lib de data-fetching (React Query/SWR) -- fora de escopo aqui pela
    // simplicidade do projeto.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadUsers();
  }, []);

  function startCreate() {
    setEditingId(null);
    setForm(emptyForm);
    setIsFormOpen(true);
  }

  function startEdit(user: User) {
    setEditingId(user.id);
    setForm({
      name: user.name,
      email: user.email,
      password: "",
      role: user.role,
    });
    setIsFormOpen(true);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      if (editingId) {
        await usersApi.update(editingId, {
          name: form.name,
          email: form.email,
          role: form.role,
        });
      } else {
        await usersApi.create(form);
      }
      setIsFormOpen(false);
      await loadUsers();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Falha ao salvar usuário.",
      );
    }
  }

  async function toggleActive(user: User) {
    setError(null);
    try {
      if (user.is_active) {
        await usersApi.deactivate(user.id);
      } else {
        await usersApi.update(user.id, { is_active: true });
      }
      await loadUsers();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Falha ao atualizar usuário.",
      );
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="font-display text-xl font-semibold text-white">
          Usuários
        </h1>
        <button
          onClick={startCreate}
          className="rounded-md bg-blue-mid px-4 py-2 font-display text-sm font-medium text-white hover:bg-blue"
        >
          + Novo usuário
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
            <label className="text-xs text-mid-gray">E-mail</label>
            <input
              type="email"
              required
              maxLength={255}
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="rounded-md border border-navy-light bg-navy-light px-3 py-2 text-sm text-white outline-none focus:border-cyan"
            />
          </div>
          {!editingId && (
            <div className="flex flex-col gap-1.5">
              <label className="text-xs text-mid-gray">Senha</label>
              <input
                type="password"
                required
                minLength={8}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="rounded-md border border-navy-light bg-navy-light px-3 py-2 text-sm text-white outline-none focus:border-cyan"
              />
            </div>
          )}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs text-mid-gray">Papel</label>
            <select
              value={form.role}
              onChange={(e) =>
                setForm({ ...form, role: e.target.value as Role })
              }
              className="rounded-md border border-navy-light bg-navy-light px-3 py-2 text-sm text-white outline-none focus:border-cyan"
            >
              <option value="tecnico">Técnico</option>
              <option value="admin">Admin</option>
            </select>
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
              <th className="py-2 font-normal">E-mail</th>
              <th className="py-2 font-normal">Papel</th>
              <th className="py-2 font-normal">Status</th>
              <th className="py-2 font-normal" />
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-b border-navy-light">
                <td className="py-3">{user.name}</td>
                <td className="py-3 text-light-gray">{user.email}</td>
                <td className="py-3 capitalize">{user.role}</td>
                <td className="py-3">
                  <span
                    className={
                      user.is_active ? "text-success" : "text-mid-gray"
                    }
                  >
                    {user.is_active ? "Ativo" : "Inativo"}
                  </span>
                </td>
                <td className="py-3 text-right">
                  <button
                    onClick={() => startEdit(user)}
                    className="mr-4 text-light-gray hover:text-cyan"
                  >
                    Editar
                  </button>
                  <button
                    onClick={() => toggleActive(user)}
                    className="text-light-gray hover:text-cyan"
                  >
                    {user.is_active ? "Desativar" : "Ativar"}
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
