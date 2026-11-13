import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { api, ApiError, errorMessage } from "./api";
import type { CheckInResult, EventInfo } from "./types";

type Result =
  | { kind: "ok"; checkin: CheckInResult }
  | { kind: "already"; code: string; at: string }
  | { kind: "error"; message: string };

export default function CheckInPage() {
  const { eventId } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState<EventInfo | null>(null);
  const [loadError, setLoadError] = useState("");
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let ignore = false;
    api<EventInfo>(`/events/${eventId}/`)
      .then((data) => {
        if (!ignore) setEvent(data);
      })
      .catch((err) => {
        if (ignore) return;
        if (err instanceof ApiError && err.status === 401) navigate("/login");
        else if (err instanceof ApiError && err.status === 404) setLoadError("Event not found, or you're not staff for it.");
        else setLoadError("Could not load this event.");
      });
    return () => {
      ignore = true;
    };
  }, [eventId, navigate]);

  async function checkIn() {
    const submitted = code.trim().toUpperCase();
    setBusy(true);
    try {
      const checkin = await api<CheckInResult>(`/events/${eventId}/checkins/`, {
        method: "POST",
        body: { code: submitted },
      });
      setResult({ kind: "ok", checkin });
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        const body = err.body as { checked_in_at: string };
        setResult({ kind: "already", code: submitted, at: body.checked_in_at });
      } else if (err instanceof ApiError && err.status === 401) {
        navigate("/login");
      } else {
        setResult({ kind: "error", message: errorMessage(err, "Check-in failed. Try again.") });
      }
    } finally {
      setBusy(false);
      setCode("");
      inputRef.current?.focus();
    }
  }

  if (loadError) {
    return (
      <main>
        <p role="alert">{loadError}</p>
        <Link to="/staff">Back to your events</Link>
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

  return (
    <main>
      <header className="row">
        <h1>Check-in: {event.name}</h1>
        <Link to="/staff">All events</Link>
      </header>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (code.trim()) void checkIn();
        }}
      >
        <label>
          Check-in code
          <input
            ref={inputRef}
            className="code-input"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            autoFocus
            autoComplete="off"
            autoCapitalize="characters"
            spellCheck={false}
          />
        </label>
        <button disabled={busy || !code.trim()}>{busy ? "Checking…" : "Check in"}</button>
      </form>
      {result && <ResultPanel result={result} />}
    </main>
  );
}

function ResultPanel({ result }: { result: Result }) {
  if (result.kind === "ok") {
    const { attendee, checked_in_at } = result.checkin;
    return (
      <div className="result ok" role="status">
        <strong>✓ {attendee.name}</strong>
        <span>
          {attendee.ticket_type} · checked in at {new Date(checked_in_at).toLocaleTimeString()}
        </span>
      </div>
    );
  }
  if (result.kind === "already") {
    return (
      <div className="result warn" role="alert">
        <strong>Already checked in</strong>
        <span>
          {result.code} was checked in at {new Date(result.at).toLocaleTimeString()}
        </span>
      </div>
    );
  }
  return (
    <div className="result error" role="alert">
      <strong>✗ {result.message}</strong>
    </div>
  );
}