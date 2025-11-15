# 🚀 Guia de Início Rápido - Super Trunfo IA

Este guia irá ajudá-lo a executar o projeto em menos de 5 minutos.

## Passo 1: Pré-requisitos

Certifique-se de ter instalado:
- Python 3.9 ou superior
- Um navegador web moderno

## Passo 2: Iniciar o Backend

Abra um terminal e execute:

```bash
cd supertrunfo_ia/backend
pip install fastapi uvicorn pydantic
python3 -m uvicorn app.main:app --reload
```

Você verá:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

✅ Backend rodando!

## Passo 3: Iniciar o Frontend

Abra um **novo terminal** e execute:

```bash
cd supertrunfo_ia/frontend/public
python3 -m http.server 3000
```

Você verá:
```
Serving HTTP on 0.0.0.0 port 3000
```

✅ Frontend rodando!

## Passo 4: Jogar

Abra seu navegador e acesse:

```
http://localhost:3000
```

## Como Jogar

1. Clique em **"Começar Jogo"**
2. Selecione a dificuldade (Fácil, Médio ou Difícil)
3. Escolha uma carta do seu deck
4. Selecione o atributo que você quer comparar
5. Clique em **"Jogar Rodada"**
6. Veja o resultado e continue jogando!

## Atributos das Cartas

- **HP (Potência)**: Maior é melhor
- **Torque**: Maior é melhor
- **Peso**: Menor é melhor ⚠️
- **0-100 km/h**: Menor tempo é melhor ⚠️
- **Velocidade Máxima**: Maior é melhor

## Níveis de Dificuldade

- **Fácil**: Bot usa heurística simples
- **Médio**: Bot simula jogadas com Monte Carlo
- **Difícil**: Bot usa aprendizado por reforço

## Problemas?

Se encontrar algum erro:

1. Verifique se ambos os servidores estão rodando
2. Confirme que as portas 8000 e 3000 estão livres
3. Veja os logs nos terminais para mensagens de erro

## Documentação Completa

- `README.md`: Documentação principal
- `API_DOCUMENTATION.md`: Detalhes da API REST

Divirta-se jogando! 🎮🏎️
