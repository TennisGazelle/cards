import json
import logging
import os
import random

from src.constants import *
from src.Card import Card
from src.Hand import Hand


class Player:
    def __init__(self, name: str, chips: int, is_dealer: bool = False) -> None:
        self.playerName = name
        self.chips = chips or 1000000  # inf money for dealer
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
        self.pending_chips = 0
        self.logger = logging.getLogger(__name__)

    def __str__(self) -> str:
        return f'{self.playerName}-${self.chips}-{self._hand}'

    def hand(self) -> Hand:
        return self._hand

    def getName(self):
        return self.playerName

    def as_filename(self):
        return f'../player_data/{self.getName()}.json'

    def get_metadata(self) -> dict:
        return {
            'chips': self.chips,
            'score': self.score,
            'num_states': len(self.states.keys()),
            'hands_seen': self.hands_seen,
        }

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
        self.logger.info('PLAYER: saved to ' + player_file.name)

    def be_dealt(self, c1: Card, c2: Card):
        self._hand = Hand([c1, c2])
        self.last_states.clear()
        self.hands_seen += 1

    def set_bet(self):
        # todo, make this variable based on superstition from what they've seen
        bet_value = 1
        self.chips -= bet_value
        self.pending_chips += bet_value
        return bet_value

    def hit(self, c):
        self._hand.add_card(c)

    def get_q_states(self):
        return self.states

    @staticmethod
    def generate_player(name: str = ''):
        if name == '':
            name = PLAYER_NAME_CHOICES[random.randint(0, len(PLAYER_NAME_CHOICES) - 1)]
        return Player(name, 1000)

    @staticmethod
    def generate_players(num_players: int):
        return [Player.generate_player() for _ in range(num_players)]

    @staticmethod
    def generate_dealer(name: str = '', chips: int = 1000000):
        if name == '':
            name = DEALER_NAME_CHOICES[random.randint(0, len(DEALER_NAME_CHOICES) - 1)]
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

    def pick_and_stage_q_action(self, dealerCard: Card) -> int:  # just numbers 0,1,2,3,4...
        # there are a few things any player can do
        # 0 hit (if possible)
        # 1 stay
        # 2 split (if applicable)
        # 3 double (if applicable)
        # 4 lost
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
                return 1  # stay
            # initialize it, and make it all vectors possible
            self.states[key] = DEFAULT_VECTOR

        # blackjacks are automatic stays
        if self._hand.isBlackJack():
            return 1  # stay

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
        probabilityVector = [float(v) / float(tokenVectorSum) for v in tokenVector]
        shot = random.uniform(0, 1)  # roll the die
        index = 0
        while shot > 0 and index < len(probabilityVector):
            shot -= probabilityVector[index]
            index += 1
        self.last_state_action_index = index - 1

        # save this key in most recent actions
        self.last_states[key] = self.last_state_action_index

        return self.last_state_action_index

    ## todo: fix this in case values go negative
    def last_action_good(self):
        self.chips += self.pending_chips * 2
        self.pending_chips = 0

        self.score['wins'] += 1
        self.hands_seen += 1
        # go through the other keys, and add that vector to the q vector
        for key in self.last_states.keys():
            # if key not in self.states.keys():
            #     self.states[key] = [0, 0, 0, 0]
            self.states[key][self.last_states[key]] += GOOD_REWARD_VALUE
        self.flush_last_states()

    ## todo: fix this in case values go negative
    def last_action_bad(self):
        self.pending_chips = 0

        self.score['losses'] += 1
        # go through the other keys, and add that vector to the q vector
        for key in self.last_states.keys():
            # if key not in self.states.keys():
            #     self.states[key] = [0, 0, 0, 0]
            self.states[key][self.last_states[key]] = max(0, self.states[key][self.last_states[key]] - BAD_REWARD_VALUE)
        self.flush_last_states()

    def last_action_neutral(self):
        self.chips += self.pending_chips
        self.pending_chips = 0

        self.flush_last_states()

    def flush_last_states(self):
        self.last_states.clear()

    def ask_for_insurance(self):
        # todo: decide whether or not to give insurance based on hand
        return 0