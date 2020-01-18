class Player():
 
    def __init__(self, ID, name, coms, holdings=100):
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
 
    def __repr__(self):
        return self.name
