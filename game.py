import random

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
 
        suits = ["spades", "hearts", "clubs", "diamonds"]
        numbers = ['Ace'] + [str(n) for n in range(2, 11)] + ['Jack', 'Queen', 'King']
        deck = [number + " of " + suit for suit in suits for number in numbers]
        self.deck = [Card(*c) for c in enumerate(deck)]
        random.shuffle(self.deck)
        
        self.start_pos = 0

        print("new game started")
 
       
    def finished(self):
        return len(self.players_still_in) < 2
 
    def run_hand(self):
        hand = Hand(self.players_still_in, self.deck, self.start_pos)
        hand.run()
        self.inc_start_position()

        bust_players = [player for player in self.players_still_in if not player.has_money()]
        for player in bust_players:
            player.coms.send_line("You ran out of money")
            player.coms.close()

        self.players_still_in = [player for player in self.players_still_in if player.has_money()]

    def inc_start_position(self):
        x = self.start_pos
        while True:
            x = (x + 1) % len(self.players_still_in)
            player = self.players_still_in[x]
            if player.has_money():
                self.start_pos = x
                break
