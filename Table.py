class Table:
    id: str = None
    content: str = None
    def __init__(self, id: int, content: str = None) -> None:
        self.id = id
        if content is not None:
            self.content = content.strip()