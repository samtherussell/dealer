from .communicator import Communicator


class Player:
 
    def __init__(self, ID: int, name, coms: Communicator, holdings=100):
        self.ID = ID
        self.name = name
        self.coms = coms
        self.holdings = holdings
 
    def has_money(self):
        return self.holdings > 0
 
    def bet(self, amount):
        self.holdings -= amount
 
    def win(self, amount):
        self.holdings += amount

    def __eq__(self, other):
        return self.ID == self.ID

    def __repr__(self):
        return "{} with {} left".format(self.name, self.holdings)
