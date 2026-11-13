from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from core.api import EventViewSet, LoginView, LogoutView, PublicEventView, RegisterView, TicketTypeViewSet
from core.views import health, spa

router = DefaultRouter()
router.register("events", EventViewSet, basename="event")
router.register("ticket-types", TicketTypeViewSet, basename="tickettype")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    path("api/auth/token/", LoginView.as_view()),
    path("api/auth/logout/", LogoutView.as_view()),
    path("api/public/events/<int:pk>/", PublicEventView.as_view()),
    path("api/public/events/<int:pk>/register/", RegisterView.as_view()),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("api/", include(router.urls)),
    # Everything else is a React route; must stay last.
    re_path(r"^(?!api/|admin/|static/|assets/).*$", spa),
]

