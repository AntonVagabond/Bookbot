# BookBot - телеграм бот для удобного чтения книг

Этот Telegram-бот позволяет добавлять и удалять книги из собственной библиотеки, а также читать их в удобном виде. Изначально в библиотеке есть одна встроенная книга Рэя Брэдбери "Марсианские Хроники". Чтобы добавить собственную книгу, нужно отправить её в чат в виде текстового файла (.txt).

Читая книгу можно добавлять закладки, нажимая на кнопку текущей страницы. Закладки видны только у текущей книги, чтобы увидеть закладки другой книги, надо начать её читать.

**Команды**:

 - `/start` - запустить бота.
 - `/help` - справка по использованию.
 - `/continue` - продолжить чтение.
 - `/books` - список книг библиотеки.
 - `/bookmarks` - список закладок.

Бот использует базу данных PostgreSQL для хранения своих фраз, книг, команд и пользователей.

# Зависимости 

    Python 3.8+
    aiogram 3.0.* - для использования Telegram Bot API
    psycopg2 2.9.6+ - работа с базой данных
    python-dotenv 1.0.0 - переменные окружения
    requests 2.31.0 - запросы к апи телеграмма

# Установка

1. Клонирование репозитория:

```bash
git clone https://github.com/MaximGudkov/BookBot.git
```

2. Создание виртуального окружения и установка зависимостей:

```bash
python3.8 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
3. Заполнить файл `.env.example` и переименовать его `.env`.

4. Запуск бота.
```python bot.py```

# Полезности

- Обратите внимание, что при каждом запуске бота стираются все данные из базы данных (если были) и заполняются необходимые для работы бота таблицы, это свзано с запуском функции setup_db, которую я создал для удобного создания и заполнения необходимых таблиц. Если при очередном запуске необходимо сохранить данные, следует закомментировать функцию setup_db
bot.py
```pycon
python bot.py

def main():
    ...
    # WARNING: This will delete all existing tables and will
    # re-fill the data for the bot's lexicon. See docstring
    setup_db()
    ...
```
- Чтобы протестировать бота, прикрепляю несколько книг в директорию books/