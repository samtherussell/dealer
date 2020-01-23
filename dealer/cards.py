class Card:

    def __init__(self, code: int, name: str):
        self.code = code
        self.name = name

    def __repr__(self) -> str:
        return "{} [{}]".format(self.name, self.code)


suit_names = ["spades", "hearts", "clubs", "diamonds"]
number_names = ['Ace'] + [str(n) for n in range(2, 11)] + ['Jack', 'Queen', 'King']
card_names = [number + " of " + suit for suit in suit_names for number in number_names]
deck = [Card(*c) for c in enumerate(card_names)]

card_name_lookup = {card.name: card for card in deck}
card_code_lookup = {card.code: card for card in deck}

