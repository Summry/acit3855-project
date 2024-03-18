"use client";

import { useState, useEffect } from "react";
import { IAuditStats } from "@/app/types/AuditStats";
import getAuditStats from "@/app/utils/getAuditStats";

export default function AuditCard() {
  const [auditStats, setAuditStats] = useState<IAuditStats>();

  useEffect(() => {
    const fetchAuditStats = async () => {
      const auditStatsResponse = await getAuditStats();
      setAuditStats(auditStatsResponse);
    };

    const timeout = setTimeout(fetchAuditStats, 4000);

    return () => clearTimeout(timeout);
  }, [auditStats]);

  return (
    <section>
      {auditStats ? (
        <div>
          <div className="flex flex-col items-center p-4">
            <p className="font-bold">First Delivery Event</p>
            <p>{JSON.stringify(auditStats.delivery)}</p>
          </div>
          <div className="flex flex-col items-center p-4">
            <p className="font-bold">First Schedule Event</p>
            <p>{JSON.stringify(auditStats.schedule)}</p>
          </div>
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </section>
  );
}
