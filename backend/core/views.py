import logging
import os

from django.conf import settings
from django.db import DatabaseError, connection
from django.http import FileResponse, Http404, JsonResponse

logger = logging.getLogger(__name__)


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        logger.exception("health check failed: database unreachable")
        return JsonResponse({"status": "error", "database": "unreachable"}, status=503)
    # Render sets RENDER_GIT_COMMIT; the deploy workflow waits until this matches the commit it deployed.
    commit = os.environ.get("RENDER_GIT_COMMIT", "unknown")
    return JsonResponse({"status": "ok", "database": "ok", "commit": commit})


def spa(request):
    """Serve the React app's index.html for client-side routes like /staff."""
    try:
        index = open(settings.FRONTEND_DIST / "index.html", "rb")
    except FileNotFoundError:
        raise Http404("Frontend not built.")
    response = FileResponse(index, content_type="text/html")
    # index.html names the current hashed JS/CSS files, so browsers must revalidate it.
    response["Cache-Control"] = "no-cache"
    return response
