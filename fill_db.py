from database import DBManager
from headhunter import HeadHunter
from logger_config import db_logger
from utils import get_company_list

if __name__ == '__main__':
    hh = HeadHunter()

    # Получаем список интересующих нас компаний
    company_list = get_company_list(path_to_file='data/companies.txt')

    with DBManager(config_file_path='data/db_config.ini') as db:

        # Создаём таблицы в БД, если они ещё не созданы
        db.create_tables(path_to_create_tables='data/create_tables.sql')

        # Проверяем есть ли компания из списка компаний в БД.
        # Если нет, добавляем её в БД.
        for company in company_list:
            if db.query_execute(
                    query=db.query_manager.queries.get('check_record_exists_in_companies_table'),
                    params=(company,),
                    fetchone=True
            ):
                db_logger.debug(f'В таблице companies уже существует запись с company_name = {company}')
            else:
                db.query_execute(
                    query=db.query_manager.queries.get('add_record_to_companies_table'),
                    params=(hh.get_employer_id(employer_name=company), company),
                    commit=True
                )

        # Получаем список id компаний из БД
        company_ids = db.query_execute(
            query=db.query_manager.queries.get('get_company_ids'),
            fetchall=True
        )

        # Для каждой компании получаем список вакансий
        for company_id in company_ids:
            vacancy_list = hh.get_vacancies_by_employer_id(employer_id=company_id[0])

            # Проверяем есть ли вакансия из списка в БД.
            # Если нет, добавляем её в БД.
            for vacancy_data in vacancy_list:
                vacancy_id = vacancy_data[0]
                if db.query_execute(
                        query=db.query_manager.queries.get('check_record_exists_in_vacancies_table'),
                        params=(vacancy_id,),
                        fetchone=True
                ):
                    db_logger.debug(f'В таблице vacancies уже существует запись с vacancy_id = {vacancy_id}')
                else:
                    db.query_execute(
                        query=db.query_manager.queries.get('add_record_to_vacancies_table'),
                        params=vacancy_data,
                        commit=True
                    )
