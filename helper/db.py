#
#  _    ___  ___ ___  _  _ ___ _____    _   _ ___ ___ ___ ___  ___ _____
# | |  / _ \| _ \   \| \| | __|_   _|__| | | / __| __| _ \ _ )/ _ \_   _|
# | |_| (_) |   / |) | .` | _|  | ||___| |_| \__ \ _||   / _ \ (_) || |
# |____\___/|_|_\___/|_|\_|___| |_|     \___/|___/___|_|_\___/\___/ |_|
#
#                            © Copyright 2022
#
#                       https://t.me/lordnet_userbot
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

from json import dumps, loads
from sqlite3 import connect, Row, Cursor, OperationalError
import inspect
from threading import Lock
from helper.cmd import get_module_name


class Database:
    def __init__(self):
        self._conn = connect("lordnet.sqlite3", check_same_thread=False)
        self._conn.row_factory = Row
        self._cursor = self._conn.cursor()
        self._lock = Lock()

    @staticmethod
    def _parse_row(row: Row):
        if row["type"] == "bool":
            return row["val"] == "1"
        elif row["type"] == "int":
            return int(row["val"])
        elif row["type"] == "str":
            return row["val"]
        else:
            return loads(row["val"])

    def __execute(self, module: str, *args, **kwargs) -> Cursor:
        self._lock.acquire()
        try:
            return self._cursor.execute(*args, **kwargs)
        except OperationalError as e:
            if str(e).startswith("no such table"):
                sql = f"""
                CREATE TABLE IF NOT EXISTS '{module}' (
                var TEXT UNIQUE NOT NULL,
                val TEXT NOT NULL,
                type TEXT NOT NULL
                )
                """
                self._cursor.execute(sql)
                self._conn.commit()
                return self._cursor.execute(*args, **kwargs)
            raise e from None
        finally:
            self._lock.release()

    def get(self, variable: str, default=None):
        module = get_module_name(inspect.getmodule(inspect.stack()[1][0]))

        sql = f"SELECT * FROM '{module}' WHERE var=:var"
        cur = self.__execute(module, sql, {"tabl": module, "var": variable})

        row = cur.fetchone()
        if row is None:
            return default
        else:
            return self._parse_row(row)

    def set(self, variable: str, value) -> bool:
        module = get_module_name(inspect.getmodule(inspect.stack()[1][0]))

        sql = f"""
        INSERT INTO '{module}' VALUES ( :var, :val, :type )
        ON CONFLICT (var) DO
        UPDATE SET val=:val, type=:type WHERE var=:var
        """

        if isinstance(value, bool):
            val = "1" if value else "0"
            typ = "bool"
        elif isinstance(value, str):
            val = value
            typ = "str"
        elif isinstance(value, int):
            val = str(value)
            typ = "int"
        else:
            val = dumps(value)
            typ = "json"

        self.__execute(module, sql, {"var": variable, "val": val, "type": typ})
        self._conn.commit()

        return True

    def remove(self, variable: str):
        module = get_module_name(inspect.getmodule(inspect.stack()[1][0]))

        sql = f"DELETE FROM '{module}' WHERE var=:var"
        self.__execute(module, sql, {"var": variable})
        self._conn.commit()

    def get_collection(self) -> dict:
        module = get_module_name(inspect.getmodule(inspect.stack()[1][0]))

        sql = f"SELECT * FROM '{module}'"
        cur = self.__execute(module, sql)

        collection = {}
        for row in cur:
            collection[row["var"]] = self._parse_row(row)

        return collection

    def close(self):
        module = get_module_name(inspect.getmodule(inspect.stack()[1][0]))
        if not module.startswith(("__main__", "modules")):
            return
        self._conn.commit()
        self._conn.close()


db = Database()
