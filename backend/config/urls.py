from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from core.api import EventViewSet, PublicEventView, RegisterView, TicketTypeViewSet
from core.views import health

router = DefaultRouter()
router.register("events", EventViewSet, basename="event")
router.register("ticket-types", TicketTypeViewSet, basename="tickettype")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    path("api/auth/token/", obtain_auth_token),
    path("api/public/events/<int:pk>/", PublicEventView.as_view()),
    path("api/public/events/<int:pk>/register/", RegisterView.as_view()),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("api/", include(router.urls)),
]
