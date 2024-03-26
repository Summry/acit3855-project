"use client";

import { IProcessorStats } from "@/app/types/ProcessorStats";
import getProcessorStats from "@/app/utils/getProcessorStats";
import { useEffect, useState } from "react";
import { Skeleton } from "@/components/ui/skeleton";

export default function ProcessorCard() {
  const [processorStats, setProcessorStats] = useState<IProcessorStats>();
  const [lastUpdated, setLastUpdated] = useState<string>("");

  useEffect(() => {
    const fetchData = async () => {
      const processorStats = await getProcessorStats();
      setProcessorStats(processorStats);
      setLastUpdated(new Date().toLocaleString());
    };

    const timeout = setTimeout(fetchData, 4000);

    return () => clearTimeout(timeout);
  }, [processorStats]);

  const deliveriesContent = processorStats ? (
    <div className="space-y-2 pt-2">
      <p>Total deliveries: {processorStats.num_of_deliveries}</p>
      <p>Total delivery items: {processorStats.total_delivery_items}</p>
    </div>
  ) : (
    <div className="space-y-2 pt-2">
      <Skeleton className="h-4 w-[200px] delay-150" />
      <Skeleton className="h-4 w-[150px]" />
    </div>
  );

  const schedulesContent = processorStats ? (
    <div className="space-y-2 pt-2">
      <p>Total schedules: {processorStats.num_of_schedules}</p>
      <p>
        Total scheduled deliveries: {processorStats.total_scheduled_deliveries}
      </p>
    </div>
  ) : (
    <div className="space-y-2 pt-2">
      <Skeleton className="h-4 w-[200px] delay-75" />
      <Skeleton className="h-4 w-[150px] delay-200" />
    </div>
  );

  return (
    <div className="flex flex-col justify-center items-center">
      <div className="flex justify-between items-center">
        <div className="flex flex-col p-4">
          <h3>Deliveries</h3>
          {deliveriesContent}
        </div>
        <div className="flex flex-col p-4">
          <h3>Schedules</h3>
          {schedulesContent}
        </div>
      </div>

      {lastUpdated ? (
        <p className="font-bold pb-2">Last Updated: {lastUpdated}</p>
      ) : (
        <div className="font-bold pb-2 flex justify-center w-[100%] items-center">
          Last Updated:{" "}
          <div className="flex items-center pl-2 space-x-1">
            <Skeleton className="h-4 w-4 rounded-full delay-75" />
            <Skeleton className="h-4 w-4 rounded-full delay-150" />
            <Skeleton className="h-4 w-4 rounded-full delay-300" />
          </div>
        </div>
      )}
    </div>
  );
}
