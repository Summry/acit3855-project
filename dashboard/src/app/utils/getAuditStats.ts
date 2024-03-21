import { IAuditDelivery, IAuditSchedule } from "../types/AuditStats";
import getProcessorStats from "./getProcessorStats";

export default async function getAuditStats() {
  try {
    const processorStats = await getProcessorStats();

    if (!processorStats) {
      throw new Error(
        "There was an error fetching Processor Stats from Audit."
      );
    }

    // const randomDeliveryIndex = Math.floor(
    //   Math.random() * processorStats.num_of_deliveries
    // );
    // const randomScheduleIndex = Math.floor(
    //   Math.random() * processorStats.num_of_schedules
    // );

    const auditDeliveryResponse = await fetch(
      `${process.env.NEXT_PUBLIC_AUDIT_API_URL}/delivery?index=0`
    );
    const auditScheduleResponse = await fetch(
      `${process.env.NEXT_PUBLIC_AUDIT_API_URL}/schedule?index=0`
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

    if (!auditDeliveryResponse.ok) {
      throw new Error("There was an error fetching the Audit Delivery stats.");
    }

    if (!auditScheduleResponse.ok) {
      throw new Error("There was an error fetching the Audit Schedule stats.");
    }

    const auditDelivery: IAuditDelivery = await auditDeliveryResponse.json();
    const auditSchedule: IAuditSchedule = await auditScheduleResponse.json();

    return { delivery: auditDelivery, schedule: auditSchedule };
  } catch (error) {
    console.error(error);
    return {
      delivery: {
        delivery_id: "",
        item_quantity: 0,
        requested_date: "",
        trace_id: "",
        user_id: "",
      },
      schedule: {
        created_date: "",
        number_of_deliveries: 0,
        schedule_id: "",
        trace_id: "",
        user_id: "",
      },
    };
  }
}
