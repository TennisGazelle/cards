from src.Deck import Deck


def test_shuffleDeck():
    d = Deck()
    d.shuffle()
    d.fan()

def test_prepDeck():
    d = Deck()
    d.shuffle()
    print('prep_deck')
    print(d.next())
    print(d.next())
    print(d.next())