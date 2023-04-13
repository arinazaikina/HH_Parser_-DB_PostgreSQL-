-- create_table_companies
CREATE TABLE IF NOT EXISTS companies (
    company_id INT PRIMARY KEY,
    company_name VARCHAR(250) UNIQUE
);

-- create_table_vacancies
CREATE TABLE  IF NOT EXISTS vacancies(
    vacancy_id INT PRIMARY KEY,
    vacancy_name VARCHAR(250) NOT NULL,
    vacancy_url VARCHAR(250) NOT NULL,
    salary INT NOT NULL,
    city VARCHAR(100) NOT NULL,
    published_date DATE NOT NULL,
    company_id INT REFERENCES companies(company_id)

    CONSTRAINT check_salary CHECK ( salary > 0 )

);
