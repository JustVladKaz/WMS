from apscheduler.schedulers.background import BackgroundScheduler
from .tasks import generate_daily_sales_report

def start_scheduler():
    scheduler = BackgroundScheduler()
    if not scheduler.running:
        # Remove old jobs before adding a new one
        scheduler.remove_all_jobs()
        scheduler.add_job(generate_daily_sales_report, "cron", hour=23, minute=59)
        scheduler.start()
