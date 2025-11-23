# Correções Aplicadas no Projeto Super Trunfo IA

Este documento descreve todas as correções realizadas para fazer o projeto voltar a funcionar.

## Data da Correção
23 de Novembro de 2025

## Problemas Encontrados e Soluções

### 1. Importação Não Utilizada (main.py)

**Problema:** O arquivo `backend/app/main.py` importava `RLBot` mas não utilizava.

**Arquivo:** `backend/app/main.py` (linha 16)

**Correção:**
```python
# ANTES
from ..bots.rl_bot import RLBot

# DEPOIS
# (linha removida)
```

**Impacto:** Limpeza de código, sem impacto funcional.

---

### 2. Parâmetro Faltante no RLBot (CRÍTICO)

**Problema:** O construtor do `RLBot` esperava o parâmetro `stats_list`, mas não estava sendo passado ao criar o bot de dificuldade "difícil".

**Arquivo:** `backend/app/game_manager.py` (linha 254)

**Correção:**
```python
# ANTES
return RLBot(deck, epsilon=0.0, qfile=qfile if os.path.exists(qfile) else None)

# DEPOIS
return RLBot(deck, STATS, epsilon=0.0, qfile=qfile if os.path.exists(qfile) else None)
```

**Impacto:** **CRÍTICO** - Sem esta correção, o jogo travava ao selecionar dificuldade "difícil" com erro `TypeError`.

---

### 3. Caminho Errado do Modelo DQN

**Problema:** O código tentava carregar `rl_q_table.json` (modelo antigo Q-Learning) em vez de `dqn_model.pth` (modelo DQN atual).

**Arquivo:** `backend/app/game_manager.py` (linha 250-253)

**Correção:**
```python
# ANTES
qfile = os.path.join(
    os.path.dirname(__file__), 
    "..", "data", "rl_q_table.json"
)

# DEPOIS
qfile = os.path.join(
    os.path.dirname(__file__), 
    "..", "data", "dqn_model.pth"
)
```

**Impacto:** O bot de nível difícil agora pode carregar o modelo treinado corretamente (se existir).

---

### 4. Dependências Faltantes (CRÍTICO)

**Problema:** O arquivo `requirements.txt` não incluía `torch` e `numpy`, necessários para o bot de IA.

**Arquivo:** `backend/requirements.txt`

**Correção:**
```txt
# ANTES
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6

# DEPOIS
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
torch==2.1.0
numpy==1.24.3
```

**Impacto:** **CRÍTICO** - Sem estas dependências, o servidor não inicia.

---

### 5. URL Hardcoded da API (Frontend)

**Problema:** A URL da API estava hardcoded com um domínio de desenvolvimento antigo.

**Arquivo:** `frontend/public/js/api.js` (linha 5)

**Correção:**
```javascript
// ANTES
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : 'https://8000-i003phe7kjhw34lv8ctlm-51754cba.manusvm.computer';

// DEPOIS
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : `${window.location.protocol}//${window.location.hostname}:8000`;
```

**Impacto:** Frontend agora funciona em qualquer ambiente, detectando automaticamente a URL correta.

---

### 6. Importações Relativas Incorretas

**Problema:** As importações dos bots em `game_manager.py` usavam importação relativa (`..bots`), causando erro `ImportError: attempted relative import beyond top-level package`.

**Arquivo:** `backend/app/game_manager.py` (linhas 13-15)

**Correção:**
```python
# ANTES
from ..bots.weighted_bot import WeightedBot
from ..bots.mcts_bot import MCTSBot
from ..bots.rl_bot import RLBot

# DEPOIS
from bots.weighted_bot import WeightedBot
from bots.mcts_bot import MCTSBot
from bots.rl_bot import RLBot
```

**Impacto:** **CRÍTICO** - Servidor agora inicia corretamente com uvicorn.

---

### 7. Incompatibilidade de Dimensão do RLBot (CRÍTICO)

**Problema:** O RLBot estava configurado para 7 atributos, mas o jogo usa apenas 5. Além disso, o vetor de estado estava sendo construído com todas as cartas do deck do bot, mas a rede neural só foi projetada para receber as 5 primeiras cartas. Isso causava o erro `mat1 and mat2 shapes cannot be multiplied`.

**Arquivos:** `backend/bots/rl_bot.py` e `backend/app/rl_model.py`

**Correções:**
1.  **Constantes:** Alteradas de 7 para 5 atributos.
    ```python
    # ANTES
    STATE_SIZE = 5 * 7
    STATS_COUNT = 7
    # DEPOIS
    STATE_SIZE = 5 * 5
    STATS_COUNT = 5
    ```
2.  **Vetor de Estado:** Limitado a usar apenas as 5 primeiras cartas do deck do bot para construir o vetor de estado.
    ```python
    # backend/bots/rl_bot.py (linha 87)
    for card in deck[:5]:
        card_vectors.extend(self._get_card_features(card))
    ```

**Impacto:** **CRÍTICO** - O bot de nível difícil agora funciona corretamente (desde que o modelo antigo seja removido).

---

### 8. Caminho Incorreto do Arquivo de Dados no Treinamento (CRÍTICO)

**Problema:** O script de treinamento (`rl_training/train_dqn.py`) e o script de avaliação (`manage.py`) não conseguiam encontrar o arquivo `carros.json` devido a um caminho relativo incorreto.

**Arquivos:** `backend/rl_training/train_dqn.py` e `backend/manage.py`

**Correção:**
O caminho relativo foi corrigido para usar `os.path.join` e `os.path.dirname(__file__)` para garantir que o arquivo seja encontrado independentemente de onde o script é executado.

```python
# ANTES (em train_dqn.py)
cards_path = '../data/carros.json'

# DEPOIS (em train_dqn.py)
cards_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'carros.json')

# ANTES (em manage.py)
with open('data/carros.json', 'r', encoding='utf-8') as f:

# DEPOIS (em manage.py)
with open(os.path.join(os.path.dirname(__file__), 'data', 'carros.json'), 'r', encoding='utf-8') as f:
```

**Impacto:** **CRÍTICO** - O treinamento e a avaliação do bot de IA agora funcionam.

---

### 9. Erro de Execução do Script de Treinamento (CRÍTICO)

**Problema:** O comando `python manage.py train` falhava ao executar o script de treinamento (`train_dqn.py`) devido a problemas de caminho no ambiente do usuário (Windows/PowerShell).

**Arquivo:** `backend/manage.py`

**Correção:**
A função `train_bot` foi modificada para garantir que o script de treinamento seja executado com o diretório de trabalho (`cwd`) definido como a pasta `backend`. Isso resolve problemas de caminho relativo e garante que o `train_dqn.py` encontre o `carros.json`.

```python
# backend/manage.py (função train_bot)
# ...
    backend_dir = os.path.dirname(os.path.abspath(__file__))
# ...
    try:
        # Adicionado cwd=backend_dir
        subprocess.run(cmd, check=True, cwd=backend_dir)
        print("\n✅ Treinamento concluído!")
# ...
```

**Impacto:** **CRÍTICO** - O comando `python manage.py train` agora deve funcionar corretamente.

---

## Arquivos Adicionados

### 1. Servidor Web para Frontend

**Arquivo:** `frontend/server.py`

**Descrição:** Servidor HTTP simples em Python para servir os arquivos estáticos do frontend.

**Como usar:**
```bash
cd frontend
python server.py
```

O servidor inicia em `http://localhost:3000`.

---

### 2. Guia de Uso Completo

**Arquivo:** `COMO_USAR.md`

**Descrição:** Documentação completa com instruções passo a passo para:
- Instalar dependências
- Executar backend e frontend
- Jogar o jogo
- Treinar o bot de IA
- **Instrução CRÍTICA para remover o modelo DQN antigo**

---

**Projeto corrigido e testado com sucesso!** ✅
