"""
Bot com estratégia baseada em pesos heurísticos.
Nível: Fácil
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import STATS, evaluate


class WeightedBot:
    """
    Bot que escolhe cartas baseado em pesos predefinidos para cada atributo.
    Estratégia simples e previsível.
    """
    
    def __init__(self, deck, stat_weights=None):
        """
        Inicializa o bot.
        
        Args:
            deck: Lista de cartas disponíveis
            stat_weights: Dicionário com pesos para cada atributo (opcional)
        """
        self.deck = deck
        
        # Pesos padrão: valores maiores = mais importante
        # Peso negativo para atributos onde menor é melhor
        if stat_weights is None:
            self.stat_weights = {
                "HP": 1.0,
                "torque": 0.8,
                "weight": -0.5,      # Menor peso é melhor
                "0-100": -0.7,       # Menor tempo é melhor
                "top_speed": 1.2
            }
        else:
            self.stat_weights = stat_weights
    
    def score_card(self, card):
        """
        Calcula um score geral para uma carta baseado nos pesos.
        
        Args:
            card: Carta a ser avaliada
        
        Returns:
            Score numérico (float)
        """
        score = 0
        for stat, weight in self.stat_weights.items():
            value = card.get(stat, 0)
            
            if value == 0:
                continue
            
            # Para atributos onde menor é melhor, inverte o valor
            if stat in ["weight", "0-100"]:
                value = 1 / value
            
            score += value * weight
        
        return score
    
    def choose_card(self, player_deck, chosen_stat):
        """
        Escolhe a melhor carta do deck para jogar contra um atributo específico.
        
        Args:
            player_deck: Deck do jogador (não usado nesta estratégia simples)
            chosen_stat: Atributo escolhido para a rodada
        
        Returns:
            Carta escolhida (dict)
        """
        if not self.deck:
            return None
        
        # Escolhe a carta com maior valor no atributo escolhido
        best_card = max(
            self.deck,
            key=lambda c: (1 / c.get(chosen_stat, 1) if chosen_stat in ["weight", "0-100"] 
                          else c.get(chosen_stat, 0))
        )
        
        return best_card
    
    def choose_move(self, player_deck, stats_list=None):
        """
        Escolhe a melhor carta e atributo para jogar.
        Usado quando o bot tem a vez de escolher o atributo.
        
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
        
        # Escolhe a carta com melhor score geral
        best_card = max(self.deck, key=self.score_card)
        
        # Para essa carta, escolhe o atributo com melhor valor ponderado
        stat_scores = {}
        for stat in stats_list:
            value = best_card.get(stat, 0)
            weight = self.stat_weights.get(stat, 1.0)
            
            if value == 0:
                stat_scores[stat] = -float('inf')
                continue
            
            # Normaliza valores onde menor é melhor
            if stat in ["weight", "0-100"]:
                value = 1 / value
            
            stat_scores[stat] = value * weight
        
        best_stat = max(stat_scores, key=stat_scores.get)
        
        return best_card, best_stat
