export type TicketType = {
  id: number;
  event: number;
  name: string;
  capacity: number;
};

export type EventInfo = {
  id: number;
  name: string;
  venue: string;
  starts_at: string;
  ends_at: string;
  owner: string;
  staff: string[];
  ticket_types: TicketType[];
};

export type Page<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};