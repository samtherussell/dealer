class Communicator():
 
    def __init__(self, conn):
        self.conn = conn
 
    def send(self, d):
        return self.conn.send(d.encode("utf8"))
 
    def send_line(self, d):
        return self.send(d + "\n")
 
    def send_hand(self, hand):
        cards = " ".join(["{:02d}".format(card.code) for card in hand])
        self.send_line("Hand\n" + cards)
 
    def send_card_reveal(self, reveals):
        cards = " ".join(["{:02d}".format(card.code) for card in reveals])
        self.send_line("Reveal {}\n".format(len(reveals)) + cards)
 
    def recv(self, d):
        return self.conn.recv(d).decode("utf8").strip()
