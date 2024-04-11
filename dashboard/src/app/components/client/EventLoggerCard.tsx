'use client';

import { IEventLoggerStats } from '@/app/types/EventLoggerStats';
import getEventLoggerStats from '@/app/utils/getEventLoggerStats';
import { Skeleton } from '@/components/ui/skeleton';
import React, { useState, useEffect } from 'react'

export default function EventLoggerCard() {
  const [eventLoggerStats, setEventLoggerStats] = useState<IEventLoggerStats>()

  useEffect(() => {
    const fetchData = async () => {
      const eventLoggerStats = await getEventLoggerStats()
      setEventLoggerStats(eventLoggerStats)
    };

    const timeout = setTimeout(fetchData, 4000)

    return () => clearTimeout(timeout)
  }, [eventLoggerStats])

  const eventLoggerContent = eventLoggerStats ? (
    <div className="space-y-2 pt-2">
      <p>0001 Events Logged: {eventLoggerStats.eventOne}</p>
      <p>0002 Events Logged: {eventLoggerStats.eventTwo}</p>
      <p>0003 Events Logged: {eventLoggerStats.eventThree}</p>
      <p>0004 Events Logged: {eventLoggerStats.eventFour}</p>
    </div>
  ) : (
    <div className="space-y-2 pt-2">
      <Skeleton className="h-4 w-[200px]" />
      <Skeleton className="h-4 w-[200px] delay-150" />
      <Skeleton className="h-4 w-[150px] delay-250" />
      <Skeleton className="h-4 w-[150px] delay-350" />
    </div>
  )

  return (
    <div>
      <div className="flex flex-col justify-center items-center">
        <div className="flex justify-center w-[500px]">
          <div className="flex flex-col p-4">
            {eventLoggerContent}
          </div>
        </div>
      </div>
    </div>
  )
}
