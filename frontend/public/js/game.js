/**
 * Lógica do jogo Super Trunfo - Frontend Retro.
 */

// Estado do jogo
let gameState = {
    gameId: null,
    playerDeck: [],
    selectedCard: null,
    selectedAttribute: null,
    difficulty: null,
    isPlaying: false,
    fullDeck: []
};

// Mapeamento de IDs de carros para imagens
const IMAGE_MAP = {
    1: 'rx-7.jpg',
    2: 'civic-type-r.jpg',
    3: 'gt-r-34.jpeg',
    4: 'supra.jpeg',
    5: 'mustang.jpeg',
    6: '911-carrera-gts.jpg',
    7: 'm3.jpeg',
    8: 'aventador.jpeg',
    9: 'tesla-model-s-plaid.jpg',
    10: 'impreza-wrx-sti.jpeg',
    11: 'camaro-ss.jpeg',
    12: 'a45-amg.jpeg',
    13: 'challenger-hellcat.jpeg',
    14: 'huracan-evo.jpg',
    15: 'rs7-sportback.jpg',
    16: 'corvette-c8.jpg',
    17: 'golf-r.jpeg',
    18: 'viper-acr.jpeg',
    19: 'ferrari-488.jpg',
    20: 'Koenigsegg-Agera-R.jpeg',
    21: 'Pagani-Huayra.jpeg',
    22: 'm5-competition.jpeg',
    23: 'Aston-Martin-Vantage.jpg',
    24: 'Chiron-Super-Sport.jpg',
    25: 'fiat-uno.jpg'
};

/**
 * Retorna o caminho da imagem para um carro específico
 */
function getCarImage(cardId) {
    const imageName = IMAGE_MAP[cardId];
    return imageName ? `images/${imageName}` : `https://placehold.co/200x120/000000/FF0000?text=No+Image`;
}

// Mapeamento de atributos para exibição
const ATTRIBUTE_NAMES = {
    'HP': 'POTÊNCIA',
    'torque': 'TORQUE',
    'weight': 'PESO',
    '0-100': '0-100',
    'top_speed': 'VEL. MÁX'
};

// Elementos do DOM
const elements = {
    gameStatus: document.getElementById('gameStatus'),
    startGameBtn: document.getElementById('startGameBtn'),
    fullDeckContainer: document.getElementById('fullDeckContainer'),
    fullDeckGrid: document.getElementById('fullDeckGrid'),
    difficultyMenu: document.getElementById('difficultyMenu'),
    gameContainer: document.getElementById('gameContainer'),
    playerDeckContainer: document.getElementById('playerDeckContainer'),
    playerCard: document.getElementById('playerCard'),
    aiCard: document.getElementById('aiCard'),
    playerCardName: document.getElementById('playerCardName'),
    playerCardImage: document.getElementById('playerCardImage'),
    playerAttributes: document.getElementById('playerAttributes'),
    aiCardName: document.getElementById('aiCardName'),
    aiCardImage: document.getElementById('aiCardImage'),
    playerScore: document.getElementById('playerScore'),
    aiScore: document.getElementById('aiScore'),
    playerDeckCount: document.getElementById('playerDeckCount'),
    aiDeckCount: document.getElementById('aiDeckCount'),
    resultMessage: document.getElementById('resultMessage'),
    confirmCardBtn: document.getElementById('confirmCardBtn')
};

/**
 * Inicializa a aplicação.
 */
async function init() {
    try {
        // Verifica se a API está disponível
        const health = await api.health();
        console.log('API Status:', health);
        
        // Carrega baralho completo
        const deckResponse = await api.getDeck();
        gameState.fullDeck = deckResponse.cards || deckResponse;
        
        renderFullDeck();
        
        elements.gameStatus.textContent = 'Analise o baralho e clique em "Começar Jogo" para iniciar!';
        
        // Event listeners
        elements.startGameBtn.addEventListener('click', showDifficultyMenu);
        
        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const difficulty = e.target.dataset.difficulty;
                startGame(difficulty);
            });
        });
        
        elements.confirmCardBtn.addEventListener('click', playRound);
        
    } catch (error) {
        console.error('Erro ao inicializar:', error);
        elements.gameStatus.textContent = 'Erro ao conectar com o servidor';
        elements.gameStatus.classList.add('text-red-500');
    }
}

/**
 * Renderiza o baralho completo.
 */
function renderFullDeck() {
    elements.fullDeckGrid.innerHTML = '';
    
    gameState.fullDeck.forEach(card => {
        const cardEl = document.createElement('div');
        cardEl.className = 'deck-view-card';
        
        cardEl.innerHTML = `
            <h3 class="text-xs font-bold text-red-400 mb-2 text-center">${card.name}</h3>
            <p class="text-xs text-gray-400 text-center mb-2">${card.brand} (${card.year})</p>
            <div class="text-xs text-green-400 space-y-1">
                <div>HP: ${Math.round(card.HP)}</div>
                <div>Torque: ${Math.round(card.torque)} Nm</div>
                <div>Peso: ${Math.round(card.weight)} kg</div>
                <div>0-100: ${card['0-100'].toFixed(1)}s</div>
                <div>Vel. Máx: ${Math.round(card.top_speed)} km/h</div>
            </div>
        `;
        
        elements.fullDeckGrid.appendChild(cardEl);
    });
}

/**
 * Mostra menu de dificuldade.
 */
function showDifficultyMenu() {
    elements.fullDeckContainer.classList.add('hidden');
    elements.startGameBtn.classList.add('hidden');
    elements.difficultyMenu.classList.remove('hidden');
    elements.gameStatus.textContent = 'Escolha o nível de dificuldade';
}

/**
 * Inicia um novo jogo.
 */
async function startGame(difficulty) {
    try {
        elements.gameStatus.textContent = 'Iniciando jogo...';
        
        // Chama API para iniciar jogo
        const response = await api.startGame(difficulty);
        
        gameState.gameId = response.game_id;
        gameState.playerDeck = response.player_deck;
        gameState.difficulty = difficulty;
        gameState.isPlaying = true;
        
        // Atualiza UI
        elements.difficultyMenu.classList.add('hidden');
        elements.gameContainer.classList.remove('hidden');
        
        updateGameUI(response);
        renderPlayerDeck();
        
        elements.gameStatus.textContent = `Jogo iniciado! Dificuldade: ${difficulty.toUpperCase()}`;
        elements.gameStatus.classList.add('text-green-400');
        
    } catch (error) {
        console.error('Erro ao iniciar jogo:', error);
        elements.gameStatus.textContent = `Erro: ${error.message}`;
        elements.gameStatus.classList.add('text-red-500');
    }
}

/**
 * Renderiza o deck do jogador.
 */
function renderPlayerDeck() {
    elements.playerDeckContainer.innerHTML = '';
    
    gameState.playerDeck.forEach(card => {
        const cardEl = document.createElement('div');
        cardEl.className = `player-deck-card ${gameState.selectedCard?.id === card.id ? 'selected-deck-card' : ''}`;
        
        cardEl.innerHTML = `
            <p class="card-name-short text-green-400 mb-1">${card.name}</p>
            <p class="text-gray-400" style="font-size: 6px;">${card.brand}</p>
        `;
        
        cardEl.addEventListener('click', () => selectCard(card));
        
        elements.playerDeckContainer.appendChild(cardEl);
    });
}

/**
 * Seleciona uma carta.
 */
function selectCard(card) {
    gameState.selectedCard = card;
    gameState.selectedAttribute = null;
    
    renderPlayerDeck();
    displayPlayerCard(card);
    
    // Mostra botão de confirmação
    elements.confirmCardBtn.classList.remove('hidden');
    elements.confirmCardBtn.disabled = true;
    
    // Remove flip da carta do jogador
    elements.playerCard.classList.remove('flipped');
    
    elements.gameStatus.textContent = 'Carta selecionada! Escolha um atributo.';
}

/**
 * Exibe a carta do jogador.
 */
function displayPlayerCard(card) {
    elements.playerCardName.textContent = card.name;
    elements.playerCardImage.src = getCarImage(card.id);
    
    elements.playerAttributes.innerHTML = `
        <li class="attribute-item" data-attribute="HP">
            ${ATTRIBUTE_NAMES['HP']}: <span class="font-semibold">${Math.round(card.HP)}</span>
        </li>
        <li class="attribute-item" data-attribute="torque">
            ${ATTRIBUTE_NAMES['torque']}: <span class="font-semibold">${Math.round(card.torque)} Nm</span>
        </li>
        <li class="attribute-item" data-attribute="weight">
            ${ATTRIBUTE_NAMES['weight']}: <span class="font-semibold">${Math.round(card.weight)} kg</span>
        </li>
        <li class="attribute-item" data-attribute="0-100">
            ${ATTRIBUTE_NAMES['0-100']}: <span class="font-semibold">${card['0-100'].toFixed(1)}s</span>
        </li>
        <li class="attribute-item" data-attribute="top_speed">
            ${ATTRIBUTE_NAMES['top_speed']}: <span class="font-semibold">${Math.round(card.top_speed)} km/h</span>
        </li>
    `;
    
    // Event listeners para atributos
    document.querySelectorAll('.attribute-item').forEach(el => {
        el.addEventListener('click', () => {
            const attr = el.dataset.attribute;
            selectAttribute(attr);
        });
    });
}

/**
 * Seleciona um atributo.
 */
function selectAttribute(attribute) {
    gameState.selectedAttribute = attribute;
    
    // Atualiza UI
    document.querySelectorAll('.attribute-item').forEach(el => {
        if (el.dataset.attribute === attribute) {
            el.classList.add('selected');
        } else {
            el.classList.remove('selected');
        }
    });
    
    elements.gameStatus.textContent = `Atributo selecionado: ${ATTRIBUTE_NAMES[attribute]}`;
    elements.confirmCardBtn.disabled = false;
}

/**
 * Joga uma rodada.
 */
async function playRound() {
    if (!gameState.selectedCard || !gameState.selectedAttribute) {
        alert('Selecione uma carta e um atributo!');
        return;
    }
    
    try {
        elements.confirmCardBtn.disabled = true;
        elements.gameStatus.textContent = 'Jogando rodada...';
        
        // Chama API
        const response = await api.playRound(
            gameState.gameId,
            gameState.selectedCard.id,
            gameState.selectedAttribute
        );
        
        // Exibe resultado
        displayRoundResult(response);
        
        // Atualiza estado
        updateGameUI(response);
        
        // Verifica fim de jogo
        if (response.game_over) {
            endGame(response.game_winner);
        } else {
            // Aguarda 3 segundos antes de preparar próxima rodada
            setTimeout(async () => {
                // Atualiza deck do jogador
                const status = await api.getGameStatus(gameState.gameId);
                gameState.playerDeck = status.current_player_deck;
                
                // Reseta seleção
                gameState.selectedCard = null;
                gameState.selectedAttribute = null;
                
                renderPlayerDeck();
                
                // Reseta cartas
                elements.playerCard.classList.add('flipped');
                elements.aiCard.classList.add('flipped');
                elements.confirmCardBtn.classList.add('hidden');
                elements.resultMessage.textContent = '';
                
                elements.gameStatus.textContent = 'Selecione sua próxima carta';
            }, 3000);
        }
        
    } catch (error) {
        console.error('Erro ao jogar rodada:', error);
        elements.gameStatus.textContent = `Erro: ${error.message}`;
        elements.gameStatus.classList.add('text-red-500');
        elements.confirmCardBtn.disabled = false;
    }
}

/**
 * Exibe resultado da rodada.
 */
function displayRoundResult(response) {
    const result = response.round_result;
    
    // Vira a carta da IA
    elements.aiCard.classList.remove('flipped');
    
    // Exibe carta da IA
    elements.aiCardName.textContent = result.ai_card.name;
    elements.aiCardImage.src = getCarImage(result.ai_card.id);
    
    // Atualiza atributos da IA
    document.getElementById('aiHP').innerHTML = `POTÊNCIA: <span class="font-semibold">${Math.round(result.ai_card.HP)}</span>`;
    document.getElementById('aiTorque').innerHTML = `TORQUE: <span class="font-semibold">${Math.round(result.ai_card.torque)} Nm</span>`;
    document.getElementById('aiWeight').innerHTML = `PESO: <span class="font-semibold">${Math.round(result.ai_card.weight)} kg</span>`;
    document.getElementById('ai0100').innerHTML = `0-100: <span class="font-semibold">${result.ai_card['0-100'].toFixed(1)}s</span>`;
    document.getElementById('aiTopSpeed').innerHTML = `VEL. MÁX: <span class="font-semibold">${Math.round(result.ai_card.top_speed)} km/h</span>`;
    
    // Destaca atributos comparados
    document.querySelectorAll('.attribute-item').forEach(el => {
        if (el.dataset.attribute === result.attribute) {
            if (result.winner === 'player') {
                el.classList.add('winner');
                el.classList.remove('loser');
            } else if (result.winner === 'ai') {
                el.classList.add('loser');
                el.classList.remove('winner');
            }
        }
    });
    
    // Mensagem de resultado
    let messageClass = '';
    if (result.winner === 'player') {
        messageClass = 'text-green-500';
    } else if (result.winner === 'ai') {
        messageClass = 'text-red-500';
    } else {
        messageClass = 'text-yellow-400';
    }
    
    elements.resultMessage.textContent = result.message;
    elements.resultMessage.className = `text-center text-lg md:text-xl font-bold mb-4 ${messageClass}`;
}

/**
 * Atualiza UI com dados do jogo.
 */
function updateGameUI(data) {
    if (data.player_score !== undefined) {
        elements.playerScore.textContent = data.player_score;
        elements.aiScore.textContent = data.ai_score;
    }
    
    if (data.player_deck_count !== undefined) {
        elements.playerDeckCount.textContent = data.player_deck_count;
        elements.aiDeckCount.textContent = data.ai_deck_count;
    } else if (data.player_deck) {
        elements.playerDeckCount.textContent = data.player_deck.length;
    }
    
    if (data.ai_deck_count !== undefined) {
        elements.aiDeckCount.textContent = data.ai_deck_count;
    }
}

/**
 * Finaliza o jogo.
 */
function endGame(winner) {
    gameState.isPlaying = false;
    
    let message = '';
    let messageClass = '';
    
    if (winner === 'player') {
        message = '🎉 VOCÊ VENCEU! 🎉';
        messageClass = 'text-green-500';
    } else if (winner === 'ai') {
        message = '😢 A IA VENCEU! 😢';
        messageClass = 'text-red-500';
    } else {
        message = '🤝 EMPATE! 🤝';
        messageClass = 'text-yellow-400';
    }
    
    elements.gameStatus.textContent = message;
    elements.gameStatus.className = `text-2xl font-bold ${messageClass}`;
    
    elements.confirmCardBtn.textContent = 'Jogar Novamente';
    elements.confirmCardBtn.classList.remove('hidden');
    elements.confirmCardBtn.disabled = false;
    elements.confirmCardBtn.onclick = () => location.reload();
}

// Inicializa quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', init);
