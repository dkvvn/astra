from datetime import timedelta
from pathlib import Path
from aiogram import Bot
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session
from astra.api import config
from astra.core import db, models, schema
from astra.api.bot import (
    start_bot,
    stop_bot,
    set_bot_webhook,
    process_wh_update,
)
from astra.api.utils import short_uuid, get_bot_wh_path
from astra.misc.utils import result_stringify, logging_setup, devport_init
import logging
import orjson

logger = logging.getLogger(__name__)
logging_setup(logger)

devport_init()

app = FastAPI()
start_bot()


@app.get("/api/test")
def test_helloworld():
    return "Hello World!"


@app.on_event("startup")
async def on_startup():
    # TG
    await set_bot_webhook()


@app.on_event("shutdown")
async def on_shutdown():
    # TG
    await stop_bot()


app.post(get_bot_wh_path())(process_wh_update)
logger.info(get_bot_wh_path())


@app.post("/api/status")
async def process_task_status(task_info: schema.TaskInfo):
    bot = Bot.get_current()

    with Session(db.engine) as session:
        task = session.get(models.Task, task_info.id)
        if task is None:
            raise HTTPException(
                404,
                f"Task with id '{task_info.id}' does not exist, but task_info contains it",
            )
        user_id = task.account.service_id
        job = task.job
        if job is None:
            raise HTTPException(404, f"Task with id '{task_info.id}' does not have Job")

        if task_info.status != schema.task_states.SUCCESS:
            position = job.get_queue_position(session)
            if position == 0:
                await bot.send_message(
                    user_id,
                    f"#T{short_uuid(task_info.id)} Статус: {task_info.status}, в обработке",
                )
            else:
                await bot.send_message(
                    user_id,
                    f"#T{short_uuid(task_info.id)} Статус: {task_info.status}, позиция в очереди: {position}",
                )
            return
        result = schema.TranscribeResult(**orjson.loads(task_info.result))
        execution_time: timedelta = job.endedAt - job.createdAt
        await bot.send_message(
            user_id,
            f"#T{short_uuid(task_info.id)} Анализ завершён за {execution_time.seconds} сек.",
        )
        await bot.send_message(user_id, result_stringify(result, " "))


@app.get("/api/file")
async def get_file(job_id: str = Body(embed=True)):
    with Session(db.engine) as session:
        job = session.get(models.Job, job_id)
        if job is None:
            raise HTTPException(404, f"job not found ({job_id})")
        filepath = config.MEDIA_DIR / job.filehash
        if not filepath.is_file():
            raise HTTPException(410, "File removed.")
        return FileResponse(filepath)


app.mount("/", StaticFiles(directory='./frontend/dist', html=True), name="static")