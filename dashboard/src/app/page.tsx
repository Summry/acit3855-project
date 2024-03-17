"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

type DelisheryStats = {
  stats: {
    num_of_deliveries: number;
    num_of_schedules: number;
    total_delivery_items: number;
    total_scheduled_deliveries: number;
  };
  audit: {
    event1: {
      delivery_id: string;
      item_quantity: number;
      requested_date: string;
      trace_id: string;
      user_id: string;
    };
    event2: {
      created_date: string;
      number_of_deliveries: number;
      schedule_id: string;
      trace_id: string;
      user_id: string;
    };
  };
  lastUpdated: string;
};

export default function Home() {
  const [delisheryStats, setDelisheryStats] = useState<DelisheryStats>();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const statsResponse = await fetch(
          "http://acit3855lab6a.westus.cloudapp.azure.com:8100/stats"
        );
        const statsData = await statsResponse.json();

        // const auditResponse = await fetch(
        //   "http://acit3855lab6a.westus.cloudapp.azure.com:8110/delishery/delivery?index=0"
        // );
        // const auditData = await auditResponse.json();

        setDelisheryStats((prev) => ({
          stats: statsData,
          audit: {
            event1: {
              delivery_id: "",
              item_quantity: 0,
              requested_date: "",
              trace_id: "",
              user_id: "",
            },
            event2: {
              created_date: "",
              number_of_deliveries: 0,
              schedule_id: "",
              trace_id: "",
              user_id: "",
            },
          },
          lastUpdated: new Date().toLocaleString(),
        }));
        setIsLoading(false);
      } catch (e) {
        console.error("There was an error fetching data:", e);
      }
    };

    const interval = setInterval(() => {
      fetchStats();
    }, 2000);

    return () => clearInterval(interval);
  }, [delisheryStats]);

  return (
    <main className="h-screen flex flex-col items-center">
      <figure className="flex flex-col items-center">
        <Image
          src="/food-delivery.png"
          alt="Delishery"
          height={150}
          width={150}
        />
        <figcaption>
          <a
            href="https://www.flaticon.com/free-icons/food-delivery"
            title="food delivery icons"
            className="hover:text-blue-700 hover:underline text-xs"
          >
            Food delivery icons created by lapiyee - Flaticon
          </a>
        </figcaption>
      </figure>

      <section>
        <h2>Latest Stats</h2>
        <div>
          <div>
            <h3>Deliveries</h3>
            {isLoading && <p>Loading...</p>}
            {delisheryStats?.stats && (
              <div>
                <p>
                  Total deliveries:{" "}
                  {delisheryStats?.stats.total_scheduled_deliveries}
                </p>
                <p>
                  Total delivery items:{" "}
                  {delisheryStats?.stats.total_delivery_items}
                </p>
              </div>
            )}
          </div>
          <div>
            <h3>Schedules</h3>
            {isLoading && <p>Loading...</p>}
            {delisheryStats?.stats && (
              <div>
                <p>Total schedules: {delisheryStats?.stats.num_of_schedules}</p>
                <p>
                  Total deliveries: {delisheryStats?.stats.num_of_deliveries}
                </p>
              </div>
            )}
          </div>
        </div>
      </section>

      <p className="font-bold">Last Updated: {delisheryStats?.lastUpdated}</p>

      <h2>Home</h2>
      <h3>Home</h3>
      <p>Why hello there</p>
    </main>
  );
}
