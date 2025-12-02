"""
Sistema de Logs Estruturado para Super Trunfo
==============================================

Fornece logging consistente e organizado para toda a aplicação.
"""

import os
import logging
from datetime import datetime
from pathlib import Path


class GameLogger:
    """Logger centralizado para o jogo Super Trunfo."""
    
    def __init__(self, name="SuperTrunfo", log_dir="../logs"):
        """
        Inicializa o logger.
        
        Args:
            name: Nome do logger
            log_dir: Diretório para armazenar os logs
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configura o logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove handlers existentes para evitar duplicação
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Handler para arquivo (todos os níveis)
        timestamp = datetime.now().strftime("%Y%m%d")
        file_handler = logging.FileHandler(
            self.log_dir / f"game_{timestamp}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Handler para console (INFO e acima)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '[%(levelname)s] %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # Adiciona handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """Registra mensagem de debug."""
        self.logger.debug(message)
    
    def info(self, message):
        """Registra mensagem informativa."""
        self.logger.info(message)
    
    def warning(self, message):
        """Registra mensagem de aviso."""
        self.logger.warning(message)
    
    def error(self, message):
        """Registra mensagem de erro."""
        self.logger.error(message)
    
    def critical(self, message):
        """Registra mensagem crítica."""
        self.logger.critical(message)
    
    def log_game_start(self, player1, player2):
        """Registra início de um jogo."""
        self.info("="*60)
        self.info(f"NOVO JOGO: {player1} vs {player2}")
        self.info("="*60)
    
    def log_round(self, round_num, player, card, stat, result):
        """Registra uma rodada do jogo."""
        result_str = "VITÓRIA" if result == 1 else "DERROTA" if result == -1 else "EMPATE"
        self.info(f"Rodada {round_num}: {player} jogou {card['name']} ({stat}={card.get(stat)}) - {result_str}")
    
    def log_game_end(self, winner, score):
        """Registra fim de um jogo."""
        self.info(f"FIM DE JOGO: Vencedor = {winner} | Placar = {score}")
        self.info("="*60 + "\n")
    
    def log_training_metrics(self, episode, metrics):
        """Registra métricas de treinamento."""
        self.info(f"\n--- Episódio {episode} ---")
        for key, value in metrics.items():
            if isinstance(value, float):
                self.info(f"  {key}: {value:.4f}")
            else:
                self.info(f"  {key}: {value}")


# Instância global do logger
_game_logger = None


def get_logger(name="SuperTrunfo", log_dir="../logs"):
    """
    Retorna a instância global do logger.
    
    Args:
        name: Nome do logger
        log_dir: Diretório para armazenar os logs
    
    Returns:
        GameLogger: Instância do logger
    """
    global _game_logger
    
    if _game_logger is None:
        _game_logger = GameLogger(name, log_dir)
    
    return _game_logger


# Funções de conveniência
def debug(message):
    """Registra mensagem de debug."""
    get_logger().debug(message)


def info(message):
    """Registra mensagem informativa."""
    get_logger().info(message)


def warning(message):
    """Registra mensagem de aviso."""
    get_logger().warning(message)


def error(message):
    """Registra mensagem de erro."""
    get_logger().error(message)


def critical(message):
    """Registra mensagem crítica."""
    get_logger().critical(message)
