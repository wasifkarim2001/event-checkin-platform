import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import { api, ApiError, clearToken } from "./api";
import type { EventInfo, Page } from "./types";

export default function StaffEventsPage() {
  const [events, setEvents] = useState<EventInfo[] | null>(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    let ignore = false;
    api<Page<EventInfo>>("/events/")
      .then((page) => {
        if (!ignore) setEvents(page.results);
      })
      .catch((err) => {
        if (ignore) return;
        if (err instanceof ApiError && err.status === 401) navigate("/login");
        else setError("Could not load events.");
      });
    return () => {
      ignore = true;
    };
  }, [navigate]);

  function signOut() {
    clearToken();
    navigate("/login");
  }

  return (
    <main>
      <header className="row">
        <h1>Your events</h1>
        <button onClick={signOut}>Sign out</button>
      </header>
      {error && <p role="alert">{error}</p>}
      {events === null && !error && <p>Loading…</p>}
      {events?.length === 0 && <p>No events yet. Create one in the admin.</p>}
      <ul>
        {events?.map((event) => (
          <li key={event.id}>
            <strong>{event.name}</strong>, {new Date(event.starts_at).toLocaleString()}
            {event.venue && ` at ${event.venue}`}
           {" · "}
            <Link to={`/events/${event.id}/register`}>Registration page</Link>
                        {" · "}
            <Link to={`/staff/events/${event.id}/checkin`}>Check in</Link>
          </li>
        ))}
      </ul>
    </main>
  );
}