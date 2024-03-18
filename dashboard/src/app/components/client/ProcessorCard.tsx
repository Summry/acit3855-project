"use client";

import { ProcessorStats } from "@/app/types/ProcessorStats";
import { useEffect, useState } from "react";

export default function ProcessorCard() {
  const [processorStats, setProcessorStats] = useState<ProcessorStats>();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const statsResponse = await fetch(
          "http://acit3855lab6a.westus.cloudapp.azure.com:8100/stats"
        );

        if (!statsResponse.ok) {
          throw new Error("There was an error fetching Processor Stats data.");
        }

        const statsData: ProcessorStats = await statsResponse.json();

        setProcessorStats(statsData);
      } catch (error) {
        console.error(error);
      }
    };

    const interval = setInterval(() => {
      fetchStats();
    }, 2000);

    return () => clearInterval(interval);
  }, [processorStats]);

  const deliveriesContent = processorStats ? (
    <div>
      <p>Total deliveries: {processorStats.num_of_deliveries}</p>
      <p>Total delivery items: {processorStats.total_delivery_items}</p>
    </div>
  ) : (
    <p>Loading...</p>
  );

  const schedulesContent = processorStats ? (
    <div>
      <p>Total schedules: {processorStats.num_of_schedules}</p>
      <p>
        Total scheduled deliveries: {processorStats.total_scheduled_deliveries}
      </p>
    </div>
  ) : (
    <p>Loading...</p>
  );

  return (
    <div>
      <h3>Deliveries</h3>
      {deliveriesContent}
      <h3>Schedules</h3>
      {schedulesContent}
    </div>
  );
}
