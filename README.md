# SuperTrunfo IA - Projeto de Faculdade

> **Nota:** O projeto e esta documentação ainda estão em desenvolvimento e sujeitos a alterações.

## Descrição do Projeto

Este projeto implementa o jogo SuperTrunfo com suporte a **Inteligência Artificial**. O bot adversário pode jogar em três níveis de dificuldade:

- **Fácil:** Heurística baseada em pesos (`WeightedBot`)
- **Médio:** Monte Carlo Tree Search (`MCTSBot`)
- **Difícil:** Aprendizado por Reforço (`RLBot`)

O jogador humano escolhe manualmente suas cartas e estatísticas, enquanto o bot joga conforme o nível selecionado.

O baralho é carregado a partir de um arquivo JSON, facilitando a adição de novas cartas.

## Estrutura do Projeto

```
Projeto_IntegradorVI/
│
├─ main.py                  # Entrada principal do jogo
├─ deck_loader.py           # Carregamento do baralho a partir de JSON
├─ bots/
│   ├─ __init__.py
│   ├─ weighted_bot.py      # Bot Fácil (heurística)
│   ├─ mcts_bot.py          # Bot Médio (MCTS)
│   ├─ rl_bot.py            # Bot Difícil (modelo RL treinado)
├─ training/
│   ├─ __init__.py
│   ├─ train_agent.py       # Treinamento do agente RL
└─ utils.py                 # Funções auxiliares
```

## Como Jogar

1. Prepare um arquivo JSON com as cartas. Exemplo:
    ```json
    [
         {
              "id": 1,
              "name": "RX-7",
              "brand": "Mazda",
              "year": 1992,
              "color": "red",
              "HP": 255,
              "torque": 217,
              "weight": 1300,
              "0-100": "5.9s",
              "top_speed": "250 km/h"
         }
    ]
    ```
2. Execute o jogo:
    ```bash
    python main.py
    ```
3. Informe o caminho do arquivo JSON do baralho.
4. Escolha a dificuldade do bot:
    - 1 - Fácil
    - 2 - Médio
    - 3 - Difícil
5. Jogue escolhendo cartas e estatísticas a cada rodada.
6. O placar final será exibido ao término do jogo.

## Requisitos

- Python 3.7+
- Não requer bibliotecas externas (apenas Python padrão).

## Funcionalidades

- Três níveis de dificuldade para o bot.
- Carregamento de baralho via JSON.
- Estratégias de IA distintas para cada nível.
- Placar final ao término da partida.

## Possíveis Melhorias

- Aprimorar MCTS ou RL para simular múltiplas rodadas.
- Adicionar interface gráfica (Tkinter ou PyQt).
- Suporte a multiplayer (humano x humano ou bot x bot).
- Salvar histórico de partidas e estatísticas.

## Autores
