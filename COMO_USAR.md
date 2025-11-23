# Como Usar o Super Trunfo IA

Este documento fornece instruções completas para executar o projeto Super Trunfo IA, incluindo backend e frontend.

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.8 ou superior**
- **pip** (gerenciador de pacotes Python)

## Estrutura do Projeto

O projeto está organizado em duas partes principais:

```
Projeto_IntegradorVI/
├── backend/          # API REST (FastAPI)
│   ├── app/         # Código da aplicação
│   ├── bots/        # Bots de IA
│   ├── data/        # Dados (cartas, modelos)
│   └── requirements.txt
└── frontend/        # Interface Web
    ├── public/      # Arquivos estáticos (HTML, CSS, JS)
    └── server.py    # Servidor HTTP
```

## Instalação

### Passo 1: Instalar Dependências do Backend

Navegue até a pasta do backend e instale as dependências:

```bash
cd backend
pip install -r requirements.txt
```

**Nota:** A instalação do PyTorch pode demorar alguns minutos dependendo da sua conexão.

### Passo 2: Verificar Instalação

Verifique se todas as dependências foram instaladas corretamente:

```bash
python -c "import fastapi, torch, numpy; print('✅ Todas as dependências instaladas!')"
```

## Antes de Executar (CRÍTICO)

O modelo de IA (`dqn_model.pth`) que pode estar na sua pasta `backend/data/` foi treinado com uma versão anterior do código e é **incompatível** com as correções aplicadas.

Para evitar o erro de dimensão (`mat1 and mat2 shapes cannot be multiplied`), você **DEVE** remover este arquivo antes de iniciar o backend:

```bash
cd backend/data
rm dqn_model.pth
```

Se você quiser o bot de IA treinado, precisará **treinar um novo modelo** usando o comando de treinamento após iniciar o projeto (veja seção "Treinando o Bot de IA").

## Executando o Projeto

Para executar o projeto completo, você precisa iniciar **dois servidores** em terminais separados:

### Terminal 1: Backend (API)

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Você verá uma mensagem como:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

O backend estará disponível em: **http://localhost:8000**

Para ver a documentação interativa da API, acesse: **http://localhost:8000/docs**

### Terminal 2: Frontend (Interface Web)

Abra um **novo terminal** e execute:

```bash
cd frontend
python server.py
```

Você verá uma mensagem como:

```
╔══════════════════════════════════════════════════════════╗
║          Super Trunfo IA - Frontend Server              ║
╚══════════════════════════════════════════════════════════╝

  🌐 Servidor rodando em: http://localhost:3000
  📁 Servindo arquivos de: /caminho/para/frontend/public

  ⚠️  Certifique-se de que o backend está rodando em:
     http://localhost:8000
```

O frontend estará disponível em: **http://localhost:3000**

## Jogando

1. Abra seu navegador e acesse **http://localhost:3000**
2. Clique em **"Começar Jogo"**
3. Selecione a dificuldade:
   - **FÁCIL**: Bot com estratégia simples baseada em pesos
   - **MÉDIO**: Bot usando Monte Carlo Tree Search (MCTS)
   - **DIFÍCIL**: Bot com Deep Q-Network (DQN) - Inteligência Artificial avançada
4. Selecione uma carta do seu deck
5. Escolha o atributo que deseja comparar
6. Clique em **"Jogar Rodada"**
7. Veja o resultado e continue jogando até acabarem as cartas!

## Níveis de Dificuldade

### Fácil (Weighted Bot)
O bot escolhe cartas baseado em pesos simples dos atributos. É previsível e fácil de vencer.

### Médio (MCTS Bot)
Utiliza simulações de Monte Carlo para escolher a melhor jogada. Mais desafiador que o nível fácil.

### Difícil (RL Bot - DQN)
Usa uma rede neural treinada com Deep Q-Learning. Este bot aprende estratégias complexas e é o mais difícil de vencer.

**Nota:** Se o modelo DQN não estiver treinado (`dqn_model.pth` não existe), o bot funcionará com pesos aleatórios iniciais.

## Treinando o Bot de IA (Opcional)

Se você quiser treinar o bot de nível difícil, use o script de gerenciamento:

```bash
cd backend
python manage.py train --episodes 10000
```

Isso criará o arquivo `backend/data/dqn_model.pth` com o modelo treinado.

Para avaliar o desempenho do bot:

```bash
python manage.py evaluate
```

## Testando a API Manualmente

Você pode testar a API usando `curl` ou ferramentas como Postman:

### Verificar saúde da API

```bash
curl http://localhost:8000/health
```

### Obter baralho completo

```bash
curl http://localhost:8000/deck
```

### Iniciar um jogo

```bash
curl -X POST http://localhost:8000/game/start \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "médio"}'
```

## Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'fastapi'"

**Solução:** Instale as dependências do backend:
```bash
cd backend
pip install -r requirements.txt
```

### Erro: "Address already in use"

**Solução:** Algum processo já está usando a porta 8000 ou 3000. Você pode:

1. Parar o processo existente
2. Ou usar outra porta:

```bash
# Backend em outra porta
uvicorn app.main:app --port 8001

# Frontend em outra porta (edite server.py e mude PORT = 3001)
```

### Frontend não conecta ao backend

**Verifique:**
1. O backend está rodando em http://localhost:8000?
2. Não há erros no console do navegador (F12)
3. O CORS está configurado corretamente no backend

### Bot de nível "difícil" joga aleatoriamente

**Motivo:** O modelo DQN não foi treinado ainda.

**Solução:** Treine o modelo ou aceite que ele jogará com pesos aleatórios:
```bash
cd backend
python manage.py train --episodes 10000
```

## Parando os Servidores

Para parar qualquer servidor, pressione **Ctrl+C** no terminal correspondente.

## Documentação Adicional

- **API Documentation:** http://localhost:8000/docs (quando o backend estiver rodando)
- **Arquivo de documentação da API:** `API_DOCUMENTATION.md`
- **Mudanças recentes:** `ANTES_DEPOIS.txt`

## Suporte

Se encontrar problemas, verifique:

1. Todas as dependências estão instaladas
2. Ambos os servidores (backend e frontend) estão rodando
3. As portas 8000 e 3000 estão livres
4. Você está na pasta correta ao executar os comandos

## Próximos Passos

Após dominar o jogo, você pode:

- Treinar o bot de IA com mais episódios para melhorar sua performance
- Modificar os bots existentes para criar novas estratégias
- Adicionar novas cartas ao baralho em `backend/data/carros.json`
- Personalizar a interface em `frontend/public/`

Divirta-se jogando Super Trunfo IA! 🎮🚗
