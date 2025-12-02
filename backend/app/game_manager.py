"""
Gerenciador de sessões de jogo.
"""

import uuid
import copy
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from .models import Difficulty
from .utils import evaluate, STATS

from bots.weighted_bot import WeightedBot
from bots.mcts_bot import MCTSBot
from bots.rl_bot import RLBot


class GameSession:
    """Representa uma sessão de jogo."""
    
    def __init__(self, game_id: str, difficulty: str, player_deck: List[Dict], ai_deck: List[Dict], bot):
        self.game_id = game_id
        self.difficulty = difficulty
        self.player_deck = player_deck
        self.ai_deck = ai_deck
        self.bot = bot
        self.player_score = 0
        self.ai_score = 0
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.game_over = False
        self.game_winner = None
    
    def update_activity(self):
        """Atualiza timestamp da última atividade."""
        self.last_activity = datetime.now()
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Verifica se a sessão expirou."""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)


class GameManager:
    """Gerencia múltiplas sessões de jogo."""
    
    def __init__(self, deck_path: str):
        """
        Inicializa o gerenciador.
        
        Args:
            deck_path: Caminho para o arquivo JSON do baralho
        """
        self.deck_path = deck_path
        self.sessions: Dict[str, GameSession] = {}
        self.full_deck = None
    
    def load_deck(self):
        """Carrega o baralho completo."""
        from .deck_loader import load_deck_from_json
        
        if self.full_deck is None:
            self.full_deck = load_deck_from_json(self.deck_path, shuffle_deck=False)
        
        return copy.deepcopy(self.full_deck)
    
    def create_game(self, difficulty: str) -> Tuple[str, GameSession]:
        """
        Cria uma nova sessão de jogo.
        
        Args:
            difficulty: Nível de dificuldade
        
        Returns:
            Tupla (game_id, session)
        """
        # Limpa sessões expiradas
        self._cleanup_expired_sessions()
        
        # Gera ID único
        game_id = str(uuid.uuid4())
        
        # Carrega e embaralha o baralho
        deck = self.load_deck()
        import random
        random.shuffle(deck)
        
        # Divide o baralho
        half = len(deck) // 2
        player_deck = deck[:half]
        ai_deck = deck[half:]
        
        # Cria o bot apropriado
        bot = self._create_bot(difficulty, ai_deck)
        
        # Cria a sessão
        session = GameSession(game_id, difficulty, player_deck, ai_deck, bot)
        self.sessions[game_id] = session
        
        return game_id, session
    
    def get_session(self, game_id: str) -> Optional[GameSession]:
        """
        Obtém uma sessão de jogo.
        
        Args:
            game_id: ID da sessão
        
        Returns:
            Sessão ou None se não encontrada
        """
        session = self.sessions.get(game_id)
        if session:
            session.update_activity()
        return session
    
    def delete_session(self, game_id: str):
        """Remove uma sessão."""
        if game_id in self.sessions:
            del self.sessions[game_id]
    
    def play_round(
        self, 
        game_id: str, 
        player_card_id: int, 
        attribute: str
    ) -> Dict[str, Any]:
        """
        Executa uma rodada do jogo.
        
        Args:
            game_id: ID da sessão
            player_card_id: ID da carta do jogador
            attribute: Atributo escolhido
        
        Returns:
            Dicionário com resultado da rodada
        
        Raises:
            ValueError: Se parâmetros inválidos
        """
        session = self.get_session(game_id)
        if not session:
            raise ValueError(f"Sessão não encontrada: {game_id}")
        
        if session.game_over:
            raise ValueError("O jogo já terminou")
        
        # Valida atributo
        if attribute not in STATS:
            raise ValueError(f"Atributo inválido: {attribute}. Use um de: {STATS}")
        
        # Encontra carta do jogador
        player_card = None
        for card in session.player_deck:
            if card['id'] == player_card_id:
                player_card = card
                break
        
        if not player_card:
            raise ValueError(f"Carta {player_card_id} não encontrada no deck do jogador")
        
        # Bot escolhe carta
        ai_card = session.bot.choose_card(session.player_deck, attribute)
        
        if not ai_card:
            raise ValueError("IA não conseguiu escolher uma carta")
        
        # Compara cartas
        result = evaluate(player_card, ai_card, attribute)
        
        # Determina vencedor
        if result == 1:
            winner = "player"
            message = f"Você venceu! {player_card['name']} ({player_card[attribute]}) > {ai_card['name']} ({ai_card[attribute]})"
            session.player_score += 1
        elif result == -1:
            winner = "ai"
            message = f"IA venceu! {ai_card['name']} ({ai_card[attribute]}) > {player_card['name']} ({player_card[attribute]})"
            session.ai_score += 1
        else:
            winner = "draw"
            message = f"Empate! {player_card['name']} ({player_card[attribute]}) = {ai_card['name']} ({ai_card[attribute]})"
        
        # Remove cartas jogadas
        session.player_deck.remove(player_card)
        session.ai_deck.remove(ai_card)
        
        # Atualiza deck do bot
        session.bot.deck = session.ai_deck
        
        # Verifica fim de jogo
        game_winner = None
        if len(session.player_deck) == 0 and len(session.ai_deck) == 0:
            session.game_over = True
            if session.player_score > session.ai_score:
                game_winner = "player"
            elif session.ai_score > session.player_score:
                game_winner = "ai"
            else:
                game_winner = "draw"
            session.game_winner = game_winner
        elif len(session.player_deck) == 0:
            session.game_over = True
            game_winner = "ai"
            session.game_winner = game_winner
        elif len(session.ai_deck) == 0:
            session.game_over = True
            game_winner = "player"
            session.game_winner = game_winner
        
        # Prepara resultado
        round_result = {
            "player_card": player_card,
            "ai_card": ai_card,
            "attribute": attribute,
            "winner": winner,
            "player_value": player_card[attribute],
            "ai_value": ai_card[attribute],
            "message": message
        }
        
        return {
            "round_result": round_result,
            "player_score": session.player_score,
            "ai_score": session.ai_score,
            "player_deck_count": len(session.player_deck),
            "ai_deck_count": len(session.ai_deck),
            "game_over": session.game_over,
            "game_winner": game_winner
        }
    
    def _create_bot(self, difficulty: str, deck: List[Dict]):
        """
        Cria uma instância do bot apropriado.
        
        Args:
            difficulty: Nível de dificuldade
            deck: Deck do bot
        
        Returns:
            Instância do bot
        """
        if difficulty == Difficulty.FACIL:
            return WeightedBot(deck)
        elif difficulty == Difficulty.MEDIO:
            return MCTSBot(deck, simulations=25)
        elif difficulty == Difficulty.DIFICIL:
            return MCTSBot(deck, simulations=50)
        elif difficulty == Difficulty.IMPOSSIVEL:
            # Tenta carregar modelo DQN se existir; em caso de erro, usa MCTSBot como fallback
            import os
            qfile = os.path.join(
                os.path.dirname(__file__),
                "..", "data", "dqn_model.pth"
            )
            try:
                qfile_path = qfile if os.path.exists(qfile) else None
                return RLBot(deck, STATS, epsilon=0.0, qfile=qfile_path)
            except Exception:
                # Falha ao inicializar RLBot (ex: dependências faltando ou arquivo inválido) -> fallback para MCTS
                return MCTSBot(deck, simulations=100)
        else:
            # Padrão: fácil
            return WeightedBot(deck)
    
    def _cleanup_expired_sessions(self, timeout_minutes: int = 30):
        """Remove sessões expiradas."""
        expired = [
            game_id for game_id, session in self.sessions.items()
            if session.is_expired(timeout_minutes)
        ]
        
        for game_id in expired:
            del self.sessions[game_id]
        
        if expired:
            print(f"[GameManager] Removidas {len(expired)} sessões expiradas")
