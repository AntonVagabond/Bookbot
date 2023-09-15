from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callback_factories.edit_items import EditItemsCallbackFactory
from lexicon.lexicon import LEXICON


# Book list generation function
def create_books_keyboard(*args: str) -> InlineKeyboardMarkup:
    # Creating a keyboard object
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    # We fill the keyboard with buttons-books in ascending order
    for book_name in sorted(args):
        kb_builder.row(
            InlineKeyboardButton(
                text=book_name,
                callback_data=f'{book_name}#$%book#$%'
            )
        )

    # Add two "Edit" and "Cancel" buttons to the keyboard at the end
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON['edit_button'],
            callback_data=EditItemsCallbackFactory(item_type='books').pack()
        ),
        InlineKeyboardButton(
            text=LEXICON['cancel'],
            callback_data='cancel'
        ),
        width=2
    )
    return kb_builder.as_markup()


def create_edit_books_keyboard(*args: str) -> InlineKeyboardMarkup:
    # Creating a keyboard object
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    # We fill the keyboard with buttons-books in ascending order
    for book_name in sorted(args):
        if book_name == '📖 Ray Bradbury `The Martian Chronicles`':
            continue

        kb_builder.row(
            InlineKeyboardButton(
                text=f'{LEXICON["del"]} {book_name}',
                callback_data=f'{book_name}#$%delbook#$%'
            )
        )

    # Add the "Cancel book editing" button to the end of the keyboard
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON['cancel'],
            callback_data='cancel_edit_book'
        )
    )
    return kb_builder.as_markup()
