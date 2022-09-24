from pprint import pprint
from Table import Table
import hikari


class Session:
    message: hikari.Message = None
    date :str = None
    hour:str = None
    tables:list[Table] = None
    extra: str = None
    def __init__(self, date: str, hour: str, tables: list[Table], message: hikari.Message = None, extra: str = None) -> None:
        self.date = date
        self.hour = hour 
        self.tables = tables 
        self.message = message 
        self.extra = extra 
    def __str__(self) -> str:
        return self.date

    def find_table(self, id_table: str) -> Table:
        for table in self.tables:
            if table.id == id_table:
                return table
        return None
    
    def remove_table(self, id_table: str) -> bool:
        for table in self.tables:
            if table.id == id_table:
                self.tables.remove(table)
                return True
        return False

    def first_empty_table(self) -> Table:
        for table in self.tables:
            if table.content is None or table.content == '':
                return table
        return None