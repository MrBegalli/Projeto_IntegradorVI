import random
import copy
from utils import stats, evaluate

class MCTSBot:
    def __init__(self, deck, simulations=50):
        self.deck = deck
        self.simulations = simulations

    def simulate(self, bot_card, stat, player_deck):
        score = 0
        for _ in range(self.simulations):
            opp_card = random.choice(copy.deepcopy(player_deck))
            score += evaluate(bot_card, opp_card, stat)
        return score / self.simulations

    def choose_move(self, player_deck, stats_list):
        best_score = -float("inf")
        best_card, best_stat = None, None
        for card in self.deck:
            for stat in stats_list:
                score = self.simulate(card, stat, player_deck)
                if score > best_score:
                    best_score = score
                    best_card, best_stat = card, stat
        return best_card, best_stat
