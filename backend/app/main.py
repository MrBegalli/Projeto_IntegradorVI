"""
API REST para o jogo Super Trunfo com IA.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

from .models import (
    StartGameRequest, StartGameResponse,
    PlayRoundRequest, PlayRoundResponse,
    GameStatus, ErrorResponse
)
from .game_manager import GameManager
from .utils import STATS, STATS_DISPLAY


# Inicializa FastAPI
app = FastAPI(
    title="Super Trunfo IA API",
    description="API REST para jogar Super Trunfo contra bots com diferentes níveis de dificuldade",
    version="1.0.0"
)

# Configura CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o gerenciador de jogos
DECK_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "carros.json")
game_manager = GameManager(DECK_PATH)


@app.on_event("startup")
async def startup_event():
    """Carrega o baralho ao iniciar a aplicação."""
    try:
        game_manager.load_deck()
        print(f"[API] Baralho carregado com sucesso: {len(game_manager.full_deck)} cartas")
    except Exception as e:
        print(f"[API] Erro ao carregar baralho: {e}")
        raise


@app.get("/", tags=["Info"])
async def root():
    """Endpoint raiz com informações da API."""
    return {
        "message": "Super Trunfo IA API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "start_game": "POST /game/start",
            "play_round": "POST /game/{game_id}/play",
            "game_status": "GET /game/{game_id}/status",
            "deck": "GET /deck"
        }
    }


@app.get("/health", tags=["Info"])
async def health_check():
    """Verifica saúde da API."""
    return {
        "status": "healthy",
        "active_games": len(game_manager.sessions),
        "deck_loaded": game_manager.full_deck is not None
    }


@app.get("/deck", tags=["Game"])
async def get_deck():
    """Retorna o baralho completo disponível."""
    try:
        deck = game_manager.load_deck()
        return {
            "cards": deck,
            "total": len(deck),
            "attributes": STATS,
            "attributes_display": STATS_DISPLAY
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar baralho: {str(e)}"
        )


@app.post(
    "/game/start",
    response_model=StartGameResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Game"]
)
async def start_game(request: StartGameRequest):
    """
    Inicia uma nova partida.
    
    - **difficulty**: Nível de dificuldade do bot (fácil, médio, difícil)
    
    Retorna o ID da sessão e as cartas do jogador.
    """
    try:
        game_id, session = game_manager.create_game(request.difficulty)
        
        return StartGameResponse(
            game_id=game_id,
            player_deck=session.player_deck,
            ai_deck_count=len(session.ai_deck),
            difficulty=session.difficulty,
            available_stats=STATS
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar jogo: {str(e)}"
        )


@app.post(
    "/game/{game_id}/play",
    response_model=PlayRoundResponse,
    tags=["Game"]
)
async def play_round(game_id: str, request: PlayRoundRequest):
    """
    Joga uma rodada.
    
    - **game_id**: ID da sessão de jogo
    - **card_id**: ID da carta que o jogador vai jogar
    - **attribute**: Atributo escolhido para comparação (HP, torque, weight, 0-100, top_speed)
    
    Retorna o resultado da rodada e o estado atualizado do jogo.
    """
    try:
        result = game_manager.play_round(game_id, request.card_id, request.attribute)
        return PlayRoundResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar rodada: {str(e)}"
        )


@app.get(
    "/game/{game_id}/status",
    response_model=GameStatus,
    tags=["Game"]
)
async def get_game_status(game_id: str):
    """
    Obtém o status atual do jogo.
    
    - **game_id**: ID da sessão de jogo
    
    Retorna informações sobre pontuação, cartas restantes e estado do jogo.
    """
    session = game_manager.get_session(game_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sessão não encontrada: {game_id}"
        )
    
    return GameStatus(
        game_id=session.game_id,
        player_score=session.player_score,
        ai_score=session.ai_score,
        player_deck_count=len(session.player_deck),
        ai_deck_count=len(session.ai_deck),
        difficulty=session.difficulty,
        game_over=session.game_over,
        game_winner=session.game_winner,
        current_player_deck=session.player_deck
    )


@app.delete(
    "/game/{game_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Game"]
)
async def delete_game(game_id: str):
    """
    Encerra e remove uma sessão de jogo.
    
    - **game_id**: ID da sessão de jogo
    """
    session = game_manager.get_session(game_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sessão não encontrada: {game_id}"
        )
    
    game_manager.delete_session(game_id)
    return None


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceções não tratadas."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Erro interno do servidor",
            detail=str(exc)
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
