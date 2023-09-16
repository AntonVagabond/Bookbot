from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callback_factories.edit_items import EditItemsCallbackFactory
from database.database import bot_database as db
from lexicon.lexicon import LEXICON


# Bookmark list generation function
def create_bookmarks_keyboard(book_name: str, *args: int) -> InlineKeyboardMarkup:
    # Creating a keyboard object
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    # Fill the keyboard with bookmark buttons in ascending order
    for button in sorted(set(args)):
        kb_builder.row(
            InlineKeyboardButton(
                text=f'{button} - {db.book_interface.get_page_content(book_name, button)[:100]}',
                callback_data=f'{button}#$%bookmark#$%'
            )
        )

    # Add two "Edit" and "Cancel" buttons to the keyboard at the end
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


# Function for generating a list of bookmarks to delete
def create_edit_bookmarks_keyboard(book_name: str, *args: int) -> InlineKeyboardMarkup:
    # Creating a keyboard object
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    # Fill the keyboard with bookmark buttons in ascending order
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

    # Add the "Cancel" button to the end of the keyboard
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON['cancel'],
            callback_data='cancel'
        )
    )
    return kb_builder.as_markup()
