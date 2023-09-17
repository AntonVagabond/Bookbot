from aiogram import F, Router
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup

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
    create_edit_bookmarks_keyboard,
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
            reply_markup=create_books_keyboard(*user_books)
        )
    else:
        await message.answer(LEXICON['no_books'])


# This handler will trigger the command "/bookmarks"
# and send the user a list of saved bookmarks,
# if there are any or a message that there are no bookmarks
@router.message(Command(commands='bookmarks'))
async def process_bookmarks_command(message: Message) -> None:
    user_book: str | None = db.user_interface.get_current_book(message.from_user.id)
    book_marks: dict = db.user_interface.get_book_marks(message.from_user.id)
    if book_marks:
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=create_bookmarks_keyboard(
                user_book,
                *book_marks[user_book]
            )
        )
    else:
        await message.answer(text=LEXICON['no_bookmarks'])


# This handler will trigger the command "/continue"
# and send the user the page of the book on which the user
# stopped in the process of interacting with the bot
@router.message(Command(commands='continue'))
async def process_continue_command(message: Message) -> None:
    user_book: str | None = db.user_interface.get_current_book(message.from_user.id)
    user_page: int = db.user_interface.get_current_page(message.from_user.id)
    text: str = db.book_interface.get_page_content(user_book, user_page)
    book_length: int = db.book_interface.get_length(user_book)
    print('continue')
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard(
            'backward',
            f'{user_page}/{book_length}',
            'forward',
        )
    )


# This handler will be triggered by pressing the inline button
# to save the book
@router.message(F.document)
async def process_load_book(message: Message) -> None:
    print('f.document')
    if message.document.mime_type == 'text/plain':
        book_name: str = message.caption or pretty_name(message.document.file_name)
        beautiful_name: str = f'📖 {book_name}'
        if db.user_interface.book_exists(message.from_user.id, book_name):
            answer: str = LEXICON['book_exists']
        else:
            text = get_file_text_from_server(message.document.file_id)
            try:
                content: str = prepare_book(text)
                db.user_interface.save_book(message.from_user.id, book_name, content)
                answer: str = f'Книга успешно сохранена под именем "{book_name}"'
            except BadBookError:
                answer: str = LEXICON['cant_parse']
    else:
        answer = LEXICON['miss_message']

    await message.answer(answer)


@router.callback_query(IsBookCallbackData())
async def process_book_press(callback: CallbackQuery, user_book: str) -> None:
    print('Is_bookCallback')
    db.user_interface.set_current_book(callback.from_user.id, user_book)
    db.user_interface.set_current_page(callback.from_user.id, 1)
    text: str = db.book_interface.get_page_content(user_book, 1)
    book_length: int = db.book_interface.get_length(user_book)
    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard(
            'backward',
            f'1/{book_length}',
            'forward',
        )
    )


@router.callback_query(EditItemsCallbackFactory.filter(F.item_type == 'books'))
async def process_edit_books_press(callback: CallbackQuery) -> None:
    user_books: list = db.user_interface.get_books(callback.from_user.id)
    print('books_filter')
    if len(user_books) > 1:
        answer: str = LEXICON['edit']
        await callback.message.edit_text(
            text=LEXICON[callback.data],
            reply_markup=create_edit_books_keyboard(*user_books),
        )
    else:
        answer: str = LEXICON['no_books_to_delete']

    await callback.answer(answer)


@router.callback_query(Text(text='cancel_edit_book'))
async def process_edit_books_press(callback: CallbackQuery) -> None:
    users_books: list = db.user_interface.get_books(callback.from_user.id)
    await callback.message.edit_text(
        text=LEXICON['/books'],
        reply_markup=create_books_keyboard(*users_books)
    )


@router.callback_query(IsDelBookmarkCallbackData())
async def process_del_book_press(callback: CallbackQuery, user_book: str) -> None:
    db.user_interface.remove_book(callback.from_user.id, user_book)
    user_books: list = db.user_interface.get_books(callback.from_user.id)
    reply_markup: InlineKeyboardMarkup = create_books_keyboard(*user_books)
    if len(user_books) > 1:
        text: str = LEXICON['edit_books']
        answer: str = LEXICON['delete_book']
    else:
        text: str = LEXICON['/books']
        answer: str = LEXICON['no_books_to_delete']

    await callback.message.edit_text(text=text, reply_markup=reply_markup)
    await callback.answer(answer)


# This handler will be triggered by pressing the inline "forward" button
# during the user's interaction with the message-book
@router.callback_query(Text(text='forward'))
async def process_forward_press(callback: CallbackQuery) -> None:
    user_page: int = db.user_interface.get_current_page(callback.from_user.id)
    user_book: str | None = db.user_interface.get_current_book(callback.from_user.id)
    book_length: int = db.book_interface.get_length(user_book)

    next_page: int = user_page + 1
    if user_page == book_length:
        next_page = 1
    db.user_interface.set_current_page(callback.from_user.id, next_page)
    text: str = db.book_interface.get_page_content(user_book, next_page)

    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard(
            'backward',
            f'{next_page}/{book_length}',
            'forward',
        )
    )


# This handler will be triggered by pressing the inline "back" button
# during the user's interaction with the message-book
@router.callback_query(Text(text='backward'))
async def process_backward_press(callback: CallbackQuery) -> None:
    user_page: int = db.user_interface.get_current_page(callback.from_user.id)
    user_book: str | None = db.user_interface.get_current_book(callback.from_user.id)
    book_length: int = db.book_interface.get_length(user_book)

    next_page: int = user_page - 1
    if user_page == 0:
        next_page = book_length
    db.user_interface.set_current_page(callback.from_user.id, next_page)
    text: str = db.book_interface.get_page_content(user_book, next_page)

    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard(
            'backward',
            f'{next_page}/{book_length}',
            'forward',
        )
    )


# This handler will be triggered when the inline button is pressed
# with the current page number and bookmark the current page
@router.callback_query(IsAddToBookMarksCallbackData())
async def process_page_press(callback: CallbackQuery) -> None:
    user_page: int = db.user_interface.get_current_page(callback.from_user.id)
    user_book: str | None = db.user_interface.get_current_book(callback.from_user.id)
    db.user_interface.add_book_mark(callback.from_user.id, user_book, user_page)
    print('add bookmark')
    await callback.answer(f'Страница {user_page} добавлена в закладки!')


@router.callback_query(EditItemsCallbackFactory.filter(F.item_type == 'bookmarks'))
async def process_edit_bookmarks_press(callback: CallbackQuery) -> None:
    user_book: str | None = db.user_interface.get_current_book(callback.from_user.id)
    book_marks: dict = db.user_interface.get_book_marks(callback.from_user.id)
    print(callback.data)
    print(LEXICON)
    await callback.message.edit_text(
        text=LEXICON[callback.data],
        reply_markup=create_edit_bookmarks_keyboard(user_book, *book_marks[user_book])
    )
    await callback.answer()


@router.callback_query(IsBookmarkCallbackData())
async def process_bookmark_press(callback: CallbackQuery, page: int) -> None:
    user_book: str | None = db.user_interface.get_current_book(callback.from_user.id)
    text: str = db.book_interface.get_page_content(user_book, page)
    book_length: int = db.book_interface.get_length(user_book)
    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard(
            'backward',
            f'{page}/{book_length}',
            'forward',
        )
    )
    await callback.answer()


# This handler will be triggered when the inline button is pressed
# "cancel" while working with the bookmarks list (viewing and editing)
@router.callback_query(Text(text='cancel'))
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON['cancel_text'])
    await callback.answer()


# This handler will be triggered when the inline button is pressed
# with a bookmark from the bookmarks list to delete
@router.callback_query(IsDelBookmarkCallbackData())
async def process_del_bookmark_press(callback: CallbackQuery, page: int) -> None:
    user_book: str | None = db.user_interface.get_current_book(callback.from_user.id)
    db.user_interface.remove_book_mark(callback.from_user.id, user_book, page)
    book_marks: dict = db.user_interface.get_book_marks(callback.from_user.id)
    if book_marks:
        await callback.message.edit_text(
            text=LEXICON['edit_bookmarks'],
            reply_markup=create_edit_bookmarks_keyboard(
                user_book,
                *book_marks[user_book],
            )
        )
    else:
        await callback.message.edit_text(text=LEXICON['no_bookmarks'])
    await callback.answer()
