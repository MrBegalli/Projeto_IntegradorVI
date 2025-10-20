import random
import json
from utils import stats, evaluate
from collections import defaultdict

class RLBot:
    def __init__(self, deck, epsilon=0.2, alpha=0.5, gamma=0.9, qfile=None):
        self.deck = deck
        # Q-table: chave = (estado, atributo), valor = {ação: Q-valor}
        # Estado: tupla de IDs das cartas na mão do bot
        # Ação: ID da carta escolhida
        # Usamos defaultdict para inicializar Q-valores como 0.0
        self.Q = defaultdict(lambda: defaultdict(float))
        self.epsilon = epsilon  # Taxa de exploração
        self.alpha = alpha      # Taxa de aprendizado
        self.gamma = gamma      # Fator de desconto

        # Carregar Q-table se arquivo fornecido
        if qfile:
            try:
                with open(qfile, "r") as f:
                    data = json.load(f)
                    for state_stat_str, actions_data in data.items():
                        # state_stat_str é '((card_id1, ...), stat)'
                        state_str, stat = state_stat_str.strip('()').rsplit(", ", 1)
                        state = tuple(map(int, state_str.strip('()').split(', ')))
                        state_stat = (state, stat.strip("'"))
                        
                        for action_str, q_value in actions_data.items():
                            # action_str é 'card_id'
                            action = int(action_str)
                            self.Q[state_stat][action] = q_value
                print(f"[RLBot] Q-table carregada de {qfile}")
            except Exception as e:
                print(f"[RLBot] Não foi possível carregar {qfile}: {e}")

    def get_state(self, deck):
        """Retorna o estado atual (tupla de IDs das cartas na mão do bot)."""
        return tuple(sorted([c['id'] for c in deck]))

    def choose_action(self, stat):
        """
        Escolhe a carta a ser jogada (ação) usando a política epsilon-greedy,
        dado o atributo (stat) escolhido pelo oponente.
        """
        state = self.get_state(self.deck)
        state_stat = (state, stat)
        
        possible_actions = [c['id'] for c in self.deck]
        
        if not possible_actions:
            return None # Não há cartas na mão

        # Exploração (Exploration)
        if random.random() < self.epsilon:
            # Escolhe uma carta aleatória
            return random.choice(self.deck)
        # Explotação (Exploitation)
        else:
            q_values = {action: self.Q[state_stat][action] for action in possible_actions}
            
            # Encontra o valor Q máximo
            # Se o valor não existir no Q-table, defaultdict retornará 0.0
            max_q = -float('inf')
            best_actions = []
            
            for action in possible_actions:
                q_val = self.Q[state_stat][action]
                if q_val > max_q:
                    max_q = q_val
                    best_actions = [action]
                elif q_val == max_q:
                    best_actions.append(action)
            
            # Escolhe aleatoriamente entre as ações com o valor Q máximo (para desempatar)
            chosen_card_id = random.choice(best_actions)
            
            # Retorna o objeto carta correspondente ao ID
            return next(c for c in self.deck if c['id'] == chosen_card_id)

    def update_q(self, old_state_stat, action, reward, new_state, new_stat):
        """
        Atualiza o valor Q usando a equação de Q-Learning.
        old_state_stat: tupla ((IDs das cartas), stat)
        action: ID da carta jogada
        new_state: tupla (IDs das cartas)
        new_stat: stat da próxima rodada (escolhido pelo oponente)
        """
        old_q = self.Q[old_state_stat][action]
        
        # Encontra o Q máximo para o próximo estado e o próximo stat
        new_state_stat = (new_state, new_stat)
        
        # O conjunto de ações possíveis no new_state é o conjunto de cartas restantes.
        # Como o bot não tem acesso à mão do oponente no treinamento, ele só pode
        # considerar as cartas que ele mesmo tem.
        
        # Para simplificar o Q-Learning, vamos considerar que a próxima ação será
        # a melhor carta a ser jogada DADO o novo stat.
        # No treinamento, o new_stat será o stat escolhido pelo *oponente* na próxima rodada.
        
        possible_actions = [c['id'] for c in self.deck if c['id'] in new_state]
        
        if possible_actions:
            # Encontra o Q máximo para o próximo estado/stat
            next_max = max(self.Q[new_state_stat][a] for a in possible_actions)
        else:
            next_max = 0 # Fim do episódio
            
        # Equação de Q-Learning
        new_q = old_q + self.alpha * (reward + self.gamma * next_max - old_q)
        self.Q[old_state_stat][action] = new_q

    def save_q(self, qfile):
        """Salva a Q-table em um arquivo JSON."""
        # Converte defaultdict para dict regular para serialização JSON
        to_save = {}
        for state_stat, actions in self.Q.items():
            # state_stat é ((IDs das cartas), stat)
            state, stat = state_stat
            state_stat_str = f"({state}, '{stat}')"
            actions_str = {str(a): v for a, v in actions.items()}
            to_save[state_stat_str] = actions_str
            
        with open(qfile, "w") as f:
            json.dump(to_save, f, indent=2)
        print(f"[RLBot] Q-table salva em {qfile}")

    def choose_card(self, player_deck, stat):
        """
        Função chamada pelo main.py.
        No modo de explotação (epsilon=0), usa a Q-table.
        No modo de exploração (epsilon>0), usa a política epsilon-greedy.
        """
        # A lógica de escolha de ação (com epsilon-greedy) está em choose_action
        chosen_card = self.choose_action(stat)
        
        # Se o RLBot não tiver sido treinado, ele pode não ter valores Q.
        # Fallback para a estratégia do WeightedBot (melhor carta para o stat)
        if chosen_card is None:
            # A lógica do WeightedBot está na linha 69 original, mas a classe WeightedBot
            # já existe no projeto, então podemos usar uma lógica de fallback simples:
            # Escolhe a carta com maior valor no stat escolhido (como o WeightedBot)
            chosen_card = max(self.deck, key=lambda c: (1/c[stat] if stat in ["weight","0-100"] else c[stat]))
            
        return chosen_card