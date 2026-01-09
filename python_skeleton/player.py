'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, DiscardAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import random


class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        pass

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        # the total number of seconds your bot has left to play this game
        game_clock = game_state.game_clock
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0,2,3,4,5,6 representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        # opponent's cards or [] if not revealed
        opp_cards = previous_state.hands[1-active]
        pass

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        street = round_state.street
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.board  # the board cards
        # the number of chips you have contributed to the pot this round of betting
        my_pip = round_state.pips[active]
        # the number of chips your opponent has contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]
        # the number of chips you have remaining
        my_stack = round_state.stacks[active]
        # the number of chips your opponent has remaining
        opp_stack = round_state.stacks[1-active]
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        # the number of chips you have contributed to the pot
        my_contribution = STARTING_STACK - my_stack
        # the number of chips your opponent has contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack

        pot_total = my_contribution + opp_contribution

        # Start Game Strategy Here!
        # legal_actions() returns DiscardAction only when street is 2 or 3
        if DiscardAction in legal_actions:
            # Always discards the first card in the bot's hand
            return DiscardAction(0)


        # Only use DiscardAction if it's in legal_actions (which already checks street)
        # legal_actions() returns DiscardAction only when street is 2 or 3
        if DiscardAction in legal_actions:
            # Create Ranks
            ranks = "23456789TJQKA"
            suits = "CSDH"
            strong_ranks = "TJQKA" # For Full House
            weak_ranks = "23456"

            hole_ranks = [-1, -1, -1]
            hole_suits = [-1, -1, -1]
            board_ranks = [-1, -1]
            board_suits = [-1, -1]

            #Set ranks for holes
            for card in range(3):
                hole_ranks[card] = ranks.index(my_cards[card][0])
                hole_suits[card] = suits.index(my_cards[card][1])

            #Set ranks for board
            for card in range(2):
                board_ranks[card] = ranks.index(board_cards[card][0])
                board_suits[card] = suits.index(my_cards[card][1])

            # Cases to look for: royal/straight flush, 3+ of same rank, drop lower ranks
            # Make action based on suit
            if hole_suits[0] == hole_suits[1] and hole_suits[0] != hole_suits[2]:
                if hole_suits[0] in board_suits:
                    return DiscardAction(2)
                elif hole_ranks[0] == hole_ranks[2] and hole_ranks[0] in board_ranks:
                    return DiscardAction(1)


            elif hole_suits[0] == hole_suits[2] and hole_suits[0] != hole_suits[1]:
                if hole_suits[0] in board_suits:
                    return DiscardAction(1)
                elif hole_ranks[0] == hole_ranks[1] and hole_ranks[0] in board_ranks:
                    return DiscardAction(2)

            elif hole_suits[1] == hole_suits[2] and hole_suits[1] != hole_suits[0]:
                if hole_suits[1] in board_suits:
                    return DiscardAction(0)
                elif hole_ranks[1] == hole_ranks[0] and hole_ranks[1] in board_ranks:
                    return DiscardAction(2)

            # Default: Discard lowest rank
            min_suit = min(hole_ranks)
            min_index = hole_ranks.index(min_suit)
            return DiscardAction(min_index)

        if RaiseAction in legal_actions:
            # the smallest and largest numbers of chips for a legal bet/raise
            min_raise, max_raise = round_state.raise_bounds()
            min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
            max_cost = max_raise - my_pip  # the cost of a maximum bet/raise

            # Check if hand has strong cards
            is_hole_strong = True
            is_hole_weak = False

            is_board_strong = True
            is_board_weak = False

            for card in my_cards:
                if not (card[0] in strong_ranks):
                    is_hole_strong = False
                if (card[0] in weak_ranks):
                    is_hole_weak = True

            for card in board_cards:
                if not (card[0] in strong_ranks):
                    is_board_strong = False
                if (card[0] in weak_ranks):
                    is_board_weak = True

            # Go all in/very high if both are strong

            # Bluff vs. Fold Action
            if is_hole_weak or is_board_weak:
                if is_hole_weak and is_board_weak:
                    return FoldAction()
                else:
                    # Check if board is strong, it true then go max raise
                    if is_board_strong:
                        return RaiseAction(max_raise)

            # If cards are actually strong
            if is_hole_strong or is_board_strong:
                if is_hole_strong and is_board_strong:
                    return RaiseAction(min(min_raise * 8, max_raise))
                else:
                    if random.random() < 0.6:
                        return RaiseAction(min(min_raise * 4, max_raise))

            # Middling Cards
            else:
                if random.random() < 0.3:
                    return RaiseAction(min_raise)

        # More likely to check with middling
        if CheckAction in legal_actions:  # check-call
            return CheckAction()
        if random.random() < 0.25:
            return FoldAction()
        return CallAction()


if __name__ == '__main__':
    run_bot(Player(), parse_args())
