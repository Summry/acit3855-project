import { IEventLoggerStats } from "../types/EventLoggerStats";

export default async function getEventLoggerStats() {
  try {
    const eventLoggerStats = await fetch(
      `${process.env.NEXT_PUBLIC_EVENT_LOGGER_API_URL}`
    );

    if (!eventLoggerStats.ok) {
      throw new Error("There was an error fetching the Event Logger stats - Status is not OK");
    }

    if (eventLoggerStats.status === 404) {
      // Return default values if the endpoint returns 404
      return {
        eventOne: 0,
        eventTwo: 0,
        eventThree: 0,
        eventFour: 0
      };
    }

    if (eventLoggerStats.status !== 200) {
      throw new Error("There was an error fetching the Event Logger stats - Status is not 200");
    }

    const data: { [key: string]: number } = await eventLoggerStats.json();

    // Transform the keys and create a new object with the appropriate keys
    const transformedData: IEventLoggerStats = {
      eventOne: data["0001"] || 0,
      eventTwo: data["0002"] || 0,
      eventThree: data["0003"] || 0,
      eventFour: data["0004"] || 0
    };

    return transformedData;
  } catch (e) {
    console.log(e);
  }
}
