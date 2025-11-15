# Super Trunfo IA - Carros Esportivos

Este projeto implementa o clássico jogo Super Trunfo com uma interface web moderna e um backend robusto que utiliza Inteligência Artificial para os oponentes. A aplicação foi totalmente reestruturada para separar o frontend do backend, introduzir uma API RESTful e corrigir bugs, resultando em um sistema modular, escalável e funcional.

O jogo utiliza um baralho de carros esportivos, carregado a partir de um arquivo `carros.json`, e permite ao jogador enfrentar bots com três níveis de dificuldade distintos.

---

## ✨ Features

- **Interface Web Moderna**: Frontend construído com HTML, CSS e JavaScript puro, utilizando Tailwind CSS para um design responsivo e agradável.
- **Backend com API REST**: Servidor backend desenvolvido com FastAPI (Python) que expõe endpoints para toda a lógica do jogo.
- **Três Níveis de Dificuldade**: Jogue contra bots com estratégias diferentes:
    - **Fácil**: Um bot com heurística simples baseada em pesos (`WeightedBot`).
    - **Médio**: Um bot que utiliza Monte Carlo Tree Search (MCTS) para simular jogadas (`MCTSBot`).
    - **Difícil**: Um bot que emprega Reinforcement Learning (Q-Learning) para aprender e aplicar estratégias avançadas (`RLBot`).
- **Gerenciamento de Sessão**: O backend gerencia múltiplas sessões de jogo simultaneamente, com expiração automática de sessões inativas.
- **Código Reorganizado e Otimizado**: A base de código foi completamente refatorada, com separação de responsabilidades, correção de bugs e documentação aprimorada.

---

## 🚀 Arquitetura

O projeto foi dividido em duas partes principais: **Frontend** e **Backend**, que se comunicam através de uma API REST.

### Backend

Construído em Python com o framework **FastAPI**, o backend é responsável por:

- Gerenciar as sessões de jogo.
- Carregar e distribuir as cartas do baralho.
- Implementar a lógica do jogo e a tomada de decisão dos bots.
- Expor endpoints para o frontend consumir.

### Frontend

Desenvolvido com **HTML5, CSS3 e JavaScript (ES6+)**, o frontend é uma aplicação de página única (SPA) que:

- Consome a API do backend para obter dados e executar ações.
- Renderiza a interface do jogo, incluindo o placar, as cartas e os resultados.
- Gerencia o estado da interface e a interação do usuário.

| Componente      | Tecnologia Principal | Responsabilidade                                      |
| --------------- | -------------------- | ----------------------------------------------------- |
| **Backend**     | FastAPI (Python)     | Lógica do jogo, IA dos bots, gerenciamento de sessão  |
| **Frontend**    | JavaScript (Puro)    | Interface do usuário, interação, consumo da API       |
| **Estilização** | Tailwind CSS         | Design responsivo e moderno                           |
| **Comunicação** | API REST (JSON)      | Troca de dados entre frontend e backend               |

---

## 📂 Estrutura do Projeto

A estrutura de diretórios foi organizada para refletir a separação entre frontend e backend:

```
supertrunfo_ia/
├── backend/
│   ├── app/                # Lógica principal da aplicação FastAPI
│   │   ├── __init__.py
│   │   ├── deck_loader.py    # Carregador do baralho
│   │   ├── game_manager.py   # Gerenciador de sessões
│   │   ├── main.py           # Endpoints da API
│   │   ├── models.py         # Modelos Pydantic
│   │   └── utils.py          # Funções auxiliares
│   ├── bots/               # Implementação dos bots de IA
│   │   ├── __init__.py
│   │   ├── mcts_bot.py
│   │   ├── rl_bot.py
│   │   └── weighted_bot.py
│   ├── data/
│   │   └── carros.json       # Baralho do jogo
│   └── requirements.txt    # Dependências Python
├── frontend/
│   └── public/
│       ├── css/style.css
│       ├── index.html
│       └── js/
│           ├── api.js        # Módulo de comunicação com a API
│           └── game.js       # Lógica do jogo no frontend
└── README.md
```

---

## 🛠️ Como Executar Localmente

Para rodar o projeto em sua máquina local, siga os passos abaixo.

### Pré-requisitos

- Python 3.9+
- Um navegador web moderno (Chrome, Firefox, etc.)

### 1. Backend

Primeiro, inicie o servidor backend:

```bash
# 1. Navegue até o diretório do backend
cd supertrunfo_ia/backend

# 2. (Opcional, recomendado) Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie o servidor FastAPI
uvicorn app.main:app --reload
```

O servidor backend estará rodando em `http://localhost:8000`.

### 2. Frontend

Em um novo terminal, inicie um servidor web simples para o frontend:

```bash
# 1. Navegue até o diretório público do frontend
cd supertrunfo_ia/frontend/public

# 2. Inicie um servidor HTTP
python -m http.server 3000
```

Agora, abra seu navegador e acesse `http://localhost:3000` para jogar.

---

## 🔌 Documentação da API

O backend FastAPI gera automaticamente uma documentação interativa. Com o servidor rodando, acesse `http://localhost:8000/docs` para ver todos os endpoints, modelos e testá-los diretamente pelo navegador.

### Principais Endpoints

- `GET /deck`: Retorna o baralho completo de carros.
- `POST /game/start`: Inicia uma nova partida. Requer um corpo JSON com a dificuldade (ex: `{"difficulty": "médio"}`).
- `POST /game/{game_id}/play`: Joga uma rodada. Requer o ID da carta e o atributo escolhido.
- `GET /game/{game_id}/status`: Retorna o estado atual de uma partida.

---

## 🔮 Possíveis Melhorias

- **Treinamento do RLBot**: Criar um script para treinar o `RLBot` contra si mesmo ou outros bots para gerar um arquivo `rl_q_table.json` mais robusto.
- **Animações Avançadas**: Adicionar animações mais complexas para a distribuição e resultado das cartas.
- **Modo Multiplayer**: Implementar um modo de jogo "Jogador vs. Jogador" utilizando WebSockets.
- **Persistência de Dados**: Salvar o histórico de partidas e estatísticas dos jogadores em um banco de dados.

---

## ✍️ Autor

Este projeto foi reorganizado, corrigido e aprimorado por **Manus AI**.
