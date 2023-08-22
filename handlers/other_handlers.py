from aiogram import Router
from aiogram.types import Message

router: Router = Router()


# Этот хэндлер будет реагировать на любые сообщения пользователя,
# не предусмотренные логикой работы бота
@router.message()
async def send_echo(message: Message):
    await message.answer(f'Незнаю, что вам ответить на этот текст!\n Могу его только повторить {message.text}')
