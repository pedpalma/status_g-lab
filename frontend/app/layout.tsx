import type { Metadata } from "next";
import "./globals.css";
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
