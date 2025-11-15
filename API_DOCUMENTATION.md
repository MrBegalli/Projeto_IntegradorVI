# Documentação da API - Super Trunfo IA

## Base URL

Quando rodando localmente:
```
http://localhost:8000
```

## Endpoints

### 1. Health Check

Verifica se a API está funcionando.

**Endpoint:** `GET /health`

**Resposta:**
```json
{
    "status": "healthy",
    "active_games": 0,
    "deck_loaded": true
}
```

---

### 2. Obter Baralho Completo

Retorna todas as cartas disponíveis no jogo.

**Endpoint:** `GET /deck`

**Resposta:**
```json
{
    "cards": [
        {
            "id": 1,
            "name": "RX-7",
            "brand": "Mazda",
            "year": 1992,
            "color": "red",
            "HP": 255.0,
            "torque": 217.0,
            "weight": 1300.0,
            "0-100": 5.9,
            "top_speed": 250.0
        }
    ],
    "total": 10,
    "attributes": ["HP", "torque", "weight", "0-100", "top_speed"],
    "attributes_display": {
        "HP": "Potência (HP)",
        "torque": "Torque (Nm)",
        "weight": "Peso (kg)",
        "0-100": "0-100 km/h (s)",
        "top_speed": "Velocidade Máxima (km/h)"
    }
}
```

---

### 3. Iniciar Novo Jogo

Cria uma nova sessão de jogo e distribui as cartas.

**Endpoint:** `POST /game/start`

**Body:**
```json
{
    "difficulty": "médio"
}
```

Opções de dificuldade: `"fácil"`, `"médio"`, `"difícil"`

**Resposta:**
```json
{
    "game_id": "98ff919d-73a6-4351-87fc-8e5fcb5c3987",
    "player_deck": [
        {
            "id": 8,
            "name": "Aventador",
            "brand": "Lamborghini",
            "year": 2019,
            "color": "orange",
            "HP": 759.0,
            "torque": 720.0,
            "weight": 1575.0,
            "0-100": 2.8,
            "top_speed": 350.0
        }
    ],
    "ai_deck_count": 5,
    "difficulty": "médio",
    "available_stats": ["HP", "torque", "weight", "0-100", "top_speed"]
}
```

---

### 4. Jogar Rodada

Executa uma rodada do jogo.

**Endpoint:** `POST /game/{game_id}/play`

**Body:**
```json
{
    "card_id": 8,
    "attribute": "HP"
}
```

**Resposta:**
```json
{
    "round_result": {
        "player_card": {
            "id": 8,
            "name": "Aventador",
            "HP": 759.0
        },
        "ai_card": {
            "id": 2,
            "name": "Civic Type R",
            "HP": 306.0
        },
        "attribute": "HP",
        "winner": "player",
        "player_value": 759.0,
        "ai_value": 306.0,
        "message": "Você venceu! Aventador (759.0) > Civic Type R (306.0)"
    },
    "player_score": 1,
    "ai_score": 0,
    "player_deck_count": 4,
    "ai_deck_count": 4,
    "game_over": false,
    "game_winner": null
}
```

---

### 5. Obter Status do Jogo

Retorna o estado atual de uma partida.

**Endpoint:** `GET /game/{game_id}/status`

**Resposta:**
```json
{
    "game_id": "98ff919d-73a6-4351-87fc-8e5fcb5c3987",
    "player_score": 1,
    "ai_score": 0,
    "player_deck_count": 4,
    "ai_deck_count": 4,
    "difficulty": "médio",
    "game_over": false,
    "game_winner": null,
    "current_player_deck": [...]
}
```

---

### 6. Encerrar Jogo

Remove uma sessão de jogo.

**Endpoint:** `DELETE /game/{game_id}`

**Resposta:** Status 204 (No Content)

---

## Códigos de Status HTTP

- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso
- `204 No Content`: Requisição bem-sucedida sem conteúdo de resposta
- `400 Bad Request`: Parâmetros inválidos
- `404 Not Found`: Recurso não encontrado
- `500 Internal Server Error`: Erro no servidor

---

## Documentação Interativa

Acesse `http://localhost:8000/docs` para ver a documentação interativa gerada automaticamente pelo FastAPI (Swagger UI).
