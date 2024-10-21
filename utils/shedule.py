import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from core.repositories.event import EventRepository
from core.repositories.publication import PublicationRepository
from .telegram import main
from .events import main

repo = PublicationRepository()
repo_ev = EventRepository()
scheduler = AsyncIOScheduler()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def schedule_tasks():
    tasks = await repo.select_all()
    for task in tasks:
        hour, minute = map(int, task.time.split(":"))

        # Определение дней недели в зависимости от параметра task.today
        if task.today == 0:
            trigger = CronTrigger(hour=hour, minute=minute, day_of_week="mon-fri")
        elif task.today == 5:
            trigger = CronTrigger(hour=hour, minute=minute, day_of_week="sat,sun")
        else:
            logger.warning(f"Unknown task.today value: {task.today} for task {task.id}")
            continue

        job_id = f"task_{task.id}"

        # Проверка на существование задачи с таким же идентификатором
        task_id = str(task.thematic_block_id).split(",")
        if not scheduler.get_job(job_id):
            scheduler.add_job(main, trigger=trigger, id=job_id, args=[task_id])

    events = await repo_ev.select_all()
    for event in events:
        hour, minute = map(int, event.time_out.split(":"))
        trigger = CronTrigger(hour=hour, minute=minute)
        job_id = f"event_{event.id}"
        if not scheduler.get_job(job_id):
            scheduler.add_job(main, trigger=trigger, id=job_id, args=[event.id])


async def update_scheduler():
    list_task = await repo.select_all()
    tasks = []
    for task_id in list_task:
        tasks.append(task_id.id)
    for job in scheduler.get_jobs():
        if job.id.startswith("task_"):
            if int(job.id.split("_")[1]) not in tasks:
                scheduler.remove_job(job.id)
    await schedule_tasks()


async def check_new_tasks():
    logger.info("Checking for new tasks...")
    await update_scheduler()
