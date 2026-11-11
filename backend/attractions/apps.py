from django.apps import AppConfig


class AttractionsConfig(AppConfig):
    name = 'attractions'

    def ready(self):
        import sys
        if "runserver" in sys.argv or "gunicorn" in sys.argv[0]:
            from .services.nearby_parks import _load_parks
            try:
                _load_parks()
            except Exception:
                pass  # DB may not be ready during migrations
