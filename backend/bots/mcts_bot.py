"""
Bot com estratégia Monte Carlo Tree Search.
Nível: Médio
"""

import random
import copy
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import STATS, evaluate


class MCTSBot:
    """
    Bot que usa Monte Carlo Tree Search para simular jogadas futuras.
    Mais inteligente que o WeightedBot, mas ainda computacionalmente leve.
    """
    
    def __init__(self, deck, simulations=50):
        """
        Inicializa o bot.
        
        Args:
            deck: Lista de cartas disponíveis
            simulations: Número de simulações por jogada
        """
        self.deck = deck
        self.simulations = simulations
    
    def simulate(self, bot_card, stat, player_deck):
        """
        Simula múltiplas rodadas para avaliar uma jogada.
        
        Args:
            bot_card: Carta que o bot vai jogar
            stat: Atributo escolhido
            player_deck: Deck do jogador
        
        Returns:
            Score médio das simulações (float)
        """
        if not player_deck:
            return 0
        
        score = 0
        for _ in range(self.simulations):
            # Escolhe uma carta aleatória do jogador
            opp_card = random.choice(player_deck)
            
            # Avalia o resultado
            result = evaluate(bot_card, opp_card, stat)
            score += result
        
        return score / self.simulations
    
    def choose_card(self, player_deck, chosen_stat):
        """
        Escolhe a melhor carta para jogar contra um atributo específico.
        Usa simulações para avaliar cada opção.
        
        Args:
            player_deck: Deck do jogador
            chosen_stat: Atributo escolhido para a rodada
        
        Returns:
            Carta escolhida (dict)
        """
        if not self.deck:
            return None
        
        # Simula cada carta e escolhe a com melhor score
        best_card = None
        best_score = -float('inf')
        
        for card in self.deck:
            score = self.simulate(card, chosen_stat, player_deck)
            if score > best_score:
                best_score = score
                best_card = card
        
        return best_card
    
    def choose_move(self, player_deck, stats_list=None):
        """
        Escolhe a melhor carta e atributo para jogar.
        Simula todas as combinações possíveis.
        
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
        
        best_score = -float('inf')
        best_card = None
        best_stat = None
        
        # Testa todas as combinações de carta + atributo
        for card in self.deck:
            for stat in stats_list:
                score = self.simulate(card, stat, player_deck)
                
                if score > best_score:
                    best_score = score
                    best_card = card
                    best_stat = stat
        
        return best_card, best_stat
    
    def simulate_game(self, bot_card, stat, player_deck, depth=3):
        """
        Simulação mais profunda considerando múltiplas rodadas.
        Versão avançada (opcional, não usada por padrão).
        
        Args:
            bot_card: Carta do bot
            stat: Atributo escolhido
            player_deck: Deck do jogador
            depth: Profundidade da simulação
        
        Returns:
            Score estimado (float)
        """
        if depth == 0 or not player_deck:
            return 0
        
        total_score = 0
        
        for _ in range(self.simulations // depth):
            # Simula uma rodada
            opp_card = random.choice(player_deck)
            round_result = evaluate(bot_card, opp_card, stat)
            
            # Simula rodadas futuras recursivamente
            if depth > 1:
                remaining_player = [c for c in player_deck if c != opp_card]
                remaining_bot = [c for c in self.deck if c != bot_card]
                
                if remaining_bot and remaining_player:
                    next_card = random.choice(remaining_bot)
                    next_stat = random.choice(STATS)
                    future_score = self.simulate_game(
                        next_card, next_stat, remaining_player, depth - 1
                    )
                    total_score += round_result + 0.9 * future_score
                else:
                    total_score += round_result
            else:
                total_score += round_result
        
        return total_score / (self.simulations // depth)
