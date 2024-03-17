"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

export default function Home() {
  const [delisheryStats, setDelisheryStats] = useState({
    stats: {
      num_of_deliveries: 0,
      num_of_schedules: 0,
      total_delivery_items: 0,
      total_scheduled_deliveries: 0,
    },
    audit: {
      event1: {},
      event2: {},
    },
    lastUpdated: "",
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      const statsResponse = await fetch(
        "http://acit3855lab6a.westus.cloudapp.azure.com:8100/stats"
      );
      const statsData = await statsResponse.json();

      // const auditResponse = await fetch(
      //   "http://acit3855lab6a.westus.cloudapp.azure.com:8110/delishery/delivery?index=0"
      // );
      // const auditData = await auditResponse.json();

      setDelisheryStats({
        stats: statsData,
        audit: {
          event1: {},
          event2: {},
        },
        lastUpdated: new Date().toLocaleString(),
      });
      setIsLoading(false);
    };

    fetchStats();
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
            <p>
              Number of deliveries: {delisheryStats.stats.num_of_deliveries}
            </p>
            <p>
              Total delivery items: {delisheryStats.stats.total_delivery_items}
            </p>
          </div>
        </div>
      </section>

      <h2>Home</h2>
      <h3>Home</h3>
      <p>Why hello there</p>
    </main>
  );
}
