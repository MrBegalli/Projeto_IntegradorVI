"""
Módulo de bots para o jogo Super Trunfo.
"""

from .weighted_bot import WeightedBot
from .mcts_bot import MCTSBot
from .rl_bot import RLBot

__all__ = ['WeightedBot', 'MCTSBot', 'RLBot']
