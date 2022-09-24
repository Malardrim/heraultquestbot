from posixpath import split
from pprint import pp, pprint
import re
import hikari

from SessionEvent import Session
from Table import Table

def get_table_lines(lines):
    table_lines = []
    for line in lines:
        if line.startswith('- Table'):
            table_lines.append(line)
    return table_lines

def get_extra(lines):
    tables_cnt = len(get_table_lines(lines)) + 1
    return '\n'.join(lines[tables_cnt:])

def MessageToSession(message: hikari.Message) -> Session:
    lines = message.content.split('\n')
    infosLine = lines[0]
    lines = lines[1:]
    table_lines = get_table_lines(lines)
    tables = []
    extra = get_extra(lines)
    for table_line in table_lines:
        table = MessageToTable(table_line)
        if table is not None and isinstance(table, Table):
            tables.append(table)
    date = re.search("(([0-9]{2}\/){2}[0-9]{4})", infosLine).group(1)
    hour = re.findall("(?:^.*)(?:a partir de )(.*$)", infosLine)[0]
    return Session(date, hour, tables, message, extra)

def MessageToTable(message: str) -> Table:
    split = message.split(':')
    try:
        content = split[1]
    except IndexError:
        return None
    id = split[0]
    id = id.replace('- Table ', '')
    return Table(id, content)

def session_to_message(session: Session) -> str:
    response = "Session du " + session.date + " a partir de " + session.hour + "\n"
    if session.tables is not None:
        for table in session.tables:
            if table.content is not None:
                response += "- Table " + str(table.id) + ": " + table.content + "\n"
    if session.extra is not None:
            response += "\n"
            response += session.extra
    return response