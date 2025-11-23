"""
Bot com estratégia de Reinforcement Learning (Q-Learning).
Nível: Difícil
"""

import random
import json
import sys
import os
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import STATS, evaluate


class RLBot:
    """
    Bot que usa Q-Learning para aprender estratégias ótimas.
    Pode ser treinado ou carregar uma Q-table pré-treinada.
    """
    
    def __init__(self, deck, epsilon=0.2, alpha=0.5, gamma=0.9, qfile=None):
        """
        Inicializa o bot.
        
        Args:
            deck: Lista de cartas disponíveis
            epsilon: Taxa de exploração (0-1)
            alpha: Taxa de aprendizado (0-1)
            gamma: Fator de desconto (0-1)
            qfile: Caminho para arquivo de Q-table (opcional)
        """
        self.deck = deck
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        
        # Q-table: {(estado, atributo): {ação: Q-valor}}
        # Estado: tupla de IDs das cartas na mão
        # Ação: ID da carta escolhida
        self.Q = defaultdict(lambda: defaultdict(float))
        
        # Carrega Q-table se fornecida
        if qfile and os.path.exists(qfile):
            self.load_q(qfile)
    
    def get_state(self, deck=None):
        """
        Retorna o estado atual (tupla de IDs das cartas).
        
        Args:
            deck: Deck a ser usado (usa self.deck se None)
        
        Returns:
            Tupla de IDs ordenados
        """
        if deck is None:
            deck = self.deck
        
        return tuple(sorted([c['id'] for c in deck]))
    
    def choose_action(self, stat):
        """
        Escolhe uma carta usando política epsilon-greedy.
        
        Args:
            stat: Atributo escolhido para a rodada
        
        Returns:
            Carta escolhida (dict)
        """
        if not self.deck:
            return None
        
        state = self.get_state()
        state_stat = (state, stat)
        possible_actions = [c['id'] for c in self.deck]
        
        # Exploração: escolhe carta aleatória
        if random.random() < self.epsilon:
            return random.choice(self.deck)
        
        # Explotação: escolhe carta com maior Q-valor
        q_values = {action: self.Q[state_stat][action] for action in possible_actions}
        
        # Encontra o valor Q máximo
        max_q = max(q_values.values()) if q_values else 0
        
        # Pega todas as ações com Q máximo (para desempate aleatório)
        best_actions = [action for action, q in q_values.items() if q == max_q]
        
        # Se não há Q-valores aprendidos, usa estratégia gulosa simples
        if max_q == 0:
            return self._greedy_fallback(stat)
        
        # Escolhe aleatoriamente entre as melhores
        chosen_id = random.choice(best_actions)
        
        return next(c for c in self.deck if c['id'] == chosen_id)
    
    def _greedy_fallback(self, stat):
        """
        Estratégia gulosa simples quando não há Q-valores.
        
        Args:
            stat: Atributo escolhido
        
        Returns:
            Melhor carta para o atributo
        """
        return max(
            self.deck,
            key=lambda c: (1 / c.get(stat, 1) if stat in ["weight", "0-100"] 
                          else c.get(stat, 0))
        )
    
    def choose_card(self, player_deck, chosen_stat):
        """
        Escolhe a melhor carta para jogar.
        Interface compatível com outros bots.
        
        Args:
            player_deck: Deck do jogador (não usado diretamente)
            chosen_stat: Atributo escolhido para a rodada
        
        Returns:
            Carta escolhida (dict)
        """
        return self.choose_action(chosen_stat)
    
    def choose_move(self, player_deck, stats_list=None):
        """
        Escolhe a melhor carta e atributo para jogar.
        
        Args:
            player_deck: Deck do jogador
            stats_list: Lista de atributos disponíveis (usa STATS se None)
        
        Returns:
            Tupla (carta, atributo)
        """
        if not self.deck:
            return None, None
        
        if stats_list is None:
            stats_list = STATS
        
        state = self.get_state()
        best_card = None
        best_stat = None
        best_q = -float('inf')
        
        # Testa todas as combinações
        for card in self.deck:
            for stat in stats_list:
                state_stat = (state, stat)
                q_value = self.Q[state_stat][card['id']]
                
                if q_value > best_q:
                    best_q = q_value
                    best_card = card
                    best_stat = stat
        
        # Se não há Q-valores, usa heurística
        if best_q == 0:
            best_card = max(self.deck, key=lambda c: c.get('HP', 0))
            best_stat = max(
                stats_list,
                key=lambda s: (1 / best_card.get(s, 1) if s in ["weight", "0-100"] 
                              else best_card.get(s, 0))
            )
        
        return best_card, best_stat
    
    def update_q(self, old_state_stat, action, reward, new_state, new_stat):
        """
        Atualiza Q-valor usando equação de Q-Learning.
        
        Args:
            old_state_stat: Tupla ((IDs), stat)
            action: ID da carta jogada
            reward: Recompensa recebida
            new_state: Novo estado (tupla de IDs)
            new_stat: Atributo da próxima rodada
        """
        old_q = self.Q[old_state_stat][action]
        new_state_stat = (new_state, new_stat)
        
        # Encontra Q máximo para o próximo estado
        possible_actions = [c for c in new_state]
        
        if possible_actions:
            next_max = max(self.Q[new_state_stat][a] for a in possible_actions)
        else:
            next_max = 0  # Fim do episódio
        
        # Equação de Q-Learning
        new_q = old_q + self.alpha * (reward + self.gamma * next_max - old_q)
        self.Q[old_state_stat][action] = new_q
    
    def save_q(self, qfile):
        """
        Salva Q-table em arquivo JSON.
        
        Args:
            qfile: Caminho do arquivo
        """
        to_save = {}
        
        for state_stat, actions in self.Q.items():
            state, stat = state_stat
            state_stat_str = f"({state}, '{stat}')"
            actions_str = {str(a): v for a, v in actions.items()}
            to_save[state_stat_str] = actions_str
        
        with open(qfile, "w", encoding="utf-8") as f:
            json.dump(to_save, f, indent=2)
        
        print(f"[RLBot] Q-table salva em {qfile}")
    
    def load_q(self, qfile):
        """
        Carrega Q-table de arquivo JSON.
        
        Args:
            qfile: Caminho do arquivo
        """
        try:
            with open(qfile, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for state_stat_str, actions_data in data.items():
                # Parse do formato "((1, 2, 3), 'HP')"
                # Remove parênteses externos
                state_stat_str = state_stat_str.strip()
                if state_stat_str.startswith('(') and state_stat_str.endswith(')'):
                    state_stat_str = state_stat_str[1:-1]
                
                # Separa estado e stat
                # Procura pela última vírgula seguida de aspas
                last_comma_idx = state_stat_str.rfind(", '")
                if last_comma_idx == -1:
                    continue
                
                state_part = state_stat_str[:last_comma_idx]
                stat_part = state_stat_str[last_comma_idx+3:]  # Pula ", '"
                
                # Remove parênteses do estado
                state_part = state_part.strip('()')
                # Remove aspas do stat
                stat = stat_part.strip("')")
                
                # Converte string de IDs para tupla
                if state_part:
                    try:
                        state = tuple(map(int, state_part.split(', ')))
                    except ValueError:
                        continue
                else:
                    state = ()
                
                state_stat = (state, stat)
                
                # Carrega Q-valores
                for action_str, q_value in actions_data.items():
                    try:
                        action = int(action_str)
                        self.Q[state_stat][action] = q_value
                    except ValueError:
                        continue
            
            print(f"[RLBot] Q-table carregada de {qfile} ({len(self.Q)} estados)")
        
        except Exception as e:
            print(f"[RLBot] Erro ao carregar Q-table de {qfile}: {e}")
