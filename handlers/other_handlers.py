from aiogram import Router
from aiogram.types import Message

from lexicon.lexicon import LEXICON

router: Router = Router()


# This handler will respond to any user messages,
# not provided by the logic of the bot
@router.message()
async def send_echo(message: Message):
    await message.answer(LEXICON['miss_message'])
