import { ProcessorStats } from "../types/ProcessorStats";

export default async function getProcessorStats() {
  try {
    const statsResponse = await fetch(
      "http://acit3855lab6a.westus.cloudapp.azure.com:8100/stats"
    );

    if (!statsResponse.ok) {
      throw new Error("There was an error fetching Processor Stats data.");
    }

    const statsData: ProcessorStats = await statsResponse.json();

    return statsData;
  } catch (error) {
    console.error(error);
  }
}
