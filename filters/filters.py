from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery


# Checking for adding a page to bookmarks
class IsAddToBookMarksCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return '/' in callback.data and callback.data.replace('/', '').isdigit()


# Checking for a book
class IsBookCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> dict[str, str] | bool:
        if isinstance(callback.data, str) and '#$%book#$%' in callback.data:
            book_name: str = callback.data[:-10]
            return {'user_book': book_name}
        return False


# Checking the book for clicking the delete button
class IsDelBookCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> dict[str, str] | bool:
        if isinstance(callback.data, str) and '#$%delbook#$%' in callback.data:
            book_name: str = callback.data[:-13]
            return {'user_book': book_name}
        return False


# Checking the page for clicking the bookmark button
class IsBookmarkCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> dict[str, int] | bool:
        if isinstance(callback.data, str) and '#$%bookmark#$%' in callback.data:
            page: int = int(callback.data[:-14])
            return {'page': page}
        return False


# This class reacts to bookmark buttons to delete them
class IsDelBookmarkCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> dict[str, int] | bool:
        if isinstance(callback.data, str) and '#$%delbookmark#$%' in callback.data \
                and callback.data[:-17].isdigit():
            page: int = int(callback.data[:-17])
            return {'page': page}
        return False
