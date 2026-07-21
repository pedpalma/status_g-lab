import type { Metadata } from "next";
import "./globals.css";
// Import via JS/TS (não via @import no CSS): é o padrão suportado pelo
// Fontsource + Next.js. O @import direto de node_modules dentro do CSS
// não resolve nesse pipeline (Turbopack + @tailwindcss/postcss) e quebrava
// o build.
import { AuthProvider } from "../components/private/AuthProvider";

export const metadata: Metadata = {
  title: "Status G-Lab Telecom",
  description: "Plataforma de consulta publica de incidentes da rede.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="h-full antialiased">
      <body className="min-h-full flex flex-col font-sans">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
