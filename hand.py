
from player import Player

class HandPlayer(Player):
 
    def __init__(self, player):
        super().__init__(player.ID, player.name, player.coms)
        self.bet_amount = 0
        self.folded = False
 
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
    pass

class Hand():
 
    def __init__(self, players, deck, start_pos=0):
 
        self.deck = deck
        self.pot = 0
        self.bet = 0
        self.playing_players = [HandPlayer(p) for p in players]
 
        self.discard = []
        self.hands = deal_hands(self.deck, len(self.playing_players))
        self.face_down_community_cards = deal_comm_cards(self.deck, self.discard)
        self.face_up_community_cards = []
 
        self.start_pos = start_pos
       
        print("Hand initiated:", str(self))
       
    def run(self):
 
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
        except OnePlayerLeftException:
            self.playing_players[0].win(self.pot)
 
        self.deck.extend(self.discard)
        self.deck.extend([card for hand in self.hands for card in hand])
        self.deck.extend(self.face_up_community_cards)
        self.deck.extend(self.face_down_community_cards)
 
    def assign_blinds(self, small_blind=5, big_blind=10):
        if self.start_pos > len(self.playing_players):
            raise Exception("start position larger than number of players")
 
        if small_blind > big_blind:
            raise Exception("Small blind is bigger than big blind")
 
        small_blind_enable = len(self.playing_players) > 2
 
        for i,player in enumerate(self.playing_players):
            if i == (self.start_pos-1) % len(self.playing_players):
                player.bet(big_blind)
                player.coms.send_line("You are big blind")
            elif small_blind_enable and i == (self.start_pos-2) % len(self.playing_players):
                player.bet(small_blind)
                player.coms.send_line("You are small blind")
            else:
                player.coms.send_line("You are not blind")
 
        self.bet = big_blind
 
    def deal_hands(self):
        for i,player in enumerate(self.playing_players):
            hand = self.hands[i]
            player.coms.send_hand(hand)
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
                current_player.coms.send_line("current bet:{}\n{}? ".format(self.bet, "/".join(available_options)))
                action = current_player.coms.recv(20)
                print("action:'{}'".format(action))
                
                if action == "Fold":
                    current_player.fold()
                elif action == "Call":
                    self.call_bet(current_player)
                elif "Raise" in available_options and action.startswith("Raise"):
                    self.raise_bet(current_player, action)
                    round_end_index = prevp(current_index)
                else:
                    raise Exception("invalid command")

                has_bet.add(current_player.ID)

            if current_index == round_end_index:
                break
            current_index = nextp(current_index)
           
        self.playing_players = [p for p in self.playing_players if not p.folded]
        if len(self.playing_players) < 2:
            raise OnePlayerLeftException()

       
    def call_bet(self, current_player):
        diff = self.bet - current_player.bet_amount
        if current_player.holdings < diff:
            raise Exception("cannot call")
        current_player.bet(diff)

    def raise_bet(self, current_player, action):
        raise_amount = int(action.split(" ")[1])
        diff = (self.bet - current_player.bet_amount) + raise_amount
        if current_player.holdings < diff:
            raise Exception("cannot raise by " + str(raise_amount))
        current_player.bet(diff)
        self.pot += raise_amount
        self.bet += raise_amount
        print("pot raised by {} to {}".format(raise_amount, self.bet))
    
    def reveal_cards(self, num):
        cards = self.face_down_community_cards[:num]        
        for player in self.playing_players:
            player.coms.send_card_reveal(cards)
 
        self.face_down_community_cards = self.face_down_community_cards[num:]
        self.face_up_community_cards = self.face_up_community_cards + cards
        print("revealed cards:", cards)
 
    def __repr__(self):
        return "players={}, hands={}, face_up_community_card={}, face_down_community_cards={}, pot={}"\
               .format(self.playing_players, self.hands, self.face_up_community_cards, self.face_down_community_cards, self.pot)
