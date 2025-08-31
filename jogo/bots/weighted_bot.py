from utils import stats

class WeightedBot:
    def __init__(self, deck, stat_weights=None):
        self.deck = deck
        if stat_weights is None:
            self.stat_weights = {"HP": 1.0, "torque": 0.8, "weight": -0.5, "0-100": -0.7, "top_speed": 1.2}
        else:
            self.stat_weights = stat_weights

    def score_card(self, card):
        score = 0
        for stat, weight in self.stat_weights.items():
            value = card[stat]
            if stat in ["weight", "0-100"]:
                value = 1 / value
            score += value * weight
        return score

    def choose_move(self, player_deck, stats_list):
        best_card = max(self.deck, key=self.score_card)
        stat_scores = {stat: self.stat_weights.get(stat,1)*((1/best_card[stat] if stat in ["weight","0-100"] else best_card[stat])) for stat in stats_list}
        best_stat = max(stat_scores, key=stat_scores.get)
        return best_card, best_stat

    def choose_card(self, player_deck, stat):
        # escolhe a carta com maior valor no stat escolhido
        best_card = max(self.deck, key=lambda c: (1/c[stat] if stat in ["weight","0-100"] else c[stat]))
        return best_card
