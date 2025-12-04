"""
Modelos de dados para a API do Super Trunfo.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class Difficulty(str, Enum):
    """Níveis de dificuldade do bot."""
    FACIL = "fácil"
    MEDIO = "médio"
    DIFICIL = "difícil"
    IMPOSSIVEL = "impossivel"


class Card(BaseModel):
    """Representa uma carta do jogo."""
    id: int
    name: str
    brand: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    HP: float
    torque: float
    weight: float
    zero_to_hundred: float = Field(alias="0-100")
    top_speed: float
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "RX-7",
                "brand": "Mazda",
                "year": 1992,
                "color": "red",
                "HP": 255,
                "torque": 217,
                "weight": 1300,
                "0-100": 5.9,
                "top_speed": 250
            }
        }


class StartGameRequest(BaseModel):
    """Requisição para iniciar um novo jogo."""
    difficulty: Difficulty = Field(
        default=Difficulty.FACIL,
        description="Nível de dificuldade do bot"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "difficulty": "médio"
            }
        }


class StartGameResponse(BaseModel):
    """Resposta ao iniciar um novo jogo."""
    game_id: str = Field(description="ID único da sessão de jogo")
    player_deck: List[Dict[str, Any]] = Field(description="Cartas do jogador")
    ai_deck_count: int = Field(description="Número de cartas da IA")
    difficulty: str = Field(description="Dificuldade selecionada")
    available_stats: List[str] = Field(description="Atributos disponíveis para jogar")


class PlayRoundRequest(BaseModel):
    """Requisição para jogar uma rodada."""
    card_id: int = Field(description="ID da carta que o jogador vai jogar")
    attribute: str = Field(description="Atributo escolhido para comparação")
    
    class Config:
        json_schema_extra = {
            "example": {
                "card_id": 1,
                "attribute": "HP"
            }
        }


class RoundResult(BaseModel):
    """Resultado de uma rodada."""
    player_card: Dict[str, Any] = Field(description="Carta jogada pelo jogador")
    ai_card: Dict[str, Any] = Field(description="Carta jogada pela IA")
    attribute: str = Field(description="Atributo comparado")
    winner: str = Field(description="Vencedor da rodada: 'player', 'ai' ou 'draw'")
    player_value: float = Field(description="Valor do atributo da carta do jogador")
    ai_value: float = Field(description="Valor do atributo da carta da IA")
    message: str = Field(description="Mensagem descritiva do resultado")


class PlayRoundResponse(BaseModel):
    """Resposta após jogar uma rodada."""
    round_result: RoundResult
    player_score: int = Field(description="Pontuação atual do jogador")
    ai_score: int = Field(description="Pontuação atual da IA")
    player_deck_count: int = Field(description="Número de cartas restantes do jogador")
    ai_deck_count: int = Field(description="Número de cartas restantes da IA")
    game_over: bool = Field(description="Se o jogo terminou")
    game_winner: Optional[str] = Field(
        default=None,
        description="Vencedor do jogo (se game_over=True): 'player', 'ai' ou 'draw'"
    )


class GameStatus(BaseModel):
    """Status atual do jogo."""
    game_id: str
    player_score: int
    ai_score: int
    player_deck_count: int
    ai_deck_count: int
    difficulty: str
    game_over: bool
    game_winner: Optional[str] = None
    current_player_deck: List[Dict[str, Any]] = Field(
        description="Cartas atuais do jogador"
    )


class ErrorResponse(BaseModel):
    """Resposta de erro."""
    error: str = Field(description="Mensagem de erro")
    detail: Optional[str] = Field(default=None, description="Detalhes adicionais")
