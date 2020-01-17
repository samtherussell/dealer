from hand import Hand

class Card():
 
    def __init__(self, code, name):
        self.code = code
        self.name = name
 
    def __repr__(self):
        return "{} [{}]".format(self.name, self.code)
 
class Game():
 
    def __init__(self, players):
 
        self.players_still_in = list(players)
 
        suits = ['♠', '♥', '♣', '♦']
        numbers = ['A'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']
        deck = [number + suit for suit in suits for number in numbers]
        self.deck = [Card(*c) for c in enumerate(deck)]
 
        print("new game started")
 
       
    def finished(self):
        return len(self.players_still_in) < 2
 
    def run_hand(self):
        hand = Hand(self.players_still_in, self.deck)
        hand.run()
        self.players_still_in = [player for player in self.players_still_in if player.has_money()]
