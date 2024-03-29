"use client";

import { useState, useEffect } from "react";
import { IAuditStats } from "@/app/types/AuditStats";
import getAuditStats from "@/app/utils/getAuditStats";
import { Skeleton } from "@/components/ui/skeleton";

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

  const deliveryContent = auditStats?.delivery ? (
    <div className="flex flex-col items-center p-4">
      <p className="font-bold">Delivery Event - {auditStats.deliveryIndex}</p>
      <p>{JSON.stringify(auditStats.delivery)}</p>
    </div>
  ) : (
    <p>There is no Delivery Audit log at index {auditStats?.deliveryIndex}</p>
  );

  const scheduleContent = auditStats?.schedule ? (
    <div className="flex flex-col items-center p-4">
      <p className="font-bold">Schedule Event - {auditStats.scheduleIndex}</p>
      <p>{JSON.stringify(auditStats.schedule)}</p>
    </div>
  ) : (
    <p>There is no Schedule Audit log at index {auditStats?.scheduleIndex}</p>
  );

  return (
    <section>
      {auditStats ? (
        <div className="space-y-2 pt-2 flex flex-col items-center">
          {deliveryContent}
          {scheduleContent}
        </div>
      ) : (
        <div className="space-y-2 pt-2">
          <Skeleton className="h-4 w-[350px]" />
          <Skeleton className="h-4 w-[350px] delay-150" />
          <Skeleton className="h-4 w-[275px] delay-300" />
        </div>
      )}
    </section>
  );
}
