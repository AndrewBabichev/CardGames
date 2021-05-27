"""Tests for games."""

import gettext
import numpy as np
import unittest

from .cards import Hand, Deck
from .blackjack import Blackjack
from .queen import Queen, Queen_Hand


def count_cards(cards_ids):
    """
    Count amount of not None cards.

    :param cards_ids: cards to process
    """
    counter = 0
    for card_id in cards_ids:
        if card_id is not None:
            counter += 1
    return counter


class TestDeck(unittest.TestCase):
    """Class to test Deck."""

    def setUp(self):
        """Set all parameters."""
        H1 = Hand()
        H2 = Hand()
        self.game = Deck(hands=[H1, H2], player_hand=1)
        self.game.shuffle()

    def test_00_check_initialization(self):
        """Test initialization."""
        for hand in self.game.hands:
            self.assertTrue(count_cards(hand.cards_ids) == 0)
        self.assertTrue(self.game.deck_cards_ids.size == 52)

    def test_01_check_get_random(self):
        """Test get with random card."""
        for hand in self.game.hands:
            self.game.get(hand)

        for hand in self.game.hands:
            self.assertTrue(count_cards(hand.cards_ids) == 1)
        self.assertTrue(self.game.deck_cards_ids.size == 50)

    def test_02_check_get_target(self):
        """Test get with certain card."""
        get_cards_ids = [
            np.random.randint(0, 26, (1)),
            np.random.randint(26, 52, (1))
        ]
        for hand, card_id in zip(self.game.hands, get_cards_ids):
            self.game.get(hand, card_id=card_id)

        for hand, card_id in zip(self.game.hands, get_cards_ids):
            self.assertTrue(count_cards(hand.cards_ids) == 1)
            self.assertTrue(hand.cards_ids[0] == [card_id // 13, card_id % 13])
        self.assertTrue(self.game.deck_cards_ids.size == 50)

    def test_03_check_draw_drop(self):
        """Test draw with drop option."""
        for hand in self.game.hands:
            self.game.draw(hand, amount=52, empty=26, drop=True)

        for hand in self.game.hands:
            self.assertTrue(count_cards(hand.cards_ids) == 26)
            self.assertTrue(len(hand.cards_ids) == 52)
        self.assertTrue(self.game.deck_cards_ids.size == 0)

    def test_04_check_draw_return(self):
        """Test draw without drop option."""
        for hand in self.game.hands:
            self.game.draw(hand, amount=100, empty=10, drop=False)

        for hand in self.game.hands:
            self.assertTrue(count_cards(hand.cards_ids) == 90)
            self.assertTrue(len(hand.cards_ids) == 100)
        self.assertTrue(self.game.deck_cards_ids.size == 52)

    def test_05_check_choose_card(self):
        """Test choose card."""
        hand = self.game.hands[self.game.player_hand]
        self.game.draw(hand, amount=5, empty=0, drop=True)
        cards_ids = hand.cards_ids

        hand.choose_card(0)
        hand.choose_card(4)
        hand.choose_card(1)
        hand.choose_card(2)

        self.assertTrue(cards_ids[::-1] == hand.cards_ids[::-1])
        self.assertTrue(count_cards(hand.cards_ids) == 5)
        self.assertTrue(self.game.deck_cards_ids.size == 47)


class TestBlackjack(unittest.TestCase):
    """Class to test Blackjack."""

    def setUp(self):
        """Set all parameters."""
        language = gettext.translation(
            domain='CardGames',
            localedir='./CardGames/localization/',
            languages=['eng']
        )
        language.install()
        H1 = Hand()
        H2 = Hand()
        self.game = Blackjack(hands=[H1, H2], player_hand=1, fast=True)

    def test_00_check_initialization(self):
        """Check initialization."""
        for hand in self.game.hands:
            self.assertTrue(count_cards(hand.cards_ids) == 2)
        self.assertTrue(self.game.deck_cards_ids.size == 48)

    def test_01_check_draw(self):
        """Check draw."""
        self.game.shuffle()

        score_1, _ = self.game._count_score(self.game.hands[0])
        score_2, _ = self.game._count_score(self.game.hands[1])
        self.assertTrue(score_1 == score_2)
        self.assertTrue(self.game.deck_cards_ids.size == 52)

    def test_02_check_lose(self):
        """Check game loosing."""
        player_hand = self.game.player_hand
        self.game.shuffle()
        self.game.get(self.game.hands[1 - player_hand])

        score_1, _ = self.game._count_score(self.game.hands[1 - player_hand])
        score_2, _ = self.game._count_score(self.game.hands[player_hand])
        self.assertTrue(score_1 > score_2)
        self.assertTrue(self.game.deck_cards_ids.size == 51)

    def test_03_check_win(self):
        """Check game winning."""
        player_hand = self.game.player_hand
        self.game.shuffle()
        self.game.get(self.game.hands[player_hand])

        score_1, _ = self.game._count_score(self.game.hands[1 - player_hand])
        score_2, _ = self.game._count_score(self.game.hands[player_hand])
        self.assertTrue(score_1 < score_2)
        self.assertTrue(self.game.deck_cards_ids.size == 51)

    def test_04_check_no_overflow(self):
        """Check cards overflow."""
        for hand in self.game.hands:
            for i in range(52):
                self.game.get(hand)

        for hand in self.game.hands:
            self.assertTrue(count_cards(hand.cards_ids) == 6)
            self.assertTrue(len(hand.cards_ids) == 6)
        self.assertTrue(self.game.deck_cards_ids.size == 40)


class TestQueen(unittest.TestCase):
    """Class to test Queen."""

    def setUp(self):
        """Set all parameters."""
        language = gettext.translation(
            domain='CardGames',
            localedir='./CardGames/localization/',
            languages=['eng']
        )
        language.install()
        H1 = Queen_Hand()
        H2 = Queen_Hand()
        H3 = Queen_Hand()
        self.game = Queen(hands=[H1, H2, H3], player_hand=2)

    def test_00_check_initialization(self):
        """Check initialization."""
        for hand in self.game.hands:
            self.assertTrue(
                count_cards(hand.cards_ids) <= 17 and
                count_cards(hand.cards_ids) >= 0)
        self.assertTrue(self.game.deck_cards_ids.size == 0)

    def test_01_check_queen_hand(self):
        """Check class queen hand."""
        self.game.shuffle()
        hand = self.game.hands[self.game.player_hand]
        self.game.get(hand, card_id=[0])
        self.game.get(hand, card_id=[13])
        self.game.get(hand)
        self.assertTrue(count_cards(hand.cards_ids) == 3)

        hand.choose_card(0)
        hand.choose_card(1)
        self.assertTrue(count_cards(hand.cards_ids) == 1)

    def test_02_check_remove_pairs(self):
        """Check remove pairs."""
        self.game.shuffle()
        hand = self.game.hands[self.game.player_hand]
        self.game.get(hand, card_id=[0])
        self.game.get(hand, card_id=[13])
        self.game.get(hand, card_id=[1])
        self.game.get(hand, card_id=[14])
        self.game.get(hand, card_id=[2])
        self.game.get(hand, card_id=[16])
        self.assertTrue(count_cards(hand.cards_ids) == 6)

        self.game.remove_pairs(hand)
        self.assertTrue(count_cards(hand.cards_ids) == 2)

    def test_03_check_unfold(self):
        """Check unfold."""
        self.game.shuffle()
        hand_0 = self.game.hands[1]
        hand_1 = self.game.hands[self.game.player_hand]
        self.game.get(hand_0)
        self.game.get(hand_0)
        self.assertTrue(
            count_cards(hand_0.cards_ids) == 2 and
            count_cards(hand_1.cards_ids) == 0
        )

        self.game.unfold(0)
        self.assertTrue(
            count_cards(hand_0.cards_ids) == 1 and
            count_cards(hand_1.cards_ids) == 1
        )
