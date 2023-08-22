import os
import sys
import re
import itertools

BOOK_PATH = 'book/book.txt'
PAGE_SIZE = 1050

book: dict[int, str] = {}


# Функция, возвращающая строку с текстом страницы и ее размер
def _get_part_text(text: str, start: int, size: int) -> tuple[str, int]:
    filter_one: str = re.sub(r'[.,!?:;]\.+$', '', text[start:start + size])
    filter_two: list[str] = re.findall(r'(?s).+[.,!?:;]', filter_one)

    # убирает лишние \n
    filter_three: str = re.sub(r'\n(?! {4})', '0', filter_two[0])
    return filter_three, len(filter_three)


# Функция, формирующая словарь книги
def prepare_book(path: str) -> None:
    # Открываем файл
    with open(path, 'r', encoding='utf-8') as file:
        text: str = file.read()

    # Количество символов в тексте
    all_size: int = len(text)

    # С какого места будет начинаться новая страница
    start: int = 0
    for page in itertools.count(start=1):
        if all_size <= 0:
            break
        page_content, page_size = _get_part_text(text=text, start=start, size=PAGE_SIZE)
        book[page] = page_content.lstrip()
        all_size -= page_size
        start += page_size


# Вызов функции prepare_book для подготовки книги из текстового файла
prepare_book(os.path.join(sys.path[0], os.path.normpath(BOOK_PATH)))
