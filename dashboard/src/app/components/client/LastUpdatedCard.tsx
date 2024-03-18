"use client";

import React from "react";
import { useEffect, useState } from "react";

export default function LastUpdatedCard() {
  const [lastUpdated, setLastUpdated] = useState<string>("");

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdated(new Date().toLocaleString());
    }, 2000);

    return () => clearInterval(interval);
  });

  return (
    <div>
      {lastUpdated ? (
        <p className="font-bold">Last Updated: {lastUpdated}</p>
      ) : (
        <p className="font-bold">Last Updated: Loading...</p>
      )}
    </div>
  );
}
