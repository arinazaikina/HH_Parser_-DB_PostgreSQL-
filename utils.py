from typing import List


def get_company_list(path_to_file: str) -> List[str]:
    """
    Возвращает список компаний из файла
    :param path_to_file: путь к файлу
    """
    data = []
    with open(path_to_file) as file:
        for line in file:
            data.append(line.strip())
        return data
