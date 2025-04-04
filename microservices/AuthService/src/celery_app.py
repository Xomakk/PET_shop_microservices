from celery import Celery, shared_task
from database import REDIS_URL

app = Celery(__name__, backend=REDIS_URL, broker=REDIS_URL, include=["auth.tasks"])
app.conf.update(
    task_track_started=True,
    task_time_limit=30 * 60,
)
