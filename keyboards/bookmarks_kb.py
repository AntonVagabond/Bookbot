from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callback_factories.edit_items import EditItemsCallbackFactory
from database.database import bot_database as db
from lexicon.lexicon import LEXICON


# Функция генерации списка заклодок
def create_bookmarks_keyboard(book_name: str, *args: int) -> InlineKeyboardMarkup:
    # Создаем объект клавиатуры
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    # Наполняем клавиатуру кнопками-закладками в порядке возрастания
    for button in sorted(set(args)):
        kb_builder.row(
            InlineKeyboardButton(
                text=f'{button} - {db.book_interface.get_page_content(book_name, button)[:100]}',
                callback_data=f'{button}#$%bookmark#$%'
            )
        )

    # Добавляем в клавиатуру в конце две кнопки "Редактировать" и "Отменить"
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON['edit_button'],
            callback_data=EditItemsCallbackFactory(item_type='bookmarks').pack()
        ),
        InlineKeyboardButton(
            text=LEXICON['cancel'],
            callback_data='cancel'
        ),
        width=2
    )
    return kb_builder.as_markup()


# Функция для генерации списка закладок к удалению
def create_edit_keyboard(book_name: str, *args: int) -> InlineKeyboardMarkup:
    # Создаем объект клавиатуры
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    # Наполняем клавиатуру кнопками-закладками в порядке возрастания
    for button in sorted(args):
        kb_builder.row(
            InlineKeyboardButton(
                text=f"""{LEXICON["del"]} {button} - {db.book_interface.get_page_content(
                    book_name,
                    button[:100]
                )}""",
                callback_data=f'{button}del'
            )
        )

    # Добавляем в конец клавиатуры кнопку "Отменить"
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON['cancel'],
            callback_data='cancel'
        )
    )
    return kb_builder.as_markup()
