import json
import re

import requests
import itertools as it

from config_data.config import BOT_TOKEN
from errors.error import BadBookError
from typing import Any

PAGE_SIZE = 1050


# A function that returns a string with the page text and its size
def _get_part_text(text: str, start: int, page_size: int) -> tuple[str, int] | None:
    # we use HTML parse mode in our bot, so we need to edit some symbols

    for old, new in zip(('<', '>', '&'), ('&lt', '&gt', '&amp')):
        text: str = text.replace(old, new)
    end: int = start + page_size
    if end >= len(text):
        return text[start:], len(text) - start

    for i in range(end - 1, start - 1, -1):
        if text[i] in ",.!:;?":
            return text[start:i + 1], i + 1 - start

    raise BadBookError()


# The function that forms the dictionary of the book
def prepare_book(text: str) -> str:
    content: dict = {}

    text_length: int = len(text)

    # Page Start
    cur_idx: int = 0
    for page in it.count(start=1):
        if text_length <= 0:
            break
        page_text, page_length = _get_part_text(text=text, start=cur_idx, page_size=PAGE_SIZE)
        content[page] = page_text.lstrip()
        text_length -= page_length
        cur_idx += page_length

    return json.dumps(content)


def get_file_text_from_server(file_id: str) -> str:
    file_info_url: str = f'https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}'
    response: requests = requests.get(file_info_url)
    file_info: dict = response.json()
    file_path: str = file_info['result']['file_path']
    file_url: str = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}'
    response = requests.get(file_url)
    return response.text


def pretty_name(name: str) -> str:
    name: str = name.replace('.txt', '')
    pretty: str = re.sub(r'\W', '_', name.lower())
    pretty: str = re.sub(r'_+', '_', pretty)
    return pretty[:35]
