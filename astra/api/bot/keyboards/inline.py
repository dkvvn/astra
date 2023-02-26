from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)
from astra.api import config


def app_button(text: str):
    web_app = WebAppInfo(url=config.SELF_URL_EXTERNAL)
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text=text, web_app=web_app))
    return kb

def create_post(kb: InlineKeyboardMarkup = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="Создать стенограмму из результата", callback_data="create_post"))
    return kb

def edit_post(post_id: str, kb: InlineKeyboardMarkup = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    web_app = WebAppInfo(url=f"{config.SELF_URL_EXTERNAL}/?post_id={post_id}")
    kb.add(InlineKeyboardButton(text="Изменить стенограмму", web_app=web_app))
    return kb
