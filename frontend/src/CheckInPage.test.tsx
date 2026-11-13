import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router";
import { expect, test, vi } from "vitest";
import CheckInPage from "./CheckInPage";

const EVENT = {
  id: 2,
  name: "DevConf",
  venue: "",
  starts_at: "2030-05-01T09:00:00Z",
  ends_at: "2030-05-01T17:00:00Z",
  owner: "org",
  staff: [],
  ticket_types: [],
};

function json(status: number, body: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } }),
  );
}

function mockApi(checkInStatus: number, checkInBody: unknown) {
  const fetchMock = vi.fn((_url: string, options?: RequestInit) =>
    options?.method === "POST" ? json(checkInStatus, checkInBody) : json(200, EVENT),
  );
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function renderPage() {
  render(
    <MemoryRouter initialEntries={["/staff/events/2/checkin"]}>
      <Routes>
        <Route path="/staff/events/:eventId/checkin" element={<CheckInPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

test("successful check-in shows the attendee and clears the box", async () => {
  const fetchMock = mockApi(201, {
    attendee: {
      id: 1,
      name: "Ada",
      email: "ada@example.com",
      code: "ABCD2345",
      ticket_type: "General",
      registered_at: "2030-04-01T09:00:00Z",
      checked_in_at: "2030-05-01T09:05:00Z",
    },
    checked_in_at: "2030-05-01T09:05:00Z",
    checked_in_by: "staff",
  });
  renderPage();

  const input = await screen.findByLabelText("Check-in code");
  await userEvent.type(input, " abcd2345{Enter}");

  expect(await screen.findByText("✓ Ada")).toBeInTheDocument();
  expect(input).toHaveValue("");
  const [url, options] = fetchMock.mock.calls[1];
  expect(url).toBe("/api/events/2/checkins/");
  expect(JSON.parse(options?.body as string)).toEqual({ code: "ABCD2345" });
});

test("409 shows 'already checked in' with the code", async () => {
  mockApi(409, { detail: "Already checked in.", checked_in_at: "2030-05-01T09:05:00Z" });
  renderPage();

  await userEvent.type(await screen.findByLabelText("Check-in code"), "ABCD2345{Enter}");

  expect(await screen.findByText("Already checked in")).toBeInTheDocument();
  expect(screen.getByText(/ABCD2345 was checked in at/)).toBeInTheDocument();
});