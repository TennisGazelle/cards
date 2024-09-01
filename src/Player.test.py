import json

from src.Card import Card
from src.Deck import Deck
from src.Player import Player

def test_player_q_action():
    p1 = Player('danny', 1000)
    c1, c2, c3 = Card('spades', 1), Card('hearts', 5), Card('diamonds', 8)
    p1.be_dealt(c1, c2)
    print(p1)
    print('action', p1.pick_and_stage_q_action(c3))


def test_view_player_q_action_states():
    p1 = Player('danny', 1000)
    d = Deck()
    d.shuffle()

    for i in range(1000):
        dealer_card = d.next()
        p1.be_dealt(d.next(), d.next())
        p1.pick_and_stage_q_action(dealer_card)
        p1.last_action_good()

    print(json.dumps(p1.get_q_states(), indent=3))