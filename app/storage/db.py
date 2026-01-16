import psycopg
from psycopg.rows import dict_row

class DB:
    def __init__(self, dsn: str):
        self._dsn = dsn

    def connect(self) -> None:
        # Проверка подключения при старте (быстро и надёжно)
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")

    def conn(self):
        # Контекстный менеджер на соединение
        return psycopg.connect(self._dsn, row_factory=dict_row)
