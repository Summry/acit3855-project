import { IProcessorStats } from "../types/ProcessorStats";

export default async function getProcessorStats() {
  try {
    const statsResponse = await fetch(
      `${process.env.NEXT_PUBLIC_PROCESSOR_API_URL}`
    );

    if (!statsResponse.ok) {
      throw new Error("There was an error fetching Processor Stats data.");
    }

    if (!statsResponse) {
      throw new Error("There was an error fetching Processor Stats data.");
    }

    const statsData: IProcessorStats = await statsResponse.json();

    return statsData;
  } catch (error) {
    console.error(error);
    return {
      num_of_deliveries: 0,
      total_delivery_items: 0,
      num_of_schedules: 0,
      total_scheduled_deliveries: 0,
    };
  }
}
