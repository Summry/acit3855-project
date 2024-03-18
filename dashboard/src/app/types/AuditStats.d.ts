export interface IAuditDelivery {
  delivery_id: string;
  item_quantity: number;
  requested_date: string;
  trace_id: string;
  user_id: string;
}

export interface IAuditSchedule {
  created_date: string;
  number_of_deliveries: number;
  schedule_id: string;
  trace_id: string;
  user_id: string;
}

export interface IAuditStats {
  delivery: AuditDelivery;
  schedule: AuditSchedule;
}
