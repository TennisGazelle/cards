import logging

from src.constants import *
from src.Deck import Deck
from src.Player import Player

class BlackjackTable:
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
        self.logger = logging.getLogger(__name__)

    def print_table_state(self):
        print(
            'Table:\n'
            '\tDealer:',
            'not yet dealt' if not self.dealer.get_hand() else f'{self.dealer.get_hand()}',
        )
        for p in self.players:
            print(
                f'\tPlayer {p}'
            )

    # start a round
    def deal(self):
        self.deck.reset()
        self.deck.shuffle()

        self.dealer.be_dealt(self.deck.next(), self.deck.next())
        for p in self.players:
            p.set_bet()
            p.be_dealt(self.deck.next(), self.deck.next())

    def process_player_preaction(self, active_player: Player):
        action = ACTIONS[active_player.pick_and_stage_q_action(self.dealer.get_showing_card())]
        player_sum, _ = active_player.get_hand().sum()
        self.logger.info(f"table: {active_player.get_name()}, ({player_sum}), chooses to {action}")

        # loop
        while action != 'stay':
            # if action is hit
            if action == 'hit':
                active_player.hit(self.deck.next())
                player_sum, _ = active_player.get_hand().sum()

            # todo: if action is double
            if action == 'double':
                active_player.hit(self.deck.next())
                player_sum, _ = active_player.get_hand().sum()
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
                self.logger.info(f"{active_player.get_name()} {action} {player_sum} {active_player.get_hand()}")
                # busted!
                self.logger.info(f"{active_player.get_name()} 'BUST!'")
                break

        action = ACTIONS[active_player.pick_and_stage_q_action(self.dealer.get_showing_card())]
        self.logger.info(f"{active_player.get_name()} {action} {player_sum} {active_player.get_hand()}")
        return player_sum

    def process_dealer_action(self):
        dealer_sum, dealer_sum_is_hard = self.dealer.get_hand().sum()
        self.logger.info(f"{self.dealer.get_name()} {dealer_sum} {self.dealer.get_hand()}")

        # dealer must hit on soft 17, pushes on 22
        while (dealer_sum <= 16 and dealer_sum_is_hard) or (dealer_sum <= 17 and not dealer_sum_is_hard):
            self.dealer.hit(self.deck.next())
            dealer_sum, dealer_sum_is_hard = self.dealer.get_hand().sum()
            self.logger.info(f"{self.dealer.get_name()} {dealer_sum} {self.dealer.get_hand()}")

        if dealer_sum > 22:
            # dealer loses, everyone wins
            self.logger.info('dealer lost hand, everyone wins')
            self.logger.info(f"{self.dealer.get_name()} lost; everyone wins; {dealer_sum} {self.dealer.get_hand()}")

        elif dealer_sum == 22:
            # everyone push
            self.logger.info('everyone pushes')
            self.logger.info(f"{self.dealer.get_name()} {dealer_sum}; everyone push {self.dealer.get_hand()}")

        return dealer_sum

    def process_player_result(self, dealer_sum, active_player: Player):
        if dealer_sum >= 22:
            active_player.last_action_neutral()
        else:
            player_sum, _ = active_player.get_hand().sum()
            # determine individual win or not
            if player_sum > 21:
                self.logger.info(f'{active_player.get_name()} busted')
                active_player.last_action_bad()
            elif dealer_sum > player_sum:
                self.logger.info(f'{self.dealer.get_name()} beats {active_player.get_name()}')
                active_player.last_action_bad()
            elif player_sum > dealer_sum:
                if active_player.get_hand().is_blackjack():
                    self.logger.info(f'{active_player.get_name()} got blackjack')
                    active_player.last_action_good()
                else:
                    self.logger.info(f'{active_player.get_name()} beats {self.dealer.get_name()}')
                    active_player.last_action_good()
            else:
                self.logger.info(f'{active_player.get_name()} pushes individually')
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

        ## check if dealer has blackjack (showing a 10 or a A)
        if self.dealer.get_showing_card().value == 10:
            if self.dealer.get_hand().is_blackjack():
                # everyone loses, game done
                print('dealer got blackjack, all lose, restart')
                self.round_status = TableRoundStates['INACTIVE_WAITING']
                return
        if self.dealer.get_showing_card().value == 1:
            # ask for insurance from players
            for p in self.players:
                insurance = p.ask_for_insurance()
            if self.dealer.get_hand().is_blackjack:
                # everyone loses, game done
                print('dealer got blackjack, all lose, restart')
                self.round_status = TableRoundStates['INACTIVE_WAITING']
                return

        # get all actions from players
        # then dealer does his action
        # then resolve all players
        for p in self.players:
            self.process_player_preaction(p)
        dealer_sum = self.process_dealer_action()
        for p in self.players:
            self.process_player_result(dealer_sum, p)

        self.round_status = TableRoundStates['INACTIVE_WAITING']

    def add_player(self, new_player: Player):
        if (self.round_status == TableRoundStates['INACTIVE_WAITING']):
            self.players.append(new_player)
        else:
            print('unable to add player ', new_player, ', gameplay has started')
