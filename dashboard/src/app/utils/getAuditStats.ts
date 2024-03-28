import { IAuditDelivery, IAuditSchedule } from "../types/AuditStats";

export default async function getAuditStats() {
  const randomDeliveryIndex = Math.floor(Math.random() * 100);
  const randomScheduleIndex = Math.floor(Math.random() * 100);

  try {
    const auditDeliveryResponse = await fetch(
      `${process.env.NEXT_PUBLIC_AUDIT_API_URL}/delivery?index=${randomDeliveryIndex}`
    );
    const auditScheduleResponse = await fetch(
      `${process.env.NEXT_PUBLIC_AUDIT_API_URL}/schedule?index=${randomScheduleIndex}`
    );

    if (auditDeliveryResponse.status === 404) {
      throw new Error(
        "Audit Delivery stats at the specified index is not found."
      );
    }

    if (auditScheduleResponse.status === 404) {
      throw new Error(
        "Audit Schedule stats at the specified index is not found."
      );
    }

    if (auditDeliveryResponse.status !== 200) {
      throw new Error("There was an error fetching the Audit Delivery stats.");
    }

    if (auditScheduleResponse.status !== 200) {
      throw new Error("There was an error fetching the Audit Schedule stats.");
    }

    // if (!auditDeliveryResponse.ok) {
    //   throw new Error("There was an error fetching the Audit Delivery stats.");
    // }

    // if (!auditScheduleResponse.ok) {
    //   throw new Error("There was an error fetching the Audit Schedule stats.");
    // }

    const auditDelivery: IAuditDelivery = await auditDeliveryResponse.json();
    const auditSchedule: IAuditSchedule = await auditScheduleResponse.json();

    return {
      delivery: auditDelivery,
      deliveryIndex: randomDeliveryIndex,
      schedule: auditSchedule,
      scheduleIndex: randomScheduleIndex,
    };
  } catch (error) {

    console.error(error);
    
    return {
      delivery: null,
      deliveryIndex: randomDeliveryIndex,
      schedule: null,
      scheduleIndex: randomScheduleIndex,
    };
  }
}
