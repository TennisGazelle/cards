import logging

from src.constants import *
from src.Deck import Deck
from src.Player import Player

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
        self.logger = logging.getLogger(__name__)

    def print_table_state(self):
        print(
            f'Dealer:',
            'not yet dealt' if not self.dealer.hand() else f'{self.dealer.hand()}',
            0 if self.dealer.hand() == None else self.dealer.hand().getSum()
        )
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
            p.set_bet()
            p.be_dealt(self.deck.next(), self.deck.next())

    def process_player_action(self, active_player: Player):
        action = ACTIONS[active_player.pick_and_stage_q_action(self.dealer.get_showing_card())]
        player_sum, _ = active_player.hand().getSum()
        # print(active_player.getName(), action, player_sum)
        self.logger.info(f"table: {active_player.getName()}, ({player_sum}), chooses to {action}")

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
                self.logger.info(f"{active_player.getName()} {action} {player_sum} {active_player.hand()}")
                # busted!
                self.logger.info(f"{active_player.getName()} 'BUST!'")
                break

        action = ACTIONS[active_player.pick_and_stage_q_action(self.dealer.get_showing_card())]
        self.logger.info(f"{active_player.getName()} {action} {player_sum} {active_player.hand()}")
        return player_sum

    def process_dealer_action(self):
        # do the mandatory loop for the dealer
        # dealer must hit on soft 17, pushes on 22
        dealer_sum, dealer_sum_is_hard = self.dealer.hand().getSum()
        self.logger.info(f"{self.dealer.getName()} {dealer_sum} {self.dealer.hand()}")
        # # todo, fix this logic
        while ((dealer_sum < 16 and dealer_sum_is_hard) or (dealer_sum < 17 and not dealer_sum_is_hard)):
            self.dealer.hit(self.deck.next())
            dealer_sum, dealer_sum_is_hard = self.dealer.hand().getSum()
            self.logger.info(f"{self.dealer.getName()} {dealer_sum} {self.dealer.hand()}")
        return dealer_sum

    def process_player_result(self, dealer_sum, active_player: Player):
        if dealer_sum > 22:
            # dealer loses, everyone wins
            self.logger.info('dealer lost hand, everyone wins')
            pass
        elif dealer_sum == 22:
            # everyone push
            self.logger.info('everyone pushes')
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

        ## check if dealer has blackjack
        if self.dealer.get_showing_card().value == 10:
            if self.dealer.hand().isBlackJack():
                # everyone loses, game done
                print('dealer got blackjack, all lose, restart')
                self.round_status = TableRoundStates['INACTIVE_WAITING']
                return

        if self.dealer.get_showing_card().value == 1:
            # ask for insurance from players
            for p in self.players:
                insurance = p.ask_for_insurance()
            if self.dealer.hand().isBlackJack:
                # everyone loses, game done
                print('dealer got blackjack, all lose, restart')
                self.round_status = TableRoundStates['INACTIVE_WAITING']
                return

        # get all actions from players
        # then dealer does his action
        # then resolve all players
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
            print('unable to add player ', new_player, ', gameplay has started')
