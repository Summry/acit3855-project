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

  const deliveryContent =
    auditStats?.delivery.item_quantity >= 1 ? (
      <div className="flex flex-col items-center p-4">
        <p className="font-bold">First Delivery Event</p>
        <p>{JSON.stringify(auditStats?.delivery)}</p>
      </div>
    ) : (
      <p>There is currently no Delivery Audit log</p>
    );

  const scheduleContent =
    auditStats?.schedule.number_of_deliveries >= 1 ? (
      <div className="flex flex-col items-center p-4">
        <p className="font-bold">First Schedule Event</p>
        <p>{JSON.stringify(auditStats?.schedule)}</p>
      </div>
    ) : (
      <p>There is currently no Schedule Audit log</p>
    );

  return (
    <section>
      {auditStats ? (
        <div>
          {deliveryContent}
          {scheduleContent}
        </div>
      ) : (
        <div className="space-y-2 pt-2">
          <Skeleton className="h-4 w-[350px]" />
          <Skeleton className="h-4 w-[350px]" />
          <Skeleton className="h-4 w-[275px]" />
        </div>
      )}
    </section>
  );
}
