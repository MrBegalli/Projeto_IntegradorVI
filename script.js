// --- Dados do baralho de carros ---
const DECK = [
    { nome: 'Falcon GT', pais: 'EUA', velocidade: 320, resistencia: 78, motor: 480, preco: 420000 },
    { nome: 'Veloce S', pais: 'Itália', velocidade: 330, resistencia: 70, motor: 520, preco: 690000 },
    { nome: 'Strasse RS', pais: 'Alemanha', velocidade: 305, resistencia: 85, motor: 450, preco: 510000 },
    { nome: 'Thunder R', pais: 'Japão', velocidade: 300, resistencia: 88, motor: 430, preco: 290000 },
    { nome: 'Aurora X', pais: 'Suécia', velocidade: 310, resistencia: 92, motor: 470, preco: 580000 },
    { nome: 'Roadmaster V8', pais: 'EUA', velocidade: 280, resistencia: 90, motor: 400, preco: 220000 },
    { nome: 'Corsa GTi', pais: 'Brasil', velocidade: 240, resistencia: 72, motor: 220, preco: 120000 },
    { nome: 'Tourer Hybrid', pais: 'Japão', velocidade: 230, resistencia: 95, motor: 200, preco: 160000 },
    { nome: 'Riviera LX', pais: 'França', velocidade: 260, resistencia: 80, motor: 260, preco: 240000 },
    { nome: 'Monaco V12', pais: 'Itália', velocidade: 340, resistencia: 68, motor: 700, preco: 1500000 },
    { nome: 'Super Trunfo', pais: 'Mundo', velocidade: 999, resistencia: 999, motor: 999, preco: 999999999, supertrunfo: true }
];

// Mapeamento dos atributos para exibição
const ATTRIBUTES = {
    velocidade: 'Velocidade',
    resistencia: 'Resistência',
    motor: 'Motor',
    preco: 'Preço'
};

// --- Variáveis de Estado do Jogo ---
let playerDeck = [];
let aiDeck = [];
let playerCard, aiCard;
let isPlayerTurn = true, isGameActive = false;
let playerScore = 0, aiScore = 0;
let selectedCardIndex = 0;
const winningScore = 5;
let gameDifficulty = 'fácil';

// --- Elementos do DOM ---
const gameStatusEl = document.getElementById('gameStatus');
const startGameBtn = document.getElementById('startGameBtn');
const playerCardEl = document.getElementById('playerCard');
const aiCardEl = document.getElementById('aiCard');
const playerDeckCountEl = document.getElementById('playerDeckCount');
const aiDeckCountEl = document.getElementById('aiDeckCount');
const playerScoreEl = document.getElementById('playerScore');
const aiScoreEl = document.getElementById('aiScore');
const resultMessageEl = document.getElementById('resultMessage');
const fullDeckContainer = document.getElementById('fullDeckContainer');
const fullDeckGrid = document.getElementById('fullDeckGrid');
const gameContainer = document.getElementById('gameContainer');
const difficultyMenu = document.getElementById('difficultyMenu');
const playerDeckContainer = document.getElementById('playerDeckContainer');
const playerCardNameEl = document.getElementById('playerCardName');
const playerCardImageEl = document.getElementById('playerCardImage');
const playerAttributesList = document.getElementById('playerAttributes');

// --- Função para obter caminho da imagem ---
const getCardImagePath = (cardName) => `images/${cardName}.jpg`;

// --- Funções auxiliares ---
const shuffle = (array) => {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
};

/**
 * Renderiza todas as cartas do baralho completo.
 * (Sem alteração)
 */
const renderFullDeck = () => {
    fullDeckGrid.innerHTML = '';
    DECK.forEach(card => {
        const cardEl = document.createElement('div');
        cardEl.className = 'deck-view-card';
        cardEl.innerHTML = `
            <h3 class="font-bold mb-2">${card.nome}</h3>
            <img src="${getCardImagePath(card.nome)}" alt="Imagem do ${card.nome}" class="mx-auto rounded-lg">
            <ul class="mt-2 text-sm text-left">
                <li>${ATTRIBUTES.velocidade}: <span class="font-semibold text-blue-400">${card.velocidade.toLocaleString('pt-BR')}</span></li>
                <li>${ATTRIBUTES.resistencia}: <span class="font-semibold text-red-400">${card.resistencia.toLocaleString('pt-BR')}</span></li>
                <li>${ATTRIBUTES.motor}: <span class="font-semibold text-green-400">${card.motor.toLocaleString('pt-BR')}</span></li>
                <li>${ATTRIBUTES.preco}: <span class="font-semibold text-yellow-400">R$ ${card.preco.toLocaleString('pt-BR')}</span></li>
            </ul>
        `;
        fullDeckGrid.appendChild(cardEl);
    });
};

/**
 * Distribui as cartas para o jogador e a IA.
 * (Sem alteração)
 */
const dealCards = () => {
    // Cria uma cópia do baralho e embaralha
    const shuffledDeck = [...DECK];
    shuffle(shuffledDeck);
    
    // Divide o baralho entre o jogador e a IA
    playerDeck = shuffledDeck.slice(0, Math.ceil(shuffledDeck.length / 2));
    aiDeck = shuffledDeck.slice(Math.ceil(shuffledDeck.length / 2));
};

/**
 * Renderiza a visualização do deck do jogador. (NOVO)
 */
const renderPlayerDeck = () => {
    playerDeckContainer.innerHTML = ''; // Limpa o deck anterior
    
    playerDeck.forEach((card, index) => {
        const cardEl = document.createElement('div');
        cardEl.className = `player-deck-card ${index === selectedCardIndex ? 'selected-deck-card' : ''} ${card.supertrunfo ? 'supertrunfo-deck-card' : ''}`;
        cardEl.dataset.index = index;
        cardEl.title = card.nome;
        cardEl.innerHTML = `
            <span class="card-name-short">${card.nome}</span>
            <img src="${getCardImagePath(card.nome)}" alt="${card.nome}" style="image-rendering: pixelated; margin-top: 5px; border: 1px solid #555;">
        `;
        cardEl.addEventListener('click', () => selectCard(index));
        playerDeckContainer.appendChild(cardEl);
    });
};

/**
 * Seleciona a carta a ser jogada. (NOVO)
 * @param {number} index - O índice da carta no deck do jogador.
 */
const selectCard = (index) => {
    if (!isGameActive || !isPlayerTurn) return;
    selectedCardIndex = index;
    renderPlayerDeck(); // Renderiza novamente para atualizar a seleção
    
    // Atualiza a carta principal com a carta selecionada
    playerCard = playerDeck[selectedCardIndex];
    showPlayerCard();
    gameStatusEl.textContent = 'Carta selecionada. Escolha um atributo ou mude de carta.';
};

/**
 * Atualiza a contagem de cartas e o placar na tela.
 * (Sem alteração)
 */
const updateGameStats = () => {
    playerDeckCountEl.textContent = playerDeck.length;
    aiDeckCountEl.textContent = aiDeck.length;
    playerScoreEl.textContent = playerScore;
    aiScoreEl.textContent = aiScore;
};

/**
 * Vira a carta do jogador para a frente e exibe seus dados.
 * (Atualizado para usar a carta selecionada e novos elementos)
 */
const showPlayerCard = () => {
    if (!playerCard) return;
    playerCardNameEl.textContent = playerCard.nome;
    
    // Adiciona uma classe específica se a carta for o Super Trunfo
    const playerCardContainerEl = document.getElementById('playerCardContainer');
    playerCardContainerEl.classList.toggle('supertrunfo-card', !!playerCard.supertrunfo);
    playerCardImageEl.src = getCardImagePath(playerCard.nome);
    playerAttributesList.innerHTML = '';
    
    // Cria os itens de atributo clicáveis
    for (const key in ATTRIBUTES) {
        const li = document.createElement('li');
        li.className = 'attribute-item flex justify-between p-2 rounded-md';
        li.dataset.attribute = key;
        li.innerHTML = `<span>${ATTRIBUTES[key]}:</span> <span class="font-semibold">${playerCard[key].toLocaleString('pt-BR')}</span>`;
        li.addEventListener('click', handlePlayerTurn);
        playerAttributesList.appendChild(li);
    }
    // Garante que a carta principal do jogador esteja sempre virada
    playerCardEl.classList.remove('flipped');
};

/**
 * Vira a carta da IA para a frente e exibe seus dados.
 * (Alterado para não mostrar a frente até a comparação)
 */
const showAiCard = () => {
    aiCard = aiDeck[0];
    
    // Ocultar a frente da IA
    document.getElementById('aiCardName').textContent = '?';
    document.getElementById('aiCardImage').src = 'images/placeholder.jpg'; // placeholder opcional
    aiCardEl.classList.add('flipped');
};

/**
 * Revela os valores da IA. (NOVO)
 * Esta função é chamada *durante* o compareCards, após a escolha do atributo.
 */
const revealAiCard = () => {
    document.getElementById('aiCardName').textContent = aiCard.nome;
    const aiCardContainerEl = document.getElementById('aiCardContainer');
    aiCardContainerEl.classList.toggle('supertrunfo-card', !!aiCard.supertrunfo);
    document.getElementById('aiCardImage').src = getCardImagePath(aiCard.nome);
    // Atualiza atributos
    const attrMap = { velocidade: 'aiVelocidade', resistencia: 'aiResistencia', motor: 'aiMotor', preco: 'aiPreco' };
    for (const key in attrMap) {
        const el = document.getElementById(attrMap[key]);
        if (el) {
            const span = el.querySelector('span');
            span.textContent = aiCard[key].toLocaleString('pt-BR');
        }
    }
    aiCardEl.classList.remove('flipped');
};

/**
 * Compara os atributos e determina o vencedor da rodada.
 * @param {string} attribute - O atributo selecionado para a comparação.
 */
const compareCards = (attribute) => {
    // Vira a carta da IA para revelar o resultado
    revealAiCard(); // Chama a nova função para revelar a carta
    
    // Remove a seleção dos atributos do jogador
    document.querySelectorAll('#playerAttributes .attribute-item').forEach(el => {
        el.classList.remove('selected');
    });

    // Adiciona um pequeno atraso para a animação
    setTimeout(() => {
        let winnerMessage = '';
        let winner = null;

        // Limpa o estado de vencedor/perdedor
        document.querySelectorAll('.attribute-item').forEach(el => {
            el.classList.remove('winner', 'loser');
        });

        // Destaca os atributos comparados
        const playerAttrEl = document.querySelector(`#playerAttributes li[data-attribute="${attribute}"]`);
        const aiAttrEl = document.querySelector(`#aiCard ul li[id="ai${attribute.charAt(0).toUpperCase() + attribute.slice(1)}"]`);

        // Lógica do SUPERTRUNFO
        if (playerCard.supertrunfo && !aiCard.supertrunfo) {
            winner = 'player';
            winnerMessage = 'SUPER TRUNFO! Você venceu a rodada!';
            playerScore++;
            if(playerAttrEl) playerAttrEl.classList.add('winner');
            if(aiAttrEl) aiAttrEl.classList.add('loser');
        } else if (aiCard.supertrunfo && !playerCard.supertrunfo) {
            winner = 'ai';
            winnerMessage = 'SUPER TRUNFO! A IA venceu a rodada!';
            aiScore++;
            if(playerAttrEl) playerAttrEl.classList.add('loser');
            if(aiAttrEl) aiAttrEl.classList.add('winner');
        } else {
            // Comparação normal dos valores
            const playerValue = playerCard[attribute];
            const aiValue = aiCard[attribute];
            
            if (playerValue > aiValue) {
                winner = 'player';
                winnerMessage = 'Você venceu a rodada!';
                playerScore++;
                if(playerAttrEl) playerAttrEl.classList.add('winner');
                if(aiAttrEl) aiAttrEl.classList.add('loser');
            } else if (aiValue > playerValue) {
                winner = 'ai';
                winnerMessage = 'A IA venceu a rodada!';
                aiScore++;
                if(playerAttrEl) playerAttrEl.classList.add('loser');
                if(aiAttrEl) aiAttrEl.classList.add('winner');
            } else {
                winner = 'draw';
                winnerMessage = 'Empate!';
                if(playerAttrEl) playerAttrEl.classList.add('selected');
                if(aiAttrEl) aiAttrEl.classList.add('selected');
            }
        }
        
        resultMessageEl.textContent = winnerMessage;
        
        // Distribui as cartas
        moveCards(winner);
        
        // Verifica o fim do jogo
        checkEndGame();
        
    }, 1000);
};

/**
 * Move as cartas para o baralho do vencedor da rodada.
 * @param {string} winner - O vencedor da rodada ('player', 'ai', 'draw').
 */
const moveCards = (winner) => {
    // Remove as cartas de suas posições atuais (playerCard é a carta selecionada do deck)
    const playerCardToMove = playerDeck.splice(selectedCardIndex, 1)[0];
    const aiCardToMove = aiDeck.shift();

    if (winner === 'player') {
        playerDeck.push(playerCardToMove, aiCardToMove);
    } else if (winner === 'ai') {
        aiDeck.push(aiCardToMove, playerCardToMove);
    } else { // Empate, as cartas voltam para o final de seus decks
        playerDeck.push(playerCardToMove);
        aiDeck.push(aiCardToMove);
    }
    
    // Garante que o índice da carta selecionada seja válido ou volte para a primeira carta
    selectedCardIndex = Math.min(selectedCardIndex, playerDeck.length > 0 ? playerDeck.length - 1 : 0);

    updateGameStats();
    renderPlayerDeck();
};

/**
 * Verifica se o jogo terminou.
 * (Sem alteração)
 */
const checkEndGame = () => {
    if (playerScore >= winningScore || aiDeck.length === 0) {
        endGame('Você venceu!');
    } else if (aiScore >= winningScore || playerDeck.length === 0) {
        endGame('A IA venceu!');
    } else {
        // Inicia a próxima rodada
        setTimeout(startRound, 2000); // Pequeno atraso antes de começar a próxima rodada
    }
};

/**
 * Encerra o jogo e exibe a mensagem final.
 * (Removido o botão de reinício em endGame, será manipulado por resetGame)
 * @param {string} message - A mensagem de vitória ou derrota.
 */
const endGame = (message) => {
    isGameActive = false;
    gameStatusEl.textContent = message;
    gameStatusEl.classList.remove('text-gray-400', 'text-green-500', 'text-yellow-400', 'text-red-500');
    gameStatusEl.classList.add(message.includes('Você') ? 'text-green-500' : 'text-red-500');
    resultMessageEl.textContent = '';
    
    // Exibe o botão de reinício (adicionado aqui para ser removido no reset)
    const restartBtn = document.createElement('button');
    restartBtn.textContent = 'Jogar Novamente';
    restartBtn.className = 'mt-4 bg-blue-600 text-white font-bold py-3 px-6 rounded-full shadow-lg hover:bg-blue-700 transform hover:scale-105 transition-all duration-300';
    restartBtn.onclick = resetGame;
    document.querySelector('.text-center').appendChild(restartBtn);
};

/**
 * Reseta o jogo para o estado inicial.
 * (Atualizado para mostrar o menu de dificuldade após o reset)
 */
const resetGame = () => {
    playerScore = 0;
    aiScore = 0;
    playerDeck = [];
    aiDeck = [];
    selectedCardIndex = 0;

    // Remove o botão de reinício
    const restartBtn = document.querySelector('.text-center button:last-of-type');
    if (restartBtn) restartBtn.remove();
    
    // Exibe o baralho completo e o botão de iniciar, oculta o jogo e o menu
    fullDeckContainer.classList.remove('hidden');
    gameContainer.classList.add('hidden');
    difficultyMenu.classList.add('hidden'); // Oculta o menu
    // Mantém o botão centralizado (inline-block para respeitar text-center)
    startGameBtn.style.display = 'inline-block';
    
    gameStatusEl.textContent = 'Analise o baralho e clique em "Começar Jogo" para iniciar!';
    gameStatusEl.classList.remove('text-green-500', 'text-red-500', 'text-yellow-400');
    gameStatusEl.classList.add('text-gray-400');
    
    updateGameStats();
    renderFullDeck();
    playerDeckContainer.innerHTML = ''; // Limpa o deck do jogador
    document.getElementById('aiCardContainer').classList.remove('supertrunfo-card');
    document.getElementById('playerCardContainer').classList.remove('supertrunfo-card');
};

/**
 * Inicia a rodada.
 * (Atualizado para lidar com a seleção de carta do jogador)
 */
const startRound = () => {
    resultMessageEl.textContent = '';
    
    // Garante que a carta da IA esteja virada para baixo no início da rodada
    aiCardEl.classList.add('flipped');

    // Define as cartas atuais
    aiCard = aiDeck[0];
    playerCard = playerDeck[selectedCardIndex]; 
    
    // Atualiza a visualização da carta do jogador e da IA (agora virada para baixo)
    showPlayerCard();
    showAiCard(); 

    // Define o turno inicial
    if (isPlayerTurn) {
        gameStatusEl.textContent = 'Sua vez! Selecione sua carta e escolha um atributo.';
        gameStatusEl.classList.remove('text-red-500', 'text-yellow-400');
        gameStatusEl.classList.add('text-green-500');
    } else {
        gameStatusEl.textContent = 'Vez da IA...';
        gameStatusEl.classList.remove('text-green-500', 'text-red-500');
        gameStatusEl.classList.add('text-yellow-400');
        setTimeout(handleAITurn, 1500); // Pequeno atraso para a IA
    }
    
    // Limpa os destaques de rodadas anteriores
    document.querySelectorAll('.attribute-item').forEach(el => {
        el.classList.remove('selected', 'winner', 'loser');
    });
};

/**
 * Mostra o menu de dificuldade. (NOVO)
 */
const showDifficultyMenu = () => {
    fullDeckContainer.classList.add('hidden');
    startGameBtn.style.display = 'none';
    difficultyMenu.classList.remove('hidden');
    gameStatusEl.textContent = 'Escolha o nível de dificuldade.';
    gameStatusEl.classList.remove('text-gray-400');
    gameStatusEl.classList.add('text-yellow-400');
};

/**
 * Inicia o jogo após a seleção de dificuldade. (NOVO)
 * @param {string} difficulty - A dificuldade selecionada.
 */
const selectDifficulty = (difficulty) => {
    gameDifficulty = difficulty;
    isGameActive = true;
    difficultyMenu.classList.add('hidden');
    gameContainer.classList.remove('hidden'); // Mostra a interface do jogo
    
    dealCards();
    updateGameStats();
    
    // Inicia a música de fundo
    musicPlayer.start();
    
    // Seleciona a primeira carta do deck do jogador por padrão e renderiza
    selectedCardIndex = 0;
    renderPlayerDeck();
    
    startRound();
};

/**
 * Manipula a jogada do jogador.
 * @param {Event} event - O evento de clique.
 */
const handlePlayerTurn = (event) => {
    if (!isPlayerTurn || !isGameActive) return;

    // Remove a seleção de todos os atributos
    document.querySelectorAll('#playerAttributes .attribute-item').forEach(el => {
        el.classList.remove('selected', 'winner', 'loser');
    });

    // Se a carta for o Super Trunfo, ignora o clique e vence automaticamente
    if (playerCard.supertrunfo) {
        gameStatusEl.textContent = 'SUPER TRUNFO! Você vence a rodada!';
        compareCards(null);
        isPlayerTurn = false;
        return;
    }
    
    // Adiciona a seleção ao item clicado
    event.currentTarget.classList.add('selected');

    const attribute = event.currentTarget.dataset.attribute;
    compareCards(attribute);

    isPlayerTurn = false;
};


// --- Minimax e Lógica da IA (Sem Alteração na Estrutura, mas o uso da dificuldade seria aqui) ---

/**
 * Funções para a IA Minimax
 */

const minimax = (depth, isMaximizingPlayer, currentAiDeck, currentPlayerDeck) => {
    // ... (Minimax implementation as before)
    if (depth === 0 || currentAiDeck.length === 0 || currentPlayerDeck.length === 0) {
        return currentAiDeck.length - currentPlayerDeck.length;
    }

    if (isMaximizingPlayer) {
        let maxEval = -Infinity;
        let aiSimulatedCard = currentAiDeck[0];

        for (const attribute in ATTRIBUTES) {
            const aiValue = aiSimulatedCard.supertrunfo ? Infinity : aiSimulatedCard[attribute];
            
            let evaluation;
            let playerBestAttribute = getBestPlayerMove(currentPlayerDeck[0], aiSimulatedCard);
            const playerValue = currentPlayerDeck[0].supertrunfo ? -Infinity : currentPlayerDeck[0][playerBestAttribute];

            let nextAiDeck = [...currentAiDeck];
            let nextPlayerDeck = [...currentPlayerDeck];

            if (aiValue > playerValue) {
                nextAiDeck.push(nextAiDeck.shift(), nextPlayerDeck.shift());
            } else if (playerValue > aiValue) {
                nextPlayerDeck.push(nextPlayerDeck.shift(), nextAiDeck.shift());
            } else {
                nextAiDeck.push(nextAiDeck.shift());
                nextPlayerDeck.push(nextPlayerDeck.shift());
            }

            evaluation = minimax(depth - 1, false, nextAiDeck, nextPlayerDeck);
            maxEval = Math.max(maxEval, evaluation);
        }
        return maxEval;
    } 
    else {
        let minEval = +Infinity;
        let playerSimulatedCard = currentPlayerDeck[0];

        for (const attribute in ATTRIBUTES) {
            const playerValue = playerSimulatedCard.supertrunfo ? Infinity : playerSimulatedCard[attribute];
            
            let evaluation;
            let aiBestAttribute = getBestAiMove(currentAiDeck[0], playerSimulatedCard);
            const aiValue = currentAiDeck[0].supertrunfo ? -Infinity : currentAiDeck[0][aiBestAttribute];

            let nextAiDeck = [...currentAiDeck];
            let nextPlayerDeck = [...currentPlayerDeck];

            if (playerValue > aiValue) {
                nextPlayerDeck.push(nextPlayerDeck.shift(), nextAiDeck.shift());
            } else if (aiValue > playerValue) {
                nextAiDeck.push(nextAiDeck.shift(), nextPlayerDeck.shift());
            } else {
                nextAiDeck.push(nextAiDeck.shift());
                nextPlayerDeck.push(nextPlayerDeck.shift());
            }

            evaluation = minimax(depth - 1, true, nextAiDeck, nextPlayerDeck);
            minEval = Math.min(minEval, evaluation);
        }
        return minEval;
    }
};

const getBestPlayerMove = (playerCard, aiCard) => {
    // ... (getBestPlayerMove implementation as before)
    let bestAttribute = null;
    let maxAdvantage = -Infinity;

    for (const attr in ATTRIBUTES) {
        const playerValue = playerCard.supertrunfo ? Infinity : playerCard[attr];
        const aiValue = aiCard.supertrunfo ? -Infinity : aiCard[attr];
        
        const advantage = playerValue - aiValue;

        if (advantage > maxAdvantage) {
            maxAdvantage = advantage;
            bestAttribute = attr;
        }
    }
    return bestAttribute;
};

const getBestAiMove = (aiCard, playerCard) => {
    // ... (getBestAiMove implementation as before)
    let bestAttribute = null;
    let maxAdvantage = -Infinity;

    for (const attr in ATTRIBUTES) {
        const aiValue = aiCard.supertrunfo ? Infinity : aiCard[attr];
        const playerValue = playerCard.supertrunfo ? -Infinity : playerCard[attr];

        const advantage = aiValue - playerValue;

        if (advantage > maxAdvantage) {
            maxAdvantage = advantage;
            bestAttribute = attr;
        }
    }
    return bestAttribute;
};


const getBestMinimaxMove = () => {
    // A Lógica da IA aqui seria ajustada com base na 'gameDifficulty'
    // Por exemplo:
    // 'fácil': Escolhe um atributo aleatório ou apenas o melhor para a rodada atual.
    // 'médio': Usa o getBestAiMove (melhor jogada gananciosa, 1 turno).
    // 'difícil': Usa o Minimax com profundidade 2.
    // 'impossível': Usa o Minimax com profundidade 3 ou mais.

    if (aiDeck[0].supertrunfo) {
        return Object.keys(ATTRIBUTES)[0]; 
    }
    
    // Lógica Simplificada para demonstrar o conceito:
    let bestMove = getBestAiMove(aiDeck[0], playerDeck[selectedCardIndex]); // Jogada gananciosa

    if (gameDifficulty === 'fácil') {
         // Escolhe aleatoriamente para 'Fácil'
        const attributesKeys = Object.keys(ATTRIBUTES);
        bestMove = attributesKeys[Math.floor(Math.random() * attributesKeys.length)];
    } else if (gameDifficulty === 'médio') {
        // A jogada gananciosa (getBestAiMove) é usada.
        // Já está definida acima
    } else if (gameDifficulty === 'difícil' || gameDifficulty === 'impossível') {
        // Usa Minimax para 'Difícil' e 'Impossível'
        // 'Impossível' pode ser uma profundidade maior, mas 2 já é um bom desafio.
        let maxEval = -Infinity;
        const aiSimulatedCard = aiDeck[0];
        const depth = gameDifficulty === 'impossível' ? 3 : 2; // Profundidade 3 para Impossível, 2 para Difícil

        for (const attribute in ATTRIBUTES) {
            let currentEval;
            let nextAiDeck = [...aiDeck];
            let nextPlayerDeck = [...playerDeck];

            const aiValue = nextAiDeck[0][attribute];
            // O jogador, na simulação, escolherá o melhor atributo contra a IA.
            const playerValue = nextPlayerDeck[0].supertrunfo ? Infinity : nextPlayerDeck[0][getBestPlayerMove(nextPlayerDeck[0], nextAiDeck[0])];
            
            if (aiValue > playerValue) {
                nextAiDeck.push(nextAiDeck.shift(), nextPlayerDeck.shift());
            } else if (playerValue > aiValue) {
                nextPlayerDeck.push(nextPlayerDeck.shift(), nextAiDeck.shift());
            } else {
                nextAiDeck.push(nextAiDeck.shift());
                nextPlayerDeck.push(nextPlayerDeck.shift());
            }
            
            // Chamada recursiva para o Minimax
            currentEval = minimax(depth - 1, false, nextAiDeck, nextPlayerDeck); 
            
            if (currentEval > maxEval) {
                maxEval = currentEval;
                bestMove = attribute;
            }
        }
    }
    
    return bestMove;
};


/**
 * Manipula a jogada da IA.
 * (Sem alteração, chama a função de Minimax atualizada)
 */
const handleAITurn = () => {
    let selectedAttribute = getBestMinimaxMove();

    gameStatusEl.textContent = `A IA escolheu: ${ATTRIBUTES[selectedAttribute]}!`;
    gameStatusEl.classList.remove('text-yellow-400');
    gameStatusEl.classList.add('text-red-500');

    // Destaca o atributo escolhido pela IA na carta do JOGADOR
    document.querySelectorAll('#playerAttributes .attribute-item').forEach(el => {
        el.classList.remove('selected', 'winner', 'loser');
        if (el.dataset.attribute === selectedAttribute) {
            el.classList.add('selected');
        }
    });

    compareCards(selectedAttribute);
    isPlayerTurn = true;
};

// Sistema de Música de Fundo
const musicPlayer = {
    playlist: [
        'music/Cruise Control.mp3',
        'music/Drifting With Stairs.mp3',
        'music/Uno Trails.mp3'
    ],
    currentTrack: 0,
    audio: new Audio(),
    
    // Inicia a reprodução
    start() {
        console.log('Iniciando sistema de música...');
        this.currentTrack = 0;
        this.playCurrentTrack();
    },
    
    // Toca a música atual
    playCurrentTrack() {
        // Configura o áudio
        this.audio.src = this.playlist[this.currentTrack];
        this.audio.volume = 0.5;
        this.audio.load();
        
        // Tenta tocar
        const playPromise = this.audio.play();
        if (playPromise !== undefined) {
            playPromise.catch(error => {
                console.log('Erro ao tocar, tentando novamente:', error);
                setTimeout(() => this.playCurrentTrack(), 1000);
            });
        }

        // Quando terminar, toca a próxima
        this.audio.onended = () => {
            this.currentTrack = (this.currentTrack + 1) % this.playlist.length;
            this.playCurrentTrack();
        };
    }
};

// --- Eventos ---
startGameBtn.addEventListener('click', showDifficultyMenu);
document.querySelectorAll('.difficulty-btn').forEach(button => {
    button.addEventListener('click', (event) => selectDifficulty(event.target.dataset.difficulty));
});

// Carrega o deck quando a página carrega
document.addEventListener('DOMContentLoaded', () => {
    renderFullDeck();
});