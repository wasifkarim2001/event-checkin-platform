import io
import json
import logging

import pytest

from .logs import JsonFormatter

pytestmark = pytest.mark.django_db


@pytest.fixture
def json_logs():
    """Capture every log line, formatted exactly as in production."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.addHandler(handler)
    yield lambda: [json.loads(line) for line in stream.getvalue().splitlines()]
    root.removeHandler(handler)


def find(lines, message):
    return [line for line in lines if line["message"] == message]


def test_all_lines_of_a_request_share_its_request_id(api_as, ticket_type, json_logs):
    response = api_as().post(
        f"/api/public/events/{ticket_type.event.pk}/register/",
        {"ticket_type": ticket_type.pk, "name": "Ada", "email": "ada@example.com"},
        format="json",
    )
    lines = json_logs()
    (request_line,) = find(lines, "request")
    (created,) = find(lines, "registration created")
    assert request_line["request_id"] == created["request_id"] == response["X-Request-ID"]
    assert request_line["method"] == "POST"
    assert request_line["status"] == 201
    assert isinstance(request_line["duration_ms"], float)


def test_repeat_checkin_logs_reason_and_staff_user(api_as, attendee, staff_user, json_logs):
    client = api_as(staff_user)
    url = f"/api/events/{attendee.ticket_type.event.pk}/checkins/"
    client.post(url, {"code": attendee.code}, format="json")
    client.post(url, {"code": attendee.code}, format="json")
    lines = json_logs()
    (rejected,) = find(lines, "check-in rejected")
    assert rejected["reason"] == "already_checked_in"
    assert rejected["attendee_id"] == attendee.pk
    assert [line["user_id"] for line in find(lines, "request")] == [staff_user.pk, staff_user.pk]


def test_exception_is_logged_and_request_id_is_null_outside_requests(json_logs):
    try:
        1 / 0
    except ZeroDivisionError:
        logging.getLogger("test").exception("boom")
    (line,) = json_logs()
    assert line["request_id"] is None
    assert "ZeroDivisionError" in line["exception"]
