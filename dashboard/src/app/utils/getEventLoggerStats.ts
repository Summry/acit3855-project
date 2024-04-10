import { IEventLoggerStats } from "../types/EventLoggerStats"

export default async function getEventLoggerStats() {
  try {
    const eventLoggerStats = await fetch(
      `${process.env.NEXT_PUBLIC_EVENT_LOGGER_API_URL}`
    )
    
    if (eventLoggerStats.status === 404) {
      return {
        eventOne: 0,
        eventTwo: 0,
        eventThree: 0,
        eventFour: 0
      }
    }
    
    if (!eventLoggerStats.ok) {
      throw new Error("There was an error fetching the Event Logger stats - Status is not OK")
    }
    
    if (eventLoggerStats.status !== 200) {
      throw new Error("There was an error fetching the Event Logger stats - Status is not 200")
    }

    const data: IEventLoggerStats = await eventLoggerStats.json()

    return data
  } catch (e) {
    console.log(e)
  }
}
