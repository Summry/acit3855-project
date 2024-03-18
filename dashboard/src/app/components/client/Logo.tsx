import Image from "next/image";

export default function Logo() {
  return (
    <figure className="flex flex-col items-center pt-2">
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
  );
}
