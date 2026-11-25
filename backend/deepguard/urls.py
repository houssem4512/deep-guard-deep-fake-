"""URL dispatch — the exact routes of the original FastAPI backend."""

from pathlib import Path

from django.urls import path, re_path
from django.views.static import serve as static_serve

from api import views

BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
DIST_DIR = BASE_DIR.parent / "frontend" / "dist"  # npm run build output

urlpatterns = [
    path("health", views.health, name="health"),
    path("health/", views.health),
    path("model/metadata", views.model_metadata, name="model_metadata"),
    path("model/metadata/", views.model_metadata),
    path("predict", views.predict, name="predict"),
    path("predict/", views.predict),
    path("predict/visualize", views.predict_visualize, name="predict_visualize"),
    path("predict/visualize/", views.predict_visualize),
    # Built-in sample faces for the demo widget and the workbench (vite
    # proxies /media here in dev; same origin in the built deployment).
    re_path(r"^media/(?P<path>.*)$", static_serve, {"document_root": BASE_DIR / "media"}),
    # Vite build assets (only exist after `npm run build`).
    re_path(r"^assets/(?P<path>.*)$", static_serve, {"document_root": DIST_DIR / "assets"}),
    re_path(r"^$", views.home, name="home"),
    # The React app uses history routing (/login, /user/analyze, ...): any
    # unknown GET path falls back to index.html, exactly like the original
    # SPAStaticFiles mount in FastAPI.
    re_path(r"^(?!api/|media/|assets/).*$", views.home),
]
