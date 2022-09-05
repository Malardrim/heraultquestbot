from posixpath import split
from pprint import pp, pprint
import re
import hikari

from SessionEvent import Session
from Table import Table

def MessageToSession(message: hikari.Message) -> Session:
    lines = message.content.split('\n');
    infosLine = lines[0]
    tableLines = lines[1:]
    tables = []
    extra = None
    for tableLine in tableLines:
        table = MessageToTable(tableLine)
        if isinstance(table, Table):
            tables.append(table)
        elif table is not None:
            extra = table
    date = re.search("(([0-9]{2}\/){2}[0-9]{4})", infosLine).group(1)
    hour = re.findall("(?:^.*)(?:a partir de )(.*$)", infosLine)[0]
    return Session(date, hour, tables, message, extra)

def MessageToTable(message: str) -> Table:
    split = message.split(':')
    try:
        content = split[1]
    except IndexError:
        return message
    if content is None:
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
            response += "\n" + session.extra
    return response