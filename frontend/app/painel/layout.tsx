"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../components/private/AuthProvider";
import PrivateTopbar from "../../components/private/PrivateTopbar";

export default function PainelLayout({ children }: { children: React.ReactNode }) {
  const { token, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !token) {
      router.replace("/login");
    }
  }, [isLoading, token, router]);

  if (isLoading || !token) {
    return (
      <div className="flex flex-1 items-center justify-center py-24 text-sm text-mid-gray">
        Carregando...
      </div>
    );
  }

  return (
    <>
      <PrivateTopbar />
      <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-10">{children}</main>
    </>
  );
}
