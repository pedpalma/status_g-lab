"use client";

import Link from "next/link";
import { useAuth } from "./AuthProvider";

const links = [
  { href: "/painel/incidents", label: "Incidentes" },
  { href: "/painel/users", label: "Usuários" },
  { href: "/painel/routes", label: "Rotas" },
  { href: "/painel/incident-types", label: "Tipos de incidente" },
];

export default function PrivateTopbar() {
  const { role, logout } = useAuth();

  return (
    <header
      className="flex items-center justify-between border-b border-navy-light bg-navy px-6"
      style={{ height: "var(--header-h)" }}
    >
      <div className="flex items-center gap-8">
        <Link
          href="/painel"
          className="font-display text-sm font-semibold text-white"
        >
          G-Lab Telecom
        </Link>
        <nav className="flex items-center gap-6">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm text-light-gray transition-colors duration-(--dur) hover:text-cyan"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>

      <div className="flex items-center gap-4">
        {role && <span className="text-xs text-mid-gray">{role}</span>}
        <button
          onClick={logout}
          className="text-sm text-mid-gray transition-colors duration-(--dur) hover:text-cyan"
        >
          Sair
        </button>
      </div>
    </header>
  );
}
