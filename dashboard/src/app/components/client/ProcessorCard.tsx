"use client";

import { ProcessorStats } from "@/app/types/ProcessorStats";
import getProcessorStats from "@/app/utils/getProcessorStats";
import { useEffect, useState } from "react";

export default function ProcessorCard() {
  const [processorStats, setProcessorStats] = useState<ProcessorStats>();
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
    <div className="flex flex-col items-center">
      <p>Total deliveries: {processorStats.num_of_deliveries}</p>
      <p>Total delivery items: {processorStats.total_delivery_items}</p>
    </div>
  ) : (
    <p>Loading...</p>
  );

  const schedulesContent = processorStats ? (
    <div className="flex flex-col items-center">
      <p>Total schedules: {processorStats.num_of_schedules}</p>
      <p>
        Total scheduled deliveries: {processorStats.total_scheduled_deliveries}
      </p>
    </div>
  ) : (
    <p>Loading...</p>
  );

  return (
    <div className="flex flex-col justify-center items-center">
      <div className="flex justify-around items-center">
        <div className="flex flex-col items-center p-4">
          <h3>Deliveries</h3>
          {deliveriesContent}
        </div>
        <div className="flex flex-col items-center">
          <h3>Schedules</h3>
          {schedulesContent}
        </div>
      </div>
      {lastUpdated ? (
        <p className="font-bold pb-2">Last Updated: {lastUpdated}</p>
      ) : (
        <p className="font-bold pb-2">Last Updated: Loading...</p>
      )}
    </div>
  );
}
