import Link from "next/link";

const sections = [
  {
    href: "/painel/users",
    label: "Usuários",
    description: "Gerenciar contas de técnicos e administradores.",
  },
  {
    href: "/painel/routes",
    label: "Rotas",
    description: "Cadastro de rotas da rede.",
  },
  {
    href: "/painel/incident-types",
    label: "Tipos de incidente",
    description: "Categorias usadas no registro de incidentes.",
  },
];

export default function PainelHome() {
  return (
    <div>
      <h1 className="font-display text-xl font-semibold text-white">
        Painel administrativo
      </h1>
      <ul className="mt-6 divide-y divide-navy-light border-t border-b border-navy-light">
        {sections.map((s) => (
          <li key={s.href}>
            <Link
              href={s.href}
              className="flex items-center justify-between py-4 text-off-white transition-colors duration-[var(--dur)] hover:text-cyan"
            >
              <div>
                <p className="font-display text-sm font-medium">{s.label}</p>
                <p className="text-sm text-mid-gray">{s.description}</p>
              </div>
              <span aria-hidden>{"->"}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
