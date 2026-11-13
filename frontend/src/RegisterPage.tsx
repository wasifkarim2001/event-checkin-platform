import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { api, ApiError, errorMessage } from "./api";
import type { PublicEvent, Registration } from "./types";

export default function RegisterPage() {
  const { eventId } = useParams();
  const [event, setEvent] = useState<PublicEvent | null>(null);
  const [loadError, setLoadError] = useState("");
  const [ticketType, setTicketType] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [registration, setRegistration] = useState<Registration | null>(null);

  useEffect(() => {
    let ignore = false;
    api<PublicEvent>(`/public/events/${eventId}/`)
      .then((data) => {
        if (!ignore) setEvent(data);
      })
      .catch((err) => {
        if (ignore) return;
        setLoadError(
          err instanceof ApiError && err.status === 404 ? "Event not found." : "Could not load this event.",
        );
      });
    return () => {
      ignore = true;
    };
  }, [eventId]);

  async function register() {
    setBusy(true);
    setError("");
    try {
      const result = await api<Registration>(`/public/events/${eventId}/register/`, {
        method: "POST",
        body: { ticket_type: Number(ticketType), name, email },
      });
      setRegistration(result);
    } catch (err) {
      setError(errorMessage(err, "Registration failed. Try again."));
    } finally {
      setBusy(false);
    }
  }

  if (loadError) {
    return (
      <main>
        <p role="alert">{loadError}</p>
      </main>
    );
  }
  if (!event) {
    return (
      <main>
        <p>Loading…</p>
      </main>
    );
  }

  if (registration) {
    return (
      <main>
        <h1>You're registered</h1>
        <p>Show this code at the door for {event.name}:</p>
        <p className="code">{registration.code}</p>
        <p>Save it now: it isn't emailed to you yet.</p>
      </main>
    );
  }

  const available = event.ticket_types.some((t) => t.remaining > 0);

  return (
    <main>
      <h1>{event.name}</h1>
      <p>
        {new Date(event.starts_at).toLocaleString()}
        {event.venue && `, ${event.venue}`}
      </p>
      {!available ? (
        <p>No tickets available.</p>
      ) : (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            void register();
          }}
        >
          <label>
            Ticket type
            <select value={ticketType} onChange={(e) => setTicketType(e.target.value)} required>
              <option value="" disabled>
                Choose…
              </option>
              {event.ticket_types.map((t) => (
                <option key={t.id} value={t.id} disabled={t.remaining === 0}>
                  {t.name} ({t.remaining === 0 ? "sold out" : `${t.remaining} left`})
                </option>
              ))}
            </select>
          </label>
          <label>
            Name
            <input value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" required />
          </label>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />
          </label>
          {error && <p role="alert">{error}</p>}
          <button disabled={busy}>{busy ? "Registering…" : "Register"}</button>
        </form>
      )}
    </main>
  );
}