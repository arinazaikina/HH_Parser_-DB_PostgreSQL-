import configparser
from typing import List

import psycopg2

from logger_config import db_logger
from queries_manager import QueryManager


class DBManager:
    """
    Базовый класс, описывающий базу данных
    Args:
        config_file_path (str): путь к конфигурационному файлу
    """

    def __init__(self, config_file_path: str) -> None:

        db_config = configparser.ConfigParser()
        db_config.read(filenames=config_file_path)

        self.dbname = db_config.get(section='database', option='dbname')
        self.user = db_config.get(section='database', option='user')
        self.password = db_config.get(section='database', option='password')
        self.host = db_config.get(section='database', option='host')
        self.port = db_config.get(section='database', option='port')
        self.path_to_queries = db_config.get(section='database', option='queries')
        self.connection = None
        self.cursor = None
        self.query_manager = QueryManager(path_to_file_with_queries=self.path_to_queries)

    def __enter__(self) -> 'DBManager':
        """
        Устанавливает соединение с БД и возвращает экземпляр класса
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Закрывает соединение с БД
        """
        self.close_connection()

    def connect(self) -> None:
        """
        Открывает соединение с БД
        """
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            db_logger.info('Успешное подключение к БД')

        except psycopg2.OperationalError as error:
            db_logger.exception(f'Не удалось подключиться к базе данных: {error}')
            raise Exception(f'Не удалось подключиться к базе данных: {error}')

    def close_connection(self) -> None:
        """
        Закрывает соединение с БД
        """
        if self.cursor:
            self.cursor.close()
            db_logger.info('Курсор закрыт')
        if self.connection:
            self.connection.close()
            db_logger.info('Соединение с БД закрыто')

    def query_execute(self, query: str, params=None, fetchall=False, fetchmany=None, fetchone=False, commit=False):
        """
        Выполняет переданный SQL-запрос к базе данных.
        Возвращает результат выполнения запроса.
        :param query: SQL запрос
        :param params: параметры SQL запроса (по умолчанию None)
        :param fetchall: вернуть все строки результата (по умолчанию False)
        :param fetchmany: вернуть несколько строк результата (по умолчанию None)
        :param fetchone: вернуть только одну строку результата (по умолчанию False)
        :param commit: выполнить коммит транзакции после выполнения запроса
        (False - изменения не будут сохранены, True - изменения в базе данных будут сохранены, по умолчанию False)
        """

        try:
            self.cursor.execute(query, params)

            if commit:
                self.connection.commit()
            if fetchone:
                result = self.cursor.fetchone()[0]
            elif fetchall:
                result = self.cursor.fetchall()
            elif fetchmany is not None:
                result = self.cursor.fetchmany(size=fetchmany)
            else:
                result = None

            db_logger.debug(f'Выполнен запрос {query} с параметрами {params}')
            return result

        except psycopg2.Error as error:
            db_logger.exception(f'Ошибка выполнения запроса: {error}')
            raise Exception(f'Ошибка выполнения запроса: {error}')

    def create_tables(self, path_to_create_tables: str) -> None:
        """
        Создаёт таблицы в БД, используя SQL-скрипт, путь до которого
        передаётся в качестве параметра.
        :param path_to_create_tables: путь до SQL-скрипта
        """
        try:
            with open(path_to_create_tables, 'r') as file:
                content = file.read()
                self.cursor.execute(content)
                self.connection.commit()
                db_logger.info(f'Запросы из файла {path_to_create_tables} выполнены')
        except Exception as error:
            self.connection.rollback()
            db_logger.exception(f'Ошибка при создании таблиц: {error}')
            raise Exception(f'Ошибка при создании таблиц: {error}')

    def get_companies_and_vacancies_count(self) -> List[tuple]:
        """
        Возвращает список всех компаний и количество вакансий у каждой компании
        """
        result = self.query_execute(
            query=self.query_manager.queries.get(self.get_companies_and_vacancies_count.__name__),
            fetchall=True
        )
        return result

    def get_all_vacancies(self) -> List[tuple]:
        """
        Возвращает список всех вакансий с указанием названия компании, названия вакансии,
        зарплаты, ссылки на вакансию и города.
        """
        result = self.query_execute(
            query=self.query_manager.queries.get(self.get_all_vacancies.__name__),
            fetchall=True
        )
        return result

    def get_avg_salary(self) -> int:
        """
        Возвращает среднюю зарплату по вакансиям
        """
        result = self.query_execute(
            query=self.query_manager.queries.get(self.get_avg_salary.__name__),
            fetchone=True
        )
        return result

    def get_vacancies_with_higher_salary(self) -> List[tuple]:
        """
        Возвращает список всех вакансий, у которых зарплата выше средней по вакансиям
        """
        result = self.query_execute(
            query=self.query_manager.queries.get(self.get_vacancies_with_higher_salary.__name__),
            fetchall=True
        )
        return result

    def get_vacancies_with_keyword(self, keyword: str) -> List[tuple]:
        """
        Возвращает список всех вакансий, в названии которых содержатся
        переданные в метод слова
        :param keyword: ключевое слово
        """
        result = self.query_execute(
            query=self.query_manager.queries.get(self.get_vacancies_with_keyword.__name__),
            params=(f'%{keyword}%',),
            fetchall=True
        )
        return result
