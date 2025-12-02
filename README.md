# Super Trunfo Retro - Projeto Integrador VI

Projeto de jogo Super Trunfo com tema de carros esportivos, desenvolvido com frontend estilo retro/pixel art e backend com inteligência artificial.

## 📋 Descrição

Este projeto implementa o clássico jogo de cartas Super Trunfo com uma interface visual retrô e sistema de IA com diferentes níveis de dificuldade. O jogador compete contra bots que utilizam diferentes estratégias, desde escolhas aleatórias até redes neurais profundas (DQN) e busca em árvore Monte Carlo (MCTS).

## 🎮 Características

### Frontend
- **Estilo Visual Retro**: Interface inspirada em jogos clássicos com fonte pixelada (Press Start 2P)
- **Background Temático**: Imagem de fundo personalizada com tema automotivo
- **Sistema de Cartas Flip**: Animações de virada de cartas com efeito 3D
- **Visualização do Baralho**: Possibilidade de ver todas as cartas antes de iniciar
- **Design Responsivo**: Adaptável para diferentes tamanhos de tela

### Backend
- **API RESTful**: Desenvolvida com FastAPI
- **Múltiplos Níveis de Dificuldade**:
  - **Fácil**: Bot com escolhas aleatórias
  - **Médio**: Bot com estratégia ponderada
  - **Difícil**: Bot com busca em árvore Monte Carlo (MCTS)
  - **Impossível**: Bot com IA avançada (Deep Q-Network - DQN)
- **Sistema de Pontuação**: Acompanhamento de vitórias e cartas restantes
- **Gerenciamento de Sessões**: Múltiplas partidas simultâneas

## 🚀 Como Executar (Windows)

### Pré-requisitos

- Python 3.8+ instalado e configurado no PATH
- Navegador web moderno

### Instalação e Execução

1. **Navegar para o diretório do projeto**:
```bash
cd super_trunfo_final
```

2. **Criar e Ativar Ambiente Virtual**:
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Instalar dependências do backend**:
```bash
cd backend
pip install -r requirements.txt
```
*Nota: O arquivo `requirements.txt` lista as dependências necessárias, incluindo PyTorch (necessário para o bot "Difícil").*

4. **Iniciar o servidor backend (Terminal 1)**:
```bash
cd backend
python manage.py serve
```
O backend estará rodando em `http://localhost:8000`

5. **Iniciar o servidor frontend (Terminal 2)**:
*Abra um novo terminal e navegue para o diretório do projeto.*
```bash
cd super_trunfo_final\frontend
python server.py
```
O frontend estará acessível em `http://localhost:3000`

6. **Acessar o Jogo**:
Abra seu navegador e acesse **http://localhost:3000**

## 📁 Estrutura do Projeto

```
super_trunfo_final/
├── backend/
│   ├── app/
│   │   ├── main.py              # API FastAPI
│   │   └── ...                  # Outros arquivos do backend
│   ├── bots/                    # Bots
│   ├── data/
│   ├── manage.py                # Script de gerenciamento
│   └── requirements.txt         # Dependências Python
├── frontend/
│   ├── public/
│   │   ├── css/
│   │   │   └── style.css        # Estilos retro
│   │   ├── js/
│   │   │   ├── api.js           # Cliente da API
│   │   │   └── game.js          # Lógica do frontend
│   │   ├── musica/              # Arquivos de áudio (opcional)
│   │   ├── background_jogo.jpg  # Imagem de fundo
│   │   └── index.html           # Página principal
│   └── server.py                # Servidor HTTP simples
├── API_DOCUMENTATION.md         # Documentação da API
├── HEADME.md                    # Documentação original
├── README.md                    # Este arquivo
├── COMO_EXECUTAR.md             # Guia detalhado de execução
└── ALTERACOES.md                # Resumo das alterações
```

## 🎯 Como Jogar

1. **Visualize o Baralho**: Ao abrir o jogo, você verá todas as cartas disponíveis
2. **Inicie o Jogo**: Clique em "Começar Jogo"
3. **Escolha a Dificuldade**: Selecione o nível de desafio
4. **Selecione sua Carta**: Clique em uma carta do seu deck
5. **Escolha o Atributo**: Clique no atributo que você acha que vai vencer
6. **Confirme a Jogada**: Clique em "Escolher Carta"
7. **Veja o Resultado**: A carta da IA será revelada e o vencedor da rodada será anunciado
8. **Continue Jogando**: Repita até que alguém fique sem cartas

## 🤖 Inteligência Artificial

### Bot Fácil (Random)
Escolhe cartas e atributos aleatoriamente.

### Bot Médio (Weighted)
Utiliza pesos para avaliar os melhores atributos de cada carta.

### Bot Difícil (DQN)
Implementa uma rede neural profunda (Deep Q-Network) que aprende através de reinforcement learning.

### Bot Impossível (MCTS)
Utiliza busca em árvore Monte Carlo para simular múltiplas jogadas futuras e escolher a melhor ação.

## 🛠️ Tecnologias Utilizadas

### Frontend
- HTML5
- CSS3 (com Tailwind CSS via CDN)
- JavaScript (Vanilla)
- Google Fonts (Press Start 2P)

### Backend
- Python 3.8+
- FastAPI
- PyTorch (para DQN)
- NumPy
- Pandas

## 📄 Licença

Este projeto foi desenvolvido para fins educacionais como parte do Projeto Integrador VI.
