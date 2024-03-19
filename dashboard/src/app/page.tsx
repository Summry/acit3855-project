"use client";

import ProcessorCard from "./components/client/ProcessorCard";
import AuditCard from "./components/client/AuditCard";
import Logo from "./components/client/Logo";

export default function Home() {
  return (
    <main className="h-screen flex flex-col items-center">
      <Logo />
      <section className="flex flex-col justify-center items-center mt-7">
        <h2>Latest Stats</h2>
        <ProcessorCard />
        <h2 className="pb-1">Audit Endpoints</h2>
        <AuditCard />
      </section>
    </main>
  );
}
