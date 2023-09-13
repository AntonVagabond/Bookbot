import json
from dataclasses import dataclass

import psycopg2
from psycopg2.extensions import connection

from config_data.config import (
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
)


@dataclass
class BaseQueryMixin:
    conn: connection

    def get_row_by_query(self, query: str, values: tuple = None) -> tuple:
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            result: tuple = cursor.fetchone()
        return result if result else (None,)

    def execute_query_and_commit(self, query: str, values: tuple = None) -> None:
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            self.conn.commit()


class UserInterface(BaseQueryMixin):

    def _exists(self, user_id: int) -> bool:
        query: str = "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s);"
        values: tuple = (user_id,)
        result: tuple = self.get_row_by_query(query, values)
        return result[0]

    def create_if_not_exists(
            self,
            user_id: int,
            current_page: int,
            current_book: int | None,
            books: list,
            book_marks: dict
    ) -> None:
        if not self._exists(user_id):
            query: str = '''
            INSERT INTO users
            (user_id, current_page, current_book, books, book_marks)
            VALUES (%s, %s, %s, %s, %s);
            '''
            books_str: str = "{" + ",".join(map(str, books)) + "}"
            books_marks_json: str = json.dumps(book_marks)
            values: tuple = (user_id, current_page, current_book, books_str, books_marks_json)

            self.execute_query_and_commit(query, values)

    def book_exists(self, user_id: int, book_name: str) -> bool:
        return book_name in self.get_books(user_id)

    def get_books(self, user_id: int) -> list:
        query: str = """
        SELECT name FROM books 
        WHERE id = ANY(SELECT unnest(books)
        FROM users
        WHERE user_id = %s);
        """
        values: tuple = (user_id,)

        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchall()

        book_names: list = [row[0] for row in result]
        return book_names

    def get_current_book(self, user_id: int) -> str | None:
        query: str = """
        SELECT current_book
        FROM users WHERE user_id = %s;
        """
        values: tuple = (user_id,)
        result: tuple = self.get_row_by_query(query, values)
        book_id = result[0]

        if book_id:
            query2: str = """
            SELECT name
            FROM books
            WHERE id = %s;
            """
            values2: tuple = (book_id,)
            result2: tuple = self.get_row_by_query(query2, values2)

            return result2[0]

    def _get_book_id_by_name(self, user_id: int, book_name: str) -> int:
        query: str = """
        SELECT id
        FROM books
        WHERE name = %s;
        """
        values: tuple = (book_name,)
        result: tuple = self.get_row_by_query(query, values)
        book_id = result[0]
        return book_id

    def remove_book(self, user_id: int, book_name: str) -> None:
        book_id: int = self._get_book_id_by_name(user_id, book_name)
        query: str = '''
        UPDATE users
        SET books = array_remove(books, %s),
            current_book = CASE
                                WHEN current_book = %s THEN 1
                                ELSE current_book
                           END
        WHERE user_id = %s;
        '''
        values: tuple = (book_id, book_id, user_id)
        self.execute_query_and_commit(query, values)

        query2: str = "DELETE FROM books WHERE id = %s;"
        values2: tuple = (book_id,)
        self.execute_query_and_commit(query2, values2)

    def set_current_book(self, user_id: int, book_name: str) -> None:
        book_id: int = self._get_book_id_by_name(user_id, book_name)
        query: str = '''
        UPDATE users
        SET current_book = %s
        WHERE user_id = %s;
        '''
        values: tuple = (book_id, user_id)
        self.execute_query_and_commit(query, values)

    def get_current_page(self, user_id: int) -> int:
        query: str = """
        SELECT current_page
        FROM users
        WHERE user_id = %s;
        """
        values: tuple = (user_id,)
        result = self.get_row_by_query(query, values)
        return result[0]

    def set_current_page(self, user_id: int, page: int) -> None:
        query: str = """
        UPDATE users
        SET current_page = %s
        WHERE user_id = %s;
        """
        values: tuple = (page, user_id)
        self.execute_query_and_commit(query, values)













