import random
from typing import List

from hand import Hand
from player import Player
from cards import Card, deck


class Game:
 
    def __init__(self, players: List[Player]):
 
        self.players_still_in = list(players)
 
        self.deck = list(deck)
        random.shuffle(self.deck)
        
        self.start_pos = 0

        print("new game started")

    def finished(self):
        return len(self.players_still_in) < 2
 
    def run_hand(self):
        hand = Hand(self.players_still_in, self.deck, self.start_pos)
        hand.run()

        bust_players = [player for player in self.players_still_in if not player.has_money()]
        for player in bust_players:
            player.coms.send_line("You ran out of money")
            player.coms.close()

        self.players_still_in = [player for player in self.players_still_in if player.has_money()]
        self.inc_start_position()

    def inc_start_position(self):
        x = self.start_pos
        while True:
            x = (x + 1) % len(self.players_still_in)
            player = self.players_still_in[x]
            if player.has_money():
                self.start_pos = x
                break

    def congratulate_winner(self):
        if len(self.players_still_in) > 1:
            print("no-one has won yet")
        else:
            winner_coms = self.players_still_in[0].coms
            winner_coms.send_line("YOU ARE THE CHAMPION")
            winner_coms.close()

