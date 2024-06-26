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

    if (auditDeliveryResponse.status === 404 && auditScheduleResponse.status === 404) {
      return {
        delivery: null,
        deliveryIndex: randomDeliveryIndex,
        schedule: null,
        scheduleIndex: randomScheduleIndex,
      };
    }

    if (auditDeliveryResponse.status === 404) {
      const auditSchedule: IAuditSchedule = await auditScheduleResponse.json();
      return {
        delivery: null,
        deliveryIndex: randomDeliveryIndex,
        schedule: auditSchedule,
        scheduleIndex: randomScheduleIndex,
      };
    }

    if (auditScheduleResponse.status === 404) {
      const auditDelivery: IAuditDelivery = await auditDeliveryResponse.json();
      return {
        delivery: auditDelivery,
        deliveryIndex: randomDeliveryIndex,
        schedule: null,
        scheduleIndex: randomScheduleIndex,
      };
    }

    if (auditDeliveryResponse.status !== 200) {
      throw new Error("There was an error fetching the Audit Delivery stats.");
    }

    if (auditScheduleResponse.status !== 200) {
      throw new Error("There was an error fetching the Audit Schedule stats.");
    }

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
