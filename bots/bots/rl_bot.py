import random
import json
from utils import stats, evaluate

class RLBot:
    def __init__(self, deck, epsilon=0.2, qfile=None):
        self.deck = deck
        self.Q = {}
        self.epsilon = epsilon

        # Carregar Q-table se arquivo fornecido
        if qfile:
            try:
                with open(qfile, "r") as f:
                    self.Q = json.load(f)
                # Converte chaves para tuplas
                self.Q = {eval(k): {tuple(eval(a)): v for a, v in actions.items()} for k, actions in self.Q.items()}
                print(f"[RLBot] Q-table carregada de {qfile}")
            except Exception as e:
                print(f"[RLBot] Não foi possível carregar {qfile}: {e}")

    def get_state(self, card_ids):
        return tuple(sorted(card_ids))

    def choose_move(self, player_deck, stats_list):
        state = self.get_state([c['id'] for c in self.deck])
        if state not in self.Q:
            self.Q[state] = {}

        # Exploração
        if random.random() < self.epsilon:
            card = random.choice(self.deck)
            stat = random.choice(stats_list)
            return card, stat

        # Avaliação média ponderada
        best_score = -float("inf")
        best_card, best_stat = None, None
        for c in self.deck:
            for s in stats_list:
                expected = 0
                for opp in player_deck:
                    expected += evaluate(c, opp, s)
                expected /= max(len(player_deck), 1)
                # Q-table refina decisão
                expected += self.Q[state].get((c['id'], s), 0)
                if expected > best_score:
                    best_score = expected
                    best_card, best_stat = c, s
        return best_card, best_stat

    def update_q(self, old_state, action, reward, new_state):
        old_val = self.Q.get(old_state, {}).get(action, 0)
        next_max = max(self.Q.get(new_state, {}).values(), default=0)
        new_val = old_val + 0.5 * (reward + 0.9 * next_max - old_val)
        if old_state not in self.Q:
            self.Q[old_state] = {}
        self.Q[old_state][action] = new_val

    def save_q(self, qfile):
        to_save = {str(k): {str(a): v for a, v in actions.items()} for k, actions in self.Q.items()}
        with open(qfile, "w") as f:
            json.dump(to_save, f, indent=2)
        print(f"[RLBot] Q-table salva em {qfile}")
