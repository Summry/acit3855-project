"use client";

import Image from "next/image";
import ProcessorCard from "./components/client/ProcessorCard";

export default function Home() {
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
          <ProcessorCard />
        </div>
      </section>
    </main>
  );
}
