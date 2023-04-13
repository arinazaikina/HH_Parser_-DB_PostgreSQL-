from abc import ABC, abstractmethod
from datetime import date
from typing import List

import requests
from requests.exceptions import RequestException

from logger_config import hh_logger


class HeadHunterBase(ABC):
    """
    Абстрактный базовый класс для работы с сервисом поиска работы HeadHunter
    Attrs:
        BASE_URL (str): базовый URL-адрес для запросов к API HeadHunter.
        DEFAULT_PARAMS (dict): параметры по умолчанию, используемые в каждом запросе.
    """

    BASE_URL = 'https://api.hh.ru'
    DEFAULT_PARAMS = {'area': '113'}

    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """
        Создает запрос к API HeadHunter и возвращает JSON-ответ
        :param endpoint: конечная точка API HeadHunter
        :param params: параметры запроса
        """
        url = f'{self.BASE_URL}/{endpoint}'
        all_params = {**self.DEFAULT_PARAMS, **(params or {})}

        try:
            response = requests.get(url=url, params=all_params)
            if response.status_code != 200:
                hh_logger.exception(f'Статус код {response.status_code}')
                raise LookupError(f'Статус код {response.status_code}')
            return response.json()
        except (RequestException, LookupError) as error:
            hh_logger.error(f'Не могу получить данные: {error}')
            return {}

    @abstractmethod
    def get_employer_id(self, employer_name: str) -> int:
        """
        Возвращает идентификатор работодателя по его наименованию
        :param employer_name: наименование работодателя
        """
        pass

    @abstractmethod
    def get_vacancy_data(self, employer_id: int, unformatted_data: dict) -> tuple:
        """
        Возвращает отформатированные данные по вакансии
        :param employer_id: идентификатор работодателя
        :param unformatted_data: неформатированные данные по вакансии
        """
        pass

    @abstractmethod
    def get_vacancies_by_employer_id(self, employer_id: int) -> List[tuple]:
        """
        Возвращает список вакансии работодателя
        :param employer_id: идентификатор работодателя
        """
        pass


class HeadHunter(HeadHunterBase):
    """
    Дочерний класс, описывающий сервис поиска работы HeadHunter.
    Базовый класс: HeadHunterBase
    """

    def get_employer_id(self, employer_name: str) -> int:
        endpoint = 'employers'
        params = {
            'text': employer_name,
            'only_with_vacancies': True,
            'per_page': 100
        }
        response = self._make_request(endpoint=endpoint, params=params)

        if response:
            companies = response.get('items')

            if companies:
                company_id = companies[0].get('id')
                hh_logger.debug(f'Для компании {employer_name} получен ID = {company_id}')

                return int(company_id)

    @staticmethod
    def _get_formatted_id(unformatted_data: dict) -> int:
        """
        Возвращает id вакансии
        :param unformatted_data: неформатированные данные по вакансии
        """
        vacancy_id = unformatted_data.get('id')
        if vacancy_id:
            return int(vacancy_id)

    @staticmethod
    def _get_formatted_name(unformatted_data: dict) -> str:
        """
        Возвращает название вакансии
        :param unformatted_data: неформатированные данные по вакансии
        """
        return unformatted_data.get('name')

    @staticmethod
    def _get_formatted_url(unformatted_data: dict) -> str:
        """
        Возвращает ссылку на вакансию
        :param unformatted_data: неформатированные данные по вакансии
        """
        return unformatted_data.get('alternate_url')

    @staticmethod
    def _get_formatted_salary(unformatted_data: dict) -> int:
        """
        Возвращает заработную плату, указанную в вакансии
        :param unformatted_data: неформатированные данные по вакансии
        """
        salary_data = unformatted_data.get('salary')
        if salary_data.get('from') is None:
            return salary_data.get('to')
        return salary_data.get('from')

    @staticmethod
    def _get_formatted_city(unformatted_data: dict) -> str:
        """
        Возвращает город, указанный в вакансии
        :param unformatted_data: неформатированные данные по вакансии
        """
        return unformatted_data.get('area', {}).get('name')

    @staticmethod
    def _get_formatted_published_date(unformatted_data: dict) -> date:
        """
        Возвращает дату публикации вакансии
        :param unformatted_data: неформатированные данные по вакансии
        """
        date_str = unformatted_data.get('published_at')
        date_obj = date_str.split('T')[0]
        return date.fromisoformat(date_obj)

    def get_vacancy_data(self, employer_id: str, unformatted_data: dict) -> tuple:
        vacancy_data = (
            self._get_formatted_id(unformatted_data),
            self._get_formatted_name(unformatted_data),
            self._get_formatted_url(unformatted_data),
            self._get_formatted_salary(unformatted_data),
            self._get_formatted_city(unformatted_data),
            self._get_formatted_published_date(unformatted_data),
            employer_id
        )
        hh_logger.debug(f'Получены отформатированные данные по вакансии {vacancy_data}')
        return vacancy_data

    def get_vacancies_by_employer_id(self, employer_id: str) -> List[tuple]:
        vacancy_list = []
        page = 0

        while True:
            endpoint = 'vacancies'
            params = {
                'per_page': 100,
                'employer_id': employer_id,
                'only_with_salary': True,
                'vacancy_type': 'open',
                'page': page
            }
            hh_logger.debug(f'Страница #{page}')
            response = self._make_request(endpoint=endpoint, params=params)
            for item in response.get('items'):
                vacancy_list.append(self.get_vacancy_data(employer_id=employer_id, unformatted_data=item))

            if response.get('pages') - page <= 1:
                hh_logger.debug(f'Количество найденных вакансий: {len(vacancy_list)}')
                break
            else:
                page += 1

        return vacancy_list
