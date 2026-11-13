import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { api, ApiError } from "./api";
import type { EventInfo, EventStats } from "./types";

const POLL_MS = 5000;

export default function DashboardPage() {
  const { eventId } = useParams();
  const navigate = useNavigate();
  const [eventName, setEventName] = useState("");
  const [stats, setStats] = useState<EventStats | null>(null);
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;
    api<EventInfo>(`/events/${eventId}/`)
      .then((event) => {
        if (!ignore) setEventName(event.name);
      })
      .catch(() => {});
    return () => {
      ignore = true;
    };
  }, [eventId]);

  useEffect(() => {
    let ignore = false;

    function load() {
      if (document.hidden) return;
      api<EventStats>(`/events/${eventId}/stats/`)
        .then((data) => {
          if (ignore) return;
          setStats(data);
          setUpdatedAt(new Date());
          setError("");
        })
        .catch((err) => {
          if (ignore) return;
          if (err instanceof ApiError && err.status === 401) navigate("/login");
          else if (err instanceof ApiError && err.status === 404) setError("Event not found, or you're not staff for it.");
          else setError("Connection problem. Showing the last numbers, retrying…");
        });
    }

    load();
    const timer = setInterval(load, POLL_MS);
    return () => {
      ignore = true;
      clearInterval(timer);
    };
  }, [eventId, navigate]);

  return (
    <main>
      <header className="row">
        <h1>Dashboard: {eventName || "…"}</h1>
        <Link to="/staff">All events</Link>
      </header>
      {error && <p role="alert">{error}</p>}
      {!stats && !error && <p>Loading…</p>}
      {stats && (
        <>
          <div className="totals">
            <Stat label="Checked in" value={stats.checked_in} of={stats.registered} />
            <Stat label="Registered" value={stats.registered} of={stats.capacity} />
          </div>
          <table>
            <thead>
              <tr>
                <th>Ticket type</th>
                <th>Registered</th>
                <th>Checked in</th>
              </tr>
            </thead>
            <tbody>
              {stats.ticket_types.map((t) => (
                <tr key={t.id}>
                  <td>{t.name}</td>
                  <td>
                    {t.registered} / {t.capacity}
                  </td>
                  <td>
                    {t.checked_in} / {t.registered}
                    <progress value={t.checked_in} max={Math.max(t.registered, 1)} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {updatedAt && (
            <p className="muted">
              Updated {updatedAt.toLocaleTimeString()} · refreshes every {POLL_MS / 1000} s
            </p>
          )}
        </>
      )}
    </main>
  );
}

function Stat({ label, value, of }: { label: string; value: number; of: number }) {
  const percent = of > 0 ? Math.round((value / of) * 100) : 0;
  return (
    <div className="stat">
      <span className="stat-value">
        {value} <small>/ {of}</small>
      </span>
      <span>
        {label} · {percent}%
      </span>
    </div>
  );
}