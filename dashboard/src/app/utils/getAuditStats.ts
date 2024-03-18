import { IAuditDelivery, IAuditSchedule } from "../types/AuditStats";

export default async function getAuditStats() {
  try {
    const auditDeliveryResponse = await fetch(
      "http://acit3855lab6a.westus.cloudapp.azure.com:8110/delishery/delivery?index=0"
    );
    const auditScheduleResponse = await fetch(
      "http://acit3855lab6a.westus.cloudapp.azure.com:8110/delishery/schedule?index=0"
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
