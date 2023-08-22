from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery


# Проверка страницы на нажатие кнопки с закладкой
class IsDigitCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data.isdigit()


# Этот класс реагирует на кнопки с закладкой для их удаления
class IsDelBookmarkCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data.endswith('del') and callback.data[:-3].isdigit()
