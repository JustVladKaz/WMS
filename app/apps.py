from django.apps import AppConfig

class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        if not hasattr(self, "scheduler_started"):
            print("🚀 Scheduler is starting...")
            from .scheduler import start_scheduler
            start_scheduler()
            self.scheduler_started = True  # Prevent multiple runs
