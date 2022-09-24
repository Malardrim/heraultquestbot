from SessionEvent import Session
from Table import Table

def generate_session(date: str, hour: str, tables: int, extra: str = None) -> Session:
    tables_list = [];
    for tableNb in range(tables):
        tables_list.append(Table(tableNb + 1, ''))
    return Session(date, hour, tables_list, None, extra)