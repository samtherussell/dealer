class Card:

    def __init__(self, code: int, name: str):
        self.code = code
        self.name = name

    def __repr__(self) -> str:
        return "{} [{}]".format(self.name, self.code)