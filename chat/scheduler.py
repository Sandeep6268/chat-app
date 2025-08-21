from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from chat.management.commands.update_online_status import Command as StatusCommand

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    # Run every 5 minutes
    scheduler.add_job(
        StatusCommand().handle,
        'interval',
        minutes=5,
        id='update_online_status',
        replace_existing=True
    )
    
    scheduler.start()
