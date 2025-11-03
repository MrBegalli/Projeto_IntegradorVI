// Dados do baralho de carros em um array JavaScript
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
    // Adicionando a carta Super Trunfo
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
let isPlayerTurn = true;
let isGameActive = false;
let playerScore = 0;
let aiScore = 0;
const winningScore = 5;

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

// --- Lógica do Jogo ---

/**
 * Embaralha um array usando o algoritmo de Fisher-Yates.
 * @param {Array} array - O array a ser embaralhado.
 */
const shuffle = (array) => {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
};

/**
 * Renderiza todas as cartas do baralho completo.
 */
const renderFullDeck = () => {
    fullDeckGrid.innerHTML = ''; // Limpa a visualização anterior
    DECK.forEach(card => {
        const cardEl = document.createElement('div');
        cardEl.className = 'deck-view-card';
        cardEl.innerHTML = `
            <h3 class="font-bold mb-2">${card.nome}</h3>
            <img src="https://placehold.co/150x90/4a5568/CBD5E0?text=${encodeURIComponent(card.nome.replace(/\s/g, '+'))}" alt="Imagem do carro" class="mx-auto rounded-lg">
            <ul class="mt-2 text-sm text-left">
                <li>${ATTRIBUTES.velocidade}: <span class="font-semibold">${card.velocidade.toLocaleString('pt-BR')}</span></li>
                <li>${ATTRIBUTES.resistencia}: <span class="font-semibold">${card.resistencia.toLocaleString('pt-BR')}</span></li>
                <li>${ATTRIBUTES.motor}: <span class="font-semibold">${card.motor.toLocaleString('pt-BR')}</span></li>
                <li>${ATTRIBUTES.preco}: <span class="font-semibold">R$ ${card.preco.toLocaleString('pt-BR')}</span></li>
            </ul>
        `;
        fullDeckGrid.appendChild(cardEl);
    });
};

/**
 * Distribui as cartas para o jogador e a IA.
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
 * Atualiza a contagem de cartas e o placar na tela.
 */
const updateGameStats = () => {
    playerDeckCountEl.textContent = playerDeck.length;
    aiDeckCountEl.textContent = aiDeck.length;
    playerScoreEl.textContent = playerScore;
    aiScoreEl.textContent = aiScore;
};

/**
 * Vira a carta do jogador para a frente e exibe seus dados.
 */
const showPlayerCard = () => {
    playerCard = playerDeck[0];
    document.getElementById('playerCardName').textContent = playerCard.nome;
    
    // Adiciona uma classe específica se a carta for o Super Trunfo
    if (playerCard.supertrunfo) {
        playerCardEl.parentElement.classList.add('supertrunfo-card');
    } else {
        playerCardEl.parentElement.classList.remove('supertrunfo-card');
    }

    // Gera uma imagem de placeholder com base no nome do carro
    document.getElementById('playerCardImage').src = `https://placehold.co/200x120/4a5568/CBD5E0?text=${encodeURIComponent(playerCard.nome.replace(/\s/g, '+'))}`;

    const attributesList = document.getElementById('playerAttributes');
    attributesList.innerHTML = '';
    
    // Cria os itens de atributo clicáveis
    for (const key in ATTRIBUTES) {
        const li = document.createElement('li');
        li.className = 'attribute-item flex justify-between p-2 rounded-md';
        li.dataset.attribute = key;
        li.innerHTML = `<span>${ATTRIBUTES[key]}:</span> <span class="font-semibold">${playerCard[key].toLocaleString('pt-BR')}</span>`;
        li.addEventListener('click', handlePlayerTurn);
        attributesList.appendChild(li);
    }
    playerCardEl.classList.remove('flipped');
};

/**
 * Vira a carta da IA para a frente e exibe seus dados.
 */
const showAiCard = () => {
    aiCard = aiDeck[0];
    document.getElementById('aiCardName').textContent = aiCard.nome;
    
    // Adiciona uma classe específica se a carta for o Super Trunfo
    if (aiCard.supertrunfo) {
        aiCardEl.parentElement.classList.add('supertrunfo-card');
    } else {
        aiCardEl.parentElement.classList.remove('supertrunfo-card');
    }

    // Gera uma imagem de placeholder com base no nome do carro
    document.getElementById('aiCardImage').src = `https://placehold.co/200x120/4a5568/CBD5E0?text=${encodeURIComponent(aiCard.nome.replace(/\s/g, '+'))}`;
    // Remove classes de destaque antigas (caso tenham sobrado da rodada anterior)
    const aiAttributeItems = aiCardEl.querySelectorAll('ul .attribute-item');
    aiAttributeItems.forEach(el => el.classList.remove('selected', 'winner', 'loser'));

    const aiVelocidadeEl = document.getElementById('aiVelocidade').querySelector('span');
    aiVelocidadeEl.textContent = aiCard.velocidade.toLocaleString('pt-BR');
    
    const aiResistenciaEl = document.getElementById('aiResistencia').querySelector('span');
    aiResistenciaEl.textContent = aiCard.resistencia.toLocaleString('pt-BR');
    
    const aiMotorEl = document.getElementById('aiMotor').querySelector('span');
    aiMotorEl.textContent = aiCard.motor.toLocaleString('pt-BR');
    
    const aiPrecoEl = document.getElementById('aiPreco').querySelector('span');
    aiPrecoEl.textContent = 'R$ ' + aiCard.preco.toLocaleString('pt-BR');

    aiCardEl.classList.remove('flipped');
};

/**
 * Compara os atributos e determina o vencedor da rodada.
 * @param {string} attribute - O atributo selecionado para a comparação.
 */
const compareCards = (attribute) => {
    // Vira a carta da IA para revelar o resultado
    aiCardEl.classList.add('flipped');

    // Adiciona um pequeno atraso para a animação
    setTimeout(() => {
        let winnerMessage = '';
        let winner = null;

        // Destaca os atributos comparados
        const playerAttrEl = document.querySelector(`#playerAttributes li[data-attribute="${attribute}"]`);
        const aiAttrEl = document.querySelector(`#aiCard ul li[id="ai${attribute.charAt(0).toUpperCase() + attribute.slice(1)}"]`);

        // Adiciona a classe para mostrar o resultado da comparação
        if(playerAttrEl) playerAttrEl.classList.remove('selected');
        
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
    const playerCardToMove = playerDeck.shift();
    const aiCardToMove = aiDeck.shift();

    if (winner === 'player') {
        playerDeck.push(playerCardToMove, aiCardToMove);
    } else if (winner === 'ai') {
        aiDeck.push(aiCardToMove, playerCardToMove);
    } else { // Empate, as cartas ficam na mesa
        playerDeck.push(playerCardToMove);
        aiDeck.push(aiCardToMove);
    }
    updateGameStats();
};

/**
 * Verifica se o jogo terminou.
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
 * @param {string} message - A mensagem de vitória ou derrota.
 */
const endGame = (message) => {
    isGameActive = false;
    gameStatusEl.textContent = message;
    gameStatusEl.classList.remove('text-gray-400', 'text-green-500', 'text-yellow-400');
    gameStatusEl.classList.add(message.includes('Você') ? 'text-green-500' : 'text-red-500');

    resultMessageEl.textContent = '';
    
    // Exibe o botão de reinício
    const restartBtn = document.createElement('button');
    restartBtn.textContent = 'Jogar Novamente';
    restartBtn.className = 'mt-4 bg-blue-600 text-white font-bold py-3 px-6 rounded-full shadow-lg hover:bg-blue-700 transform hover:scale-105 transition-all duration-300';
    restartBtn.onclick = resetGame;
    document.querySelector('.text-center').appendChild(restartBtn);
};

/**
 * Reseta o jogo para o estado inicial.
 */
const resetGame = () => {
    playerScore = 0;
    aiScore = 0;
    playerDeck = [];
    aiDeck = [];

    // Remove o botão de reinício
    const restartBtn = document.querySelector('.text-center button:last-of-type');
    if (restartBtn) restartBtn.remove();
    
    fullDeckContainer.classList.remove('hidden');
    gameContainer.classList.add('hidden');
    startGameBtn.style.display = 'block';
    gameStatusEl.textContent = 'Analise o baralho e clique em "Começar Jogo" para iniciar!';
    gameStatusEl.classList.remove('text-green-500', 'text-red-500');
    gameStatusEl.classList.add('text-gray-400');
    updateGameStats();
    renderFullDeck();
};

/**
 * Inicia a rodada.
 */
const startRound = () => {
    resultMessageEl.textContent = '';
    
    // Vira as cartas para o verso
    playerCardEl.classList.add('flipped');
    aiCardEl.classList.add('flipped');

    // Pequeno atraso para a animação
    setTimeout(() => {
        showPlayerCard();
        showAiCard();

        // Define o turno inicial
        if (isPlayerTurn) {
            gameStatusEl.textContent = 'Sua vez! Escolha um atributo.';
            gameStatusEl.classList.remove('text-red-500');
            gameStatusEl.classList.add('text-green-500');
        } else {
            gameStatusEl.textContent = 'Vez da IA...';
            gameStatusEl.classList.remove('text-green-500');
            gameStatusEl.classList.add('text-yellow-400');
            setTimeout(handleAITurn, 1500); // Pequeno atraso para a IA
        }
    }, 600);
};

/**
 * Inicia o jogo, distribuindo as cartas e começando a primeira rodada.
 */
const startGame = () => {
    isGameActive = true;
    fullDeckContainer.classList.add('hidden'); // Oculta o baralho completo
    gameContainer.classList.remove('hidden'); // Mostra a interface do jogo
    dealCards();
    updateGameStats();
    startGameBtn.style.display = 'none';
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

/**
 * Funções para a IA Minimax
 */

/**
 * Função principal do algoritmo Minimax.
 * Simula jogadas futuras para determinar a melhor jogada.
 * @param {number} depth - A profundidade da simulação (quantos turnos à frente a IA "pensará").
 * @param {boolean} isMaximizingPlayer - True se for a vez da IA (jogador maximizador), False se for a vez do usuário.
 * @param {Array} currentAiDeck - Cópia do baralho da IA para a simulação.
 * @param {Array} currentPlayerDeck - Cópia do baralho do jogador para a simulação.
 * @returns {number} O valor da jogada (score).
 */
const minimax = (depth, isMaximizingPlayer, currentAiDeck, currentPlayerDeck) => {
    // Condição de parada (base case) para a recursão
    if (depth === 0 || currentAiDeck.length === 0 || currentPlayerDeck.length === 0) {
        // Retorna um score baseado no número de cartas.
        // A IA quer maximizar seu score (número de cartas), o jogador quer minimizar.
        return currentAiDeck.length - currentPlayerDeck.length;
    }

    // Turno da IA (jogador maximizador)
    if (isMaximizingPlayer) {
        let maxEval = -Infinity;
        let aiSimulatedCard = currentAiDeck[0];

        for (const attribute in ATTRIBUTES) {
            // Se for Super Trunfo, o valor é o máximo possível
            const aiValue = aiSimulatedCard.supertrunfo ? Infinity : aiSimulatedCard[attribute];
            
            let scoreEval;
            // A IA assume que o jogador vai escolher o melhor atributo
            let playerBestAttribute = getBestPlayerMove(currentPlayerDeck[0], aiSimulatedCard);
            const playerValue = currentPlayerDeck[0].supertrunfo ? -Infinity : currentPlayerDeck[0][playerBestAttribute];

            let nextAiDeck = [...currentAiDeck];
            let nextPlayerDeck = [...currentPlayerDeck];

            // Simula a comparação e move as cartas
            if (aiValue > playerValue) {
                // IA vence
                nextAiDeck.push(nextAiDeck.shift(), nextPlayerDeck.shift());
            } else if (playerValue > aiValue) {
                // Jogador vence
                nextPlayerDeck.push(nextPlayerDeck.shift(), nextAiDeck.shift());
            } else {
                // Empate
                nextAiDeck.push(nextAiDeck.shift());
                nextPlayerDeck.push(nextPlayerDeck.shift());
            }

            scoreEval = minimax(depth - 1, false, nextAiDeck, nextPlayerDeck);
            maxEval = Math.max(maxEval, scoreEval);
        }
        return maxEval;
    } 
    // Turno do Jogador (jogador minimizador)
    else {
        let minEval = +Infinity;
        let playerSimulatedCard = currentPlayerDeck[0];

        for (const attribute in ATTRIBUTES) {
            // Se for Super Trunfo, o valor é o máximo possível
            const playerValue = playerSimulatedCard.supertrunfo ? Infinity : playerSimulatedCard[attribute];
            
            let scoreEval;
            // O jogador assume que a IA vai escolher o melhor atributo
            let aiBestAttribute = getBestAiMove(currentAiDeck[0], playerSimulatedCard);
            const aiValue = currentAiDeck[0].supertrunfo ? -Infinity : currentAiDeck[0][aiBestAttribute];

            let nextAiDeck = [...currentAiDeck];
            let nextPlayerDeck = [...currentPlayerDeck];

            // Simula a comparação e move as cartas
            if (playerValue > aiValue) {
                // Jogador vence
                nextPlayerDeck.push(nextPlayerDeck.shift(), nextAiDeck.shift());
            } else if (aiValue > playerValue) {
                // IA vence
                nextAiDeck.push(nextAiDeck.shift(), nextPlayerDeck.shift());
            } else {
                // Empate
                nextAiDeck.push(nextAiDeck.shift());
                nextPlayerDeck.push(nextPlayerDeck.shift());
            }

            scoreEval = minimax(depth - 1, true, nextAiDeck, nextPlayerDeck);
            minEval = Math.min(minEval, scoreEval);
        }
        return minEval;
    }
};

/**
 * Encontra o melhor atributo para o Jogador jogar, para ser usado na simulação da IA.
 * @param {Object} playerCard - A carta do jogador na simulação.
 * @param {Object} aiCard - A carta da IA na simulação.
 * @returns {string} O melhor atributo para o jogador jogar.
 */
const getBestPlayerMove = (playerCard, aiCard) => {
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

/**
 * Encontra o melhor atributo para a IA jogar, para ser usado na simulação do jogador.
 * @param {Object} aiCard - A carta da IA na simulação.
 * @param {Object} playerCard - A carta do jogador na simulação.
 * @returns {string} O melhor atributo para a IA jogar.
 */
const getBestAiMove = (aiCard, playerCard) => {
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


/**
 * Determina a melhor jogada da IA usando o algoritmo Minimax.
 * @returns {string} O nome do atributo que a IA deve jogar.
 */
const getBestMinimaxMove = () => {
    let bestMove = null;
    let maxEval = -Infinity;
    const aiSimulatedCard = aiDeck[0];

    // Se a IA tiver o Super Trunfo, não há necessidade de Minimax.
    if (aiSimulatedCard.supertrunfo) {
        return Object.keys(ATTRIBUTES)[0]; // Retorna qualquer atributo, a jogada é vitoriosa
    }

    // Itera sobre todos os atributos para encontrar a melhor jogada
    for (const attribute in ATTRIBUTES) {
        let currentEval;

        // Simula o resultado da jogada da IA
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
        currentEval = minimax(2, false, nextAiDeck, nextPlayerDeck); // Profundidade 2
        
        if (currentEval > maxEval) {
            maxEval = currentEval;
            bestMove = attribute;
        }
    }
    return bestMove;
};

/**
 * Manipula a jogada da IA.
 */
const handleAITurn = () => {
    let selectedAttribute = getBestMinimaxMove();

    gameStatusEl.textContent = `A IA escolheu: ${ATTRIBUTES[selectedAttribute]}!`;
    gameStatusEl.classList.remove('text-yellow-400');
    gameStatusEl.classList.add('text-red-500');

    // Destaca o atributo escolhido pela IA
    document.querySelectorAll('#playerAttributes .attribute-item').forEach(el => {
        el.classList.remove('selected', 'winner', 'loser');
        if (el.dataset.attribute === selectedAttribute) {
            el.classList.add('selected');
        }
    });

    compareCards(selectedAttribute);
    isPlayerTurn = true;
};


// Adiciona o evento de clique para o botão de iniciar jogo
startGameBtn.addEventListener('click', startGame);

// Renderiza o baralho completo quando a página é carregada
document.addEventListener('DOMContentLoaded', renderFullDeck);