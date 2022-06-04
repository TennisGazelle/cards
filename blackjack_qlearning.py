#!/usr/lib/python3
import os
import copy
import json
from random import randint
import random
from typing import List, Tuple

NUM_DECKS = 6
SUITS = ['spades', 'hearts', 'clubs', 'diamonds']
VALUES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10] # last three are JQK

# there are a few things any player can do
    # 0 hit (if possible)
    # 1 stay
    # 2 split (if applicable)
    # 3 double (if applicable)
ACTIONS = ['hit', 'stay', 'split', 'double']

GOOD_REWARD_VALUE=1
BAD_REWARD_VALUE=5

INCLUDE_DEALER_IN_Q_STATE=True

DEFAULT_VECTOR = [10, 10, 10, 10]

PLAYER_NAME_CHOICES = ['daniel', 'honi', 'sierra', 'oliver', 'alex', 'kathir', 'ben']
DEALER_NAME_CHOICES = ['Dealer-Pable', 'Dealer-Liz', 'Dealer-Mina']

TableRoundStates = {
    'INACTIVE_WAITING': 'inactive_waiting',
    'ACTIVE_DEAL': 'active_deal'
}

class Card:
    def __init__(self, suit: str, value: int) -> None:
        assert(suit in SUITS)
        assert(value in VALUES)
        self.suit = suit
        self.value = value
    
    def __str__(self) -> str:
        # return f'{self.value} of {self.suit}'
        return f'{self.value}'

class Hand:
    def __init__(self, cards: List[Card]) -> None:
        self.cards = cards

    def __str__(self) -> str:
        return f'[{[str(c) for c in self.cards]}]'

    def size(self) -> int:
        return len(self.cards)
    
    def get(self, index) -> int:
        assert index < len(self.cards)
        return self.cards[index]
    
    def add_card(self, c: Card):
        self.cards.append(c)
    
    def getSum(self) -> Tuple[int, bool]:
        if not self.cards or len(self.cards) == 0:
            return 0

        sum = 0
        isHard = True
        containsAtLeastOneAce = False
        for x in self.cards:
            # print(sum)
            # if it's an ace, check to see if its hard
            if x.value == 1:
                if containsAtLeastOneAce:
                    # there can only be at most one ace that's hard
                    # the first one seen (if previously) could still be reduced if we overflow, if we can (i.e. if notisHard)
                    # we can only ever add one, but if needed, we should reduce the first one
                    sum += 1
                    if sum > 21 and not isHard:
                        sum -= 10 # remove the first ace, make it a 1
                        isHard = True

                else:
                    # this is the first (or only) ace we see, check for 11 compatibility
                    containsAtLeastOneAce = True
                    if sum + 11 < 21:
                        isHard = False
                        sum += 11
                    else:
                        isHard = True # this one is technically redundant
                        sum += 1
            else:
                sum += x.value
                if containsAtLeastOneAce and sum > 21 and not isHard:
                    sum -= 10 # remove the first ace, make it a 1
                    isHard = True

        return sum, isHard
    
    def sort(self) -> List[Card]:
        sortedCards = copy.deepcopy(self.cards)
        sortedCards.sort(key=lambda c: c.value)
        return Hand(sortedCards)

    def isBlackJack(self) -> bool:
        h = self.sort()
        return len(self.cards) == 2 and h.get(0).value == 1 and h.get(1).value == 10

def test_getSum():
    c1 = Card('spades', 1)
    c2 = Card('hearts', 1)
    c3 = Card('spades', 6)
    h = Hand([c1, c2, c3])

    sum, isHard = h.getSum()
    print(h, 'sum:', sum, 'hard' if isHard else 'soft')
    assert(sum == 18)
    assert(isHard == False)

    c1 = Card('spades', 1)
    c2 = Card('hearts', 1)
    c3 = Card('diamonds', 10)
    c4 = Card('clubs', 1)
    h = Hand([c1, c2, c3, c4])

    sum, isHard = h.getSum()
    print(h, 'sum:', sum, 'hard' if isHard else 'soft')
    assert(sum == 13)
    assert(isHard == True)

def test_sortHand():
    c1 = Card('diamonds', 5)
    c2 = Card('hearts', 1)
    c3 = Card('spades', 4)
    h = Hand([c1, c2, c3])
    print(h)
    print(h.sort())

def test_isBlackjack():
    c1 = Card('diamonds', 1)
    c2 = Card('spades', 10)
    h = Hand([c1, c2])
    print(h)
    print(h.isBlackJack())
    assert(h.isBlackJack())

class Deck:
    def __init__(self) -> None:
        deck = []
        for _ in range(NUM_DECKS):
            for s in SUITS:
                for v in VALUES:
                    c = Card(s, v)
                    deck += [c]
        self.deck = deck
        self.index = 0
    
    def shuffle(self) -> None:
        size = len(self.deck)
        # new_indexes = range(size)
        for thisIndex in range(size):
            otherIndex = randint(thisIndex, size-1)

            buffer = self.deck[thisIndex]
            self.deck[thisIndex] = self.deck[otherIndex]
            self.deck[otherIndex] = buffer
    
    def fan(self):
        for c in self.deck:
            print(c)
    
    def next(self):
        c = self.deck[self.index]
        self.index = (self.index + 1) % len(self.deck)
        return c

    def reset(self):
        self.index = 0
        self.shuffle()

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

class Player:
    def __init__(self, name: str, chips: int, is_dealer: bool = False) -> None:
        self.playerName = name
        self.chips = chips or 1000000 # inf money for dealer
        self._hand = None
        self.states = {}
        self.is_dealer = is_dealer

        self.last_states = {}

        self.last_state_key = ''
        self.last_state_action_index = 0

        self.score = {
            'wins': 0,
            'losses': 0
        }
        self.hands_seen = 0

    def __str__(self) -> str:
        return f'{self._name}-${self.chips}-{self._hand}'
    
    def hand(self) -> Hand:
        return self._hand

    def getName(self):
        return self.playerName

    def as_filename(self):
        return f'player_data/{self.getName()}.json'

    def get_metadata(self) -> dict:
        return { 'score': self.score, 'num_states': len(self.states.keys()), 'hands_seen': self.hands_seen }

    def load_states_from_file(self):
        if os.path.exists(self.as_filename()):
            with open(self.as_filename(), 'r') as player_file:
                self.states = json.loads(player_file.read() or '{}')
                player_file.close()

            if 'metadata' in self.states.keys():
                self.score = self.states['metadata']['score']
                self.hands_seen = self.states['metadata']['hands_seen']

    def save_states(self):
        with open(self.as_filename(), 'w+') as player_file:
            payload = self.states.copy()
            payload['metadata'] = self.get_metadata()
            player_file.write(json.dumps(payload, sort_keys=True, indent=3))
            player_file.close()
        print('saved to', player_file.name)

    def be_dealt(self, c1: Card, c2: Card):
        self._hand = Hand([c1, c2])
        self.last_states.clear()
        self.hands_seen += 1
    
    def hit(self, c):
        self._hand.add_card(c)
    
    def get_q_states(self):
        return self.states
    
    @staticmethod
    def generate_player(name: str = ''):
        if name == '':
            name = PLAYER_NAME_CHOICES[randint(0, len(PLAYER_NAME_CHOICES)-1)]
        return Player(name, 1000)

    @staticmethod
    def generate_players(num_players: int):
        return [Player.generate_player() for _ in range(num_players)]

    @staticmethod
    def generate_dealer(name: str = '', chips: int = 1000000):
        if name == '':
            name = DEALER_NAME_CHOICES[randint(0, len(DEALER_NAME_CHOICES)-1)]
        return Player(name, chips, True)

    def get_showing_card(self) -> Card or None:
        if self._hand:
            return self._hand.get(0)
        else:
            return None

    def generate_state_key(self, dealerCard: Card) -> str:
        # sum, is_hard = self._hand.getSum()
        # key = str(sum) + '-hard' if is_hard else '-soft'

        key = str(self._hand.sort())
        if INCLUDE_DEALER_IN_Q_STATE:
            key = str(dealerCard) + '-' + key
        return key


    def pick_and_stage_q_action(self, dealerCard: Card) -> int: # just numbers 1,2,3,4
        # there are a few things any player can do
            # 0 hit (if possible)
            # 1 stay
            # 2 split (if applicable)
            # 3 double (if applicable)
        # represented by 4 float probability vector N within (0,1)^4
        # they will be kept as Q-states in an array with probability vectors for each of them
        # the 'action' will be the one that was made, small cache of sequences are kept in memory
        # if action is good/bad (tbd after this method), memory updated for probability vector

        # is this 'state' in q-table
        key = self.generate_state_key(dealerCard)
        if key not in self.states.keys():
            # if it's a valid state (i.e. not yet busted)
            player_sum, _ = self._hand.getSum()
            if player_sum > 21:
                self.last_state_action_index = 1
                return 1 # stay
            # initialize it, and make it all vectors possible
            self.states[key] = DEFAULT_VECTOR

        # blackjacks are automatic stays
        if self._hand.isBlackJack():
            return 1 # stay

        # shallow copy to keep track of updates
        tokenVector = self.states[key]
        # mem copy to keep track of most recent q lookup
        self.last_state_key = key
        
        # if i can split, consider index 2 in propability vector
        if self._hand.size() == 2 and self._hand.get(0).value == self._hand.get(1).value:
            pass
        else:
            tokenVector[2] = 0

        # if i can double, consider index 3 in probability vector
        if self._hand.size() == 2:
            pass
        else:
            tokenVector[3] = 0
        
        # convert token vector to probability vector
        tokenVectorSum = max(sum(tokenVector), 1)
        probabilityVector = [float(v)/float(tokenVectorSum) for v in tokenVector]
        shot = random.uniform(0, 1) # roll the die
        index = 0
        while shot > 0 and index < len(probabilityVector):
            shot -= probabilityVector[index]
            index += 1
        self.last_state_action_index = index-1

        # save this key in most recent actions
        self.last_states[key] = self.last_state_action_index

        return self.last_state_action_index
    
    def last_action_good(self):
        self.score['wins'] += 1
        self.hands_seen += 1
        # go through the other keys, and add that vector to the q vector
        for key in self.last_states.keys():
            # if key not in self.states.keys():
            #     self.states[key] = [0, 0, 0, 0]
            self.states[key][self.last_states[key]] += GOOD_REWARD_VALUE
        self.flush_last_states()

    def last_action_bad(self):
        self.score['losses'] += 1
        # go through the other keys, and add that vector to the q vector
        for key in self.last_states.keys():
            # if key not in self.states.keys():
            #     self.states[key] = [0, 0, 0, 0]
            self.states[key][self.last_states[key]] -= BAD_REWARD_VALUE
        self.flush_last_states()

    def last_action_neutral(self):
        self.flush_last_states()

    def flush_last_states(self):
        self.last_states.clear()
        
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

class Table:
    def __init__(self, num_players: int = 0) -> None:
        self.dealer = Player.generate_dealer()
        self.players = Player.generate_players(num_players)
        self.rounds = []
        self.current_round = {}
        self.deck = Deck()

        # state machine
            # inactive_waiting - no round happening, receiving bets
            # active_deal - bets locked in, players have been dealt
        self.round_status = TableRoundStates['INACTIVE_WAITING']

    def print_table_state(self):
        print(
            f'Dealer:', 
            'not yet dealt' if not self.dealer.hand() else f'{self.dealer.hand()}', 
            0 if self.dealer.hand() == None else self.dealer.hand().getSum())
        for p in self.players:
            print(
                f'Player {p.getName()}:',
                None if not p.hand() else p.hand(),
                0 if p.hand() == None else p.hand().getSum())

    # start a round
    def deal(self):
        self.deck.reset()
        self.deck.shuffle()

        self.dealer.be_dealt(self.deck.next(), self.deck.next())
        for p in self.players:
            p.be_dealt(self.deck.next(), self.deck.next())

    def process_player_action(self, active_player: Player):
        action = ACTIONS[active_player.pick_and_stage_q_action(self.dealer.get_showing_card())]
        player_sum, _ = active_player.hand().getSum()
        print(active_player.getName(), action, player_sum)
        
        # loop
        while action != 'stay':
            # if action is hit
            if action == 'hit':
                active_player.hit(self.deck.next())
                player_sum, _ = active_player.hand().getSum()

            # todo: if action is double
            if action == 'double':
                active_player.hit(self.deck.next())
                player_sum, _ = active_player.hand().getSum()
                action = 'stay'
                continue

            # todo: if action is split, make temp second hand for player
            if action == 'split':
                # interpreting 'splitting' as staying for now, skip
                action = 'stay'
                continue

            # if i bust, call it out and stop
            if player_sum > 21:
                # bust, call it bad
                active_player.last_action_bad()
                print (active_player.getName(), action, player_sum, active_player.hand())
                # busted!
                print(active_player.getName(), 'BUST!')
                break

        action = ACTIONS[active_player.pick_and_stage_q_action(self.dealer.get_showing_card())]
        print (active_player.getName(), action, player_sum, active_player.hand())
        return player_sum


    def process_dealer_action(self):
        # do the mandatory loop for the dealer
        # dealer must hit on soft 17, pushes on 22
        dealer_sum, dealer_sum_is_hard = self.dealer.hand().getSum()
        print (self.dealer.getName(), dealer_sum, self.dealer.hand())
        # # todo, fix this logic
        while ((dealer_sum < 16 and dealer_sum_is_hard) or (dealer_sum < 17 and not dealer_sum_is_hard)):
            self.dealer.hit(self.deck.next())
            dealer_sum, dealer_sum_is_hard = self.dealer.hand().getSum()
            print (self.dealer.getName(), dealer_sum, self.dealer.hand())
        return dealer_sum

    def process_player_result(self, dealer_sum, active_player: Player):
        if dealer_sum > 22:
            # dealer loses, everyone wins
            print('dealer lost hand, everyone wins')
            pass
        elif dealer_sum == 22:
            # everyone push
            print('everyone pushes')
            pass
        else:
            player_sum, _ = active_player.hand().getSum()
            # determine individual win or not
            if player_sum > 21:
                print(active_player.getName(), 'busted')
                active_player.last_action_bad()
            elif dealer_sum > player_sum:
                print(self.dealer.getName(), 'beats', active_player.getName())
                active_player.last_action_bad()
            elif player_sum > dealer_sum:
                if active_player.hand().isBlackJack():
                    print(active_player.getName(), 'got blackjack')
                    active_player.last_action_good()
                else:
                    print(active_player.getName(), 'beats', self.dealer.getName())
                    active_player.last_action_good()
            else:
                print(active_player.getName(), 'pushes individually')
                active_player.last_action_neutral()

        # active_player.save_states()
        # print('q states:', len(active_player.get_q_states().keys()))
     

    ## main round robin function
    def complete_a_round(self):
        # state machine
            # inactive_waiting - no round happening, receiving bets
            # active_deal - bets locked in, players have been dealt
        self.round_status = TableRoundStates['ACTIVE_DEAL']
        self.deal()
        # self.print_table_state()

        # todo: check for ace or 10, if ace, ask for insurance and if 10 early check for blackjack

        for p in self.players:
            self.process_player_action(p)
        dealer_sum = self.process_dealer_action()

        for p in self.players:
            self.process_player_result(dealer_sum, p)

        self.round_status = TableRoundStates['INACTIVE_WAITING']


    def add_player(self, new_player: Player):
        if (self.round_status == TableRoundStates['INACTIVE_WAITING']):
            self.players.append(new_player)
        else:
            print('unable to add player ', p, ', gameplay has started')

def test_table_population():
    t = Table()
    p1 = Player('p1', 1000)
    p2 = Player('p2', 1000)
    t.add_player(p1)
    t.add_player(p2)

    t.print_table_state()


def test_tableSetup():
    t = Table(3)
    t.print_table_state()

    t.deal()
    t.print_table_state()

# def test_parameterized_round():


def test_table_round():
    # init the players and dealer and deck
    dealer = Player('dealer', None)
    p1 = Player('danny', 1000)
    d = Deck()
    d.shuffle()

    # for the table to have scope into multiple hands a user
    # might choose to make (potential new q state on what to do)
    # all players minimum have one 'table' hand which is shared
    # between dealer and them

    # eventually the player will hold an array of 'hands' that
    # can be shared with the table for part ownership (i.e. minimum bets validated,
    # free bet or other conditions apply for side bets, etc)

    # this round must iterate per hand, per player on table

    # cache for now, remove later
    ##
    ## start removal
    ##

    p1.load_states_from_file()

    ##
    ## end removal
    ##

    for round_index in range(1000):
        # deal to everyone (just straight up, RR not important)
        dealer_showing_card = d.next()
        dealer.be_dealt(dealer_showing_card, d.next())
        p1.be_dealt(d.next(), d.next())

        # main loop for a single player, do this for all players in future
        ## start loop ##

        action = ACTIONS[p1.pick_and_stage_q_action(dealer_showing_card)]
        p1_sum, _ = p1.hand().getSum()
        print (p1.getName(), action, p1_sum, p1.getName())
        while (action != 'stay'):

            # if action is hit
            if action == 'hit':
                p1.hit(d.next())
                p1_sum, _ = p1.hand().getSum()

            # todo: if action is double
            if action == 'double':
                p1.hit(d.next())
                p1_sum, _ = p1.hand().getSum()
                action = 'stay'
                continue

            # todo: if action is split, make temp second hand for player
            if action == 'split':
                # interpreting 'splitting' as staying for now, skip
                action = 'stay'
                continue

            # if i bust, call it out and stop
            if p1_sum > 21:
                # bust, call it bad
                p1.last_action_bad()
                print (p1.getName(), action, p1_sum, p1.hand())
                # busted!
                print(p1.getName(), 'BUST!')
                break

            action = ACTIONS[p1.pick_and_stage_q_action(dealer_showing_card)]
            print (p1.getName(), action, p1_sum, p1.hand())

        # do the mandatory loop for the dealer
        # dealer must hit on soft 17, pushes on 22
        dealer_sum, dealer_sum_is_hard = dealer.hand().getSum()
        print (dealer.getName(), dealer_sum, dealer.hand())
        # todo, fix this logic
        while ((dealer_sum < 16 and dealer_sum_is_hard) or (dealer_sum < 17 and not dealer_sum_is_hard)):
            dealer.hit(d.next())
            dealer_sum, dealer_sum_is_hard = dealer.hand().getSum()
            print (dealer.getName(), dealer_sum, dealer.hand())

        # loop through players and determine their individual winnings (unless global push applies)
        if dealer_sum > 22:
            # dealer loses, everyone wins
            print('dealer lost hand, everyone wins')
            pass
        elif dealer_sum == 22:
            # everyone push
            print('everyone pushes')
            pass
        else:
            # determine individual win or not
            if p1_sum > 21:
                print(p1.getName(), 'busted')
                p1.last_action_bad()
            elif dealer_sum > p1_sum:
                print(dealer.getName(), 'beats', p1.getName())
                p1.last_action_bad()
            elif p1_sum > dealer_sum:
                if p1.hand().isBlackJack():
                    print(p1.getName(), 'got blackjack')
                    p1.last_action_good()
                else:
                    print(p1.getName(), 'beats', dealer.getName())
                    p1.last_action_good()
            else:
                print(p1.getName(), 'pushes individually')
        ## end player loop ##

        

    # cache for now, remove later
    ##
    ## start removal
    ##

    p1.save_states()

    ##
    ## end removal
    ##

    print(json.dumps(p1.get_q_states(), indent=3))
    print('q states:', len(p1.get_q_states().keys()))


# set of all possible states, with all possible choices at each one and values for each

if __name__ == '__main__':
    # test_getSum()
    # test_shuffleDeck()
    # test_prepDeck()
    # test_sortHand()
    # test_tableSetup()
    # test_isBlackjack()
    # test_player_q_action()
    # test_view_player_q_action_states()
    # test_table_population()


    # test_table_round()

    table = Table()
    p1 = Player('test_danny', 20000)
    p1.load_states_from_file()
    table.add_player(p1)

    wins, losses, win_rate, q_state_size = [], [], [], []
    starting_index = p1.get_metadata()['hands_seen']
    for i in range(1, 20000):
        table.complete_a_round()
        
        metadata = p1.get_metadata()
        wins.append(metadata['score']['wins'])
        losses.append(metadata['score']['losses'])
        win_rate.append(float(metadata['score']['wins']) / float(starting_index + i))
        q_state_size.append(metadata['num_states'])

        # print(wins, losses, q_state_size, metadata)

    p1.save_states()
    import matplotlib.pyplot as plt
    import numpy as np

    # Some example data to display
    x = np.array(range(starting_index, starting_index + len(wins)))
    y_wins = np.array(wins)
    y_losses = np.array(losses)
    y_rate = np.array(win_rate)
    y_size = np.array(q_state_size)

    # x = np.linspace(0, 2 * np.pi, 400)
    # y = np.sin(x ** 2)

    # print(x)
    # print(y_wins)
    # print(y_losses)
    # print(y_size)

    fig, axs = plt.subplots(4)
    fig.suptitle('wins, losses, unique q states')
    axs[0].plot(x, y_wins)
    axs[1].plot(x, y_losses)
    axs[2].plot(x, y_rate)
    axs[3].plot(x, y_size)
    plt.show()