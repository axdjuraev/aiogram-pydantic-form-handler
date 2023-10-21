from typing import Optional
from aiogram import Bot, Router, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from pydantic import BaseSettings
from pydantic_base_aiogram import SchemaBaseHandlersGroup


class Settings(BaseSettings):
    BOT_TOKEN: str

    class Config:
        env_file = '.env'


async def _main(handler_group: SchemaBaseHandlersGroup, settings: Optional[Settings] = None):
    router = Router()
    handler_group.register2router(router)

    @router.message(CommandStart())
    async def _(message: Message, state: FSMContext):
        return await handler_group.next(message, state)  # type: ignore

    dp = Dispatcher()
    dp.include_router(router)

    if settings is not None:
        bot = Bot(token=settings.BOT_TOKEN)
        await dp.start_polling(bot)


def main(handler_group: SchemaBaseHandlersGroup, settings: Optional[Settings] = None):
    import sys
    import logging
    import asyncio

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(_main(handler_group, settings))
    loop.close()

