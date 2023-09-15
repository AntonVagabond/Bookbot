from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon import LEXICON


# A function that generates a keyboard for a book page
def create_pagination_keyboard(*buttons: str) -> InlineKeyboardMarkup:
    # Initializing the builder
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    # Adding a row with buttons to the builder
    kb_builder.row(
        *[
            InlineKeyboardButton(
                text=LEXICON.get(button, button),
                callback_data=button)
            for button in buttons
        ]
    )
    # Returning the inline keyboard object
    return kb_builder.as_markup()
