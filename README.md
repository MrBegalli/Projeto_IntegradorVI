# SuperTrunfo IA - Projeto de Faculdade

!!ALTERAÇÕES AINDA SERÃO REALIZADAS TANTO NO PROJETO QUANTO NA DESCRIÇÃO!!

## Descrição do Projeto

Este projeto é uma implementação de um jogo de SuperTrunfo com suporte a **Inteligência Artificial**. O bot pode jogar em três níveis de dificuldade:

* **Fácil:** Heurística baseada em pesos (WeightedBot)
* **Médio:** Monte Carlo Tree Search (MCTSBot)
* **Difícil:** Reinforcement Learning (RLBot)

O jogador humano escolhe manualmente suas cartas e estatísticas, enquanto o bot faz suas jogadas de acordo com o nível selecionado.

O projeto permite que você carregue um baralho a partir de um arquivo JSON, possibilitando adicionar novas cartas facilmente.

## Estrutura do Projeto

```
supertrunfo/
│
├─ main.py                  # Entrada principal do jogo
├─ deck_loader.py           # Função para carregar o deck JSON
├─ bots/
│   ├─ __init__.py
│   ├─ weighted_bot.py      # Bot Fácil
│   ├─ mcts_bot.py          # Bot Médio
│   ├─ rl_bot.py            # Bot Difícil (usa modelo já treinado)
├─ training/                # Pasta para treinos
│   ├─ __init__.py
│   ├─ train_agent.py       # Script para treinar o RL
└─ utils.py                 # Funções auxiliares
```

## Como Jogar

1. Prepare um arquivo JSON contendo o deck de cartas. Cada carta deve conter as estatísticas:

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
       },
       ...
   ]
   ```
2. Execute `main.py`:

```bash
python main.py
```

3. Informe o caminho do arquivo JSON do deck.
4. Escolha a dificuldade do bot:

   * 1 - Fácil
   * 2 - Médio
   * 3 - Difícil
5. O jogo começa, escolha suas cartas e estatísticas em cada rodada.
6. O placar final será exibido ao final do jogo.

## Requisitos

* Python 3.7+
* Nenhuma biblioteca externa necessária, apenas o Python padrão.

## Funcionalidades

* Três modos de dificuldade distintos para o bot.
* Carregamento de deck a partir de JSON, permitindo expansão do baralho.
* Avaliação estratégica das cartas pelo bot, incluindo simulação de impacto futuro (Minimax/MCTS/Heurística).
* Placar final ao término do jogo.

## Possíveis Melhorias

* Implementar MCTS ou RL mais avançado com simulação de várias rodadas à frente.
* Adicionar interface gráfica usando Tkinter ou PyQt.
* Permitir multiplayer entre dois humanos ou dois bots.
* Salvar histórico de partidas e estatísticas de vitória dos bots.

## Autores

Pedro Bertochi - Projeto de Faculdade

Pedro Octávio - Projeto de Faculdade
