class QueryManager:
    """
    Базовый класс, описывающий менеджер для работы с SQL-запросами.
    Предоставляет возможность легко получить SQL-запрос по его комментарию
    с помощью словаря queries
    Args:
        path_to_file_with_queries: путь к файлу с SQL-запросами.
    Attrs:
        queries: словарь с запросами
    """

    def __init__(self, path_to_file_with_queries: str) -> None:
        self.path_to_file_with_queries = path_to_file_with_queries
        self.queries = {}
        self._load_queries()

    def _load_queries(self):
        """
        Загружает SQL-запросы из файла в словарь self.queries,
        где ключ - комментарий перед запросом, значение - SQL-запрос.
        """
        with open(self.path_to_file_with_queries, 'r') as file:
            content = file.read()
            blocks = content.split('-- ')

            for block in blocks[1:]:
                lines = block.split('\n')
                comment = lines[0].strip()
                query = ' '.join(lines[1:]).strip()
                self.queries[comment] = query
