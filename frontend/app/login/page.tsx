"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../components/private/AuthProvider";
import { ApiError } from "../../lib/api";

export default function LoginPage() {
  const { login, token } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (token) router.replace("/painel");
  }, [token, router]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login(email, password);
      router.push("/painel");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Erro ao conectar com o servidor.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="flex flex-1 items-center justify-center px-6 py-24">
      <div className="w-full max-w-sm">
        <h1 className="font-display text-2xl font-semibold text-white">
          Área técnica
        </h1>
        <p className="mt-1 text-sm text-mid-gray">
          Acesso restrito para técnicos e administradores.
        </p>

        <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="email" className="text-xs text-mid-gray">
              E-mail
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="rounded-md border border-navy-light bg-navy-light px-3 py-2 text-sm text-white outline-none focus:border-cyan"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="password" className="text-xs text-mid-gray">
              Senha
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="rounded-md border border-navy-light bg-navy-light px-3 py-2 text-sm text-white outline-none focus:border-cyan"
            />
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            type="submit"
            disabled={isSubmitting}
            className="mt-2 rounded-md bg-blue-mid py-2 font-display text-sm font-medium text-white transition-colors duration-(--dur) hover:bg-blue disabled:opacity-50"
          >
            {isSubmitting ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </div>
    </main>
  );
}
