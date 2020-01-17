
from player import Player
from hand_scorer import get_hand_max

class HandPlayer(Player):
 
    def __init__(self, player, hand):
        super().__init__(player.ID, player.name, player.coms)
        self.bet_amount = 0
        self.folded = False
        self.hand = hand
 
    def bet(self, amount):
        super().bet(amount)
        self.bet_amount += amount
 
    def fold(self):
        self.folded = True

def deal_hands(deck, num_players):
 
    hands = [[] for _ in range(num_players)]
 
    for i in range(2):
        for p in range(num_players):
            hands[p].append(deck.pop())
   
    return hands
 
def deal_comm_cards(deck, discard):
 
    comm_cards = []
    deal_order = [discard, comm_cards, comm_cards, comm_cards, discard, comm_cards, discard, comm_cards]
    for pile in deal_order:
        pile.append(deck.pop())
       
    return comm_cards

def get_players_options(current_player, current_bet, has_bet):
    options = ["Fold", "Call"]
    diff = current_bet - current_player.bet_amount
    if current_player.ID not in has_bet and current_player.holdings > diff:
        options.append("Raise")
    return options
 
class OnePlayerLeftException(Exception):
    def __init__(self, player):
        self.player = player

class Hand():
 
    def __init__(self, players, deck, start_pos=0):
 
        self.deck = deck
        self.pot = 0
        self.bet = 0
        self.all_hand_players = players
         
        self.discard = []
        self.hands = deal_hands(self.deck, len(self.all_hand_players))
        self.playing_players = [HandPlayer(p, h) for p,h in zip(players, self.hands)]
        self.face_down_community_cards = deal_comm_cards(self.deck, self.discard)
        self.face_up_community_cards = []
 
        self.start_pos = start_pos
       
        print("Hand initiated:", str(self))

    def put_cards_back_in_deck(self):
        self.deck.extend(self.discard)
        self.deck.extend([card for hand in self.hands for card in hand])
        self.deck.extend(self.face_up_community_cards)
        self.deck.extend(self.face_down_community_cards)
    
    def run(self):

        self.notify_players("----New Hand----")
        self.notify_player_statuses()
        self.assign_blinds()
        self.deal_hands()
       
        try:
            self.run_bet_round()
            self.reveal_cards(3)
            self.run_bet_round()
            self.reveal_cards(1)
            self.run_bet_round()
            self.reveal_cards(1)
            self.run_bet_round()
            self.decide_winner()
        except OnePlayerLeftException as e:
            self.make_winner(e.player)

        self.put_cards_back_in_deck()

    def make_winner(self, winner):
        print("winner:", winner)
        winner.win(self.pot)
        winner.coms.send_line("YOU WIN\nWinnings: {}".format(self.pot - winner.bet_amount))
        self.notify_players("YOU LOSE", exclude=winner.ID)

    def make_draw(self, winners):
        print("winner:s", winners)
        for winner in winners:
            winner.win(self.pot/2)
            winner.coms.send_line("YOU DRAW\nWinnings: {}".format(self.pot/2 - winner.bet_amount))
        self.notify_players("YOU LOSE", exclude=[w.ID for w in winners])

    def notify_players(self, s, exclude=None):
        for player in self.playing_players:
            if exclude is None \
              or type(exclude) == int and player.ID is not exclude \
              or type(exclude) == list and player.ID not in exclude:
                player.coms.send_line(s)

    def notify_player_statuses(self):
        for player in self.playing_players:
            player.coms.send_line("Money left: {}".format(player.holdings))
 
    def assign_blinds(self, small_blind=5, big_blind=10):
        if self.start_pos > len(self.playing_players):
            raise Exception("start position larger than number of players")
 
        if small_blind > big_blind:
            raise Exception("Small blind is bigger than big blind")
 
        small_blind_enable = len(self.playing_players) > 2

        self.notify_players("big blind is {}".format(big_blind))
        self.notify_players("small blind is {}".format(small_blind) if small_blind_enable else "no small blind")
 
        for i,player in enumerate(self.playing_players):
            if i == (self.start_pos-1) % len(self.playing_players):
                player.bet(big_blind)
                player.coms.send_line("You are big blind")
            elif small_blind_enable and i == (self.start_pos-2) % len(self.playing_players):
                player.bet(small_blind)
                player.coms.send_line("You are small blind")
            else:
                player.coms.send_line("You are not the blind")
 
        self.bet = big_blind
        self.pot = big_blind + (small_bling if small_blind_enable else 0)
 
    def deal_hands(self):
        for player in self.playing_players:
            player.coms.send_hand(player.hand)
        print("dealt hands")
 
    def run_bet_round(self):

        def prevp(index):
            return (index - 1) % len(self.playing_players)

        def nextp(index):
            return (index + 1) % len(self.playing_players)
        
        has_bet = set()
        current_index = self.start_pos
        round_end_index = prevp(current_index)
        while True:
            current_player = self.playing_players[current_index]
            if not current_player.folded:
                available_options = get_players_options(current_player, self.bet, has_bet)
                has_bet.add(current_player.ID)
                current_player.coms.send_line("current pot: {}\ncurrent pot bet: {}\nyour current bet: {}"\
                                              .format(self.pot, self.bet, current_player.bet_amount))
                
                while True:
                    current_player.coms.send_line("/".join(available_options))
                    action = current_player.coms.recv(20)
                    print("action:'{}'".format(action))

                    try:
                        if action == "Fold":
                            current_player.fold()
                            break
                        elif action == "Call":
                            self.call_bet(current_player)
                            break
                        elif "Raise" in available_options and action.startswith("Raise"):
                            self.raise_bet(current_player, action)
                            round_end_index = prevp(current_index)
                            break
                        else:
                            raise Exception("Invalid command")
                    except Exception as e:
                        current_player.coms.send_line(str(e))
                        

                self.notify_players("{} played {}".format(current_player.name, action), exclude=current_player.ID)

            left_in = [p for p in self.playing_players if not p.folded]
            if len(left_in) < 2:
                raise OnePlayerLeftException(left_in[0])

            if current_index == round_end_index:
                break
            current_index = nextp(current_index)
           
        self.playing_players = [p for p in self.playing_players if not p.folded]

       
    def call_bet(self, current_player):
        diff = self.bet - current_player.bet_amount
        if current_player.holdings < diff:
            raise Exception("cannot call")
        current_player.bet(diff)

    def raise_bet(self, current_player, action):
        action = action.split(" ")
        if len(action) != 2:
            raise Exception("there is no amount to raise by")
        raise_amount = int(action[1])
        diff = (self.bet - current_player.bet_amount) + raise_amount
        if current_player.holdings < diff:
            raise Exception("not enough money to raise by " + str(raise_amount))
        current_player.bet(diff)
        self.pot += diff
        self.bet += raise_amount
        print("pot raised by {} to {}".format(raise_amount, self.bet))
    
    def reveal_cards(self, num):
        cards = self.face_down_community_cards[:num]        
        for player in self.playing_players:
            player.coms.send_card_reveal(cards)
 
        self.face_down_community_cards = self.face_down_community_cards[num:]
        self.face_up_community_cards = self.face_up_community_cards + cards
        print("revealed cards:", cards)

    def decide_winner(self):

        scores = [(player, get_hand_max(player.hand + self.face_up_community_cards)) for player in self.playing_players]
        scores.sort(key=lambda x: x[1][1], reverse=True)

        print("scores:", scores)

        for score in scores:
            player = score[0]
            trick_name = score[1][0]
            self.notify_players("{} got {}".format(player.name, trick_name), exclude=player.ID)

        for score in scores:
            player = score[0]
            trick_name = score[1][0]
            player.coms.send_line("You got {}".format(trick_name))

        if scores[0][1][1] == scores[1][1][1]:
            winners = [scores[0][0], scores[1][0]]
            self.make_draw(winners)
        else:
            winner = scores[0][0]
            self.make_winner(winner)
    
    def __repr__(self):
        return "players={}, hands={}, face_up_community_card={}, face_down_community_cards={}, pot={}"\
               .format(self.playing_players, self.hands, self.face_up_community_cards, self.face_down_community_cards, self.pot)
