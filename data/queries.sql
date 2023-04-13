-- add_record_to_companies_table
INSERT INTO companies (company_id, company_name) VALUES (%s, %s);

-- add_record_to_vacancies_table
INSERT INTO vacancies (vacancy_id, vacancy_name, vacancy_url, salary, city, published_date, company_id)
VALUES (%s, %s, %s, %s, %s, %s, %s);

-- check_record_exists_in_companies_table
SELECT EXISTS(SELECT 1 FROM companies WHERE company_name = %s);

-- check_record_exists_in_vacancies_table
SELECT EXISTS(SELECT 1 FROM vacancies WHERE vacancy_id = %s);

-- get_company_ids
SELECT company_id
FROM companies;

-- get_companies_and_vacancies_count
SELECT company_name, COUNT(*) AS amount_vacancies
FROM vacancies
LEFT JOIN companies USING (company_id)
GROUP BY company_name
ORDER BY amount_vacancies DESC;

-- get_all_vacancies
SELECT companies.company_name, vacancies.vacancy_name, vacancies.salary, vacancies.vacancy_url, vacancies.city
FROM vacancies
JOIN companies USING (company_id);

-- get_avg_salary
SELECT ROUND(AVG(salary)) as avg_salary
FROM vacancies;

-- get_vacancies_with_higher_salary
SELECT *
FROM vacancies
WHERE salary > (
    SELECT AVG(salary)
    FROM vacancies
    );

-- get_vacancies_with_keyword
SELECT *
FROM vacancies
WHERE vacancy_name
LIKE %s;
