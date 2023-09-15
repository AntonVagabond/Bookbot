from aiogram import F, Router
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message

from callback_factories.edit_items import EditItemsCallbackFactory
from database.database import bot_database as db
from filters.filters import (
    IsAddToBookMarksCallbackData,
    IsBookCallbackData,
    IsDelBookCallbackData,
    IsBookmarkCallbackData,
    IsDelBookmarkCallbackData,
)
from keyboards.bookmarks_kb import (
    create_bookmarks_keyboard,
    create_edit_keyboard,
)
from keyboards.book_kb import (
    create_books_keyboard,
    create_edit_books_keyboard,
)
from keyboards.pagination_kb import create_pagination_keyboard
from lexicon.lexicon import LEXICON
from services.file_handling import (
    get_file_text_from_server,
    prepare_book,
    pretty_name,
)
from errors.error import BadBookError

router: Router = Router()


# This handler will be triggered by the command "/start" -
# add the user to the database if he was not there yet
# and send him a welcome message
@router.message(CommandStart())
async def process_start_command(message: Message) -> None:
    db.user_interface.create_if_not_exists(
        user_id=message.from_user.id,
        current_page=1,
        current_book=1,
        books=[1],
        book_marks={}
    )
    await message.answer(LEXICON[message.text])


# This handler will trigger the "/help" command
# and send the user a message with a list of available commands in the bot
@router.message(Command(commands='help'))
async def process_help_command(message: Message) -> None:
    await message.answer(LEXICON[message.text])


# This handler will trigger the "/books" command
# and send the user a message with a list of available books in the bot
@router.message(Command(commands='books'))
async def process_books_command(message: Message) -> None:
    user_books: list = db.user_interface.get_books(message.from_user.id)
    if user_books:
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=create_pagination_keyboard(*user_books)
        )
    else:
        await message.answer(LEXICON['no_books'])


@router.message(Command(commands='bookmarks'))
async def process_bookmarks_command(message: Message) -> None:
    user_book: str | None = db.user_interface.get_current_book(message.from_user.id)
    book_marks: dict = db.user_interface.get_book_marks(message.from_user.id)
    if book_marks:
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=create_pagination_keyboard(
                user_book,
                *book_marks[user_book]
            )
        )
    else:
        await message.answer(text=LEXICON['no_bookmarks'])


# Этот хэндлер будет срабатывать на команду "/continue"
# и отправлять пользователю страницу книги, на которой пользователь
# остановился в процессе взаимодействия с ботом
@router.message(Command(commands='continue'))
async def process_continue_command(message: Message) -> None:
    user_book: str | None = db.user_interface.get_current_book(message.from_user.id)
    user_page: int = db.user_interface.get_current_page(message.from_user.id)
    text: str = db.book_interface.get_page_content(user_book, user_page)
    book_length: int = db.book_interface.get_length(user_book)
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard(
            'backward',
            f'{user_page}/{book_length}',
            'forward',
        )
    )


# Этот хэндлер будет срабатывать на команду "/bookmarks"
# и отправлять пользователю список сохраненных закладок,
# если они есть или сообщение о том, что закладок нет
@router.message(Command(commands='bookmarks'))
async def process_bookmarks_command(message: Message):
    if users_db[message.from_user.id]["bookmarks"]:
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=create_bookmarks_keyboard(
                *users_db[message.from_user.id]["bookmarks"]))
    else:
        await message.answer(text=LEXICON['no_bookmarks'])


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
# во время взаимодействия пользователя с сообщением-книгой
@router.callback_query(F.data == 'forward')
async def process_forward_press(callback: CallbackQuery):
    if users_db[callback.from_user.id]['page'] < len(book):
        users_db[callback.from_user.id]['page'] += 1
        text = book[users_db[callback.from_user.id]['page']]
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                'backward',
                f'{users_db[callback.from_user.id]["page"]}/{len(book)}',
                'forward'))
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "назад"
# во время взаимодействия пользователя с сообщением-книгой
@router.callback_query(F.data == 'backward')
async def process_backward_press(callback: CallbackQuery):
    if users_db[callback.from_user.id]['page'] > 1:
        users_db[callback.from_user.id]['page'] -= 1
        text = book[users_db[callback.from_user.id]['page']]
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                'backward',
                f'{users_db[callback.from_user.id]["page"]}/{len(book)}',
                'forward'))
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с номером текущей страницы и добавлять текущую страницу в закладки
@router.callback_query(lambda x: '/' in x.data and x.data.replace('/', '').isdigit())
async def process_page_press(callback: CallbackQuery):
    users_db[callback.from_user.id]['bookmarks'].add(
        users_db[callback.from_user.id]['page'])
    await callback.answer('Страница добавлена в закладки!')


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с закладкой из списка закладок
@router.callback_query(IsDigitCallbackData())
async def process_bookmark_press(callback: CallbackQuery):
    text = book[int(callback.data)]
    users_db[callback.from_user.id]['page'] = int(callback.data)
    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard(
            'backward',
            f'{users_db[callback.from_user.id]["page"]}/{len(book)}',
            'forward'))
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# "редактировать" под списком закладок
@router.callback_query(F.data == 'edit_bookmarks')
async def process_edit_press(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON[callback.data],
        reply_markup=create_edit_keyboard(
            *users_db[callback.from_user.id]["bookmarks"]))
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# "отменить" во время работы со списком закладок (просмотр и редактирование)
@router.callback_query(F.data == 'cancel')
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON['cancel_text'])
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с закладкой из списка закладок к удалению
@router.callback_query(IsDelBookmarkCallbackData())
async def process_del_bookmark_press(callback: CallbackQuery):
    users_db[callback.from_user.id]['bookmarks'].remove(
        int(callback.data[:-3]))
    if users_db[callback.from_user.id]['bookmarks']:
        await callback.message.edit_text(
            text=LEXICON['/bookmarks'],
            reply_markup=create_edit_keyboard(
                *users_db[callback.from_user.id]["bookmarks"]))
    else:
        await callback.message.edit_text(text=LEXICON['no_bookmarks'])
    await callback.answer()
