/**
 * Lógica do jogo Super Trunfo - Frontend.
 */

// Estado do jogo
let gameState = {
    gameId: null,
    playerDeck: [],
    selectedCard: null,
    selectedAttribute: null,
    difficulty: null,
    isPlaying: false
};

// Mapeamento de atributos para exibição
const ATTRIBUTE_NAMES = {
    'HP': 'Potência (HP)',
    'torque': 'Torque (Nm)',
    'weight': 'Peso (kg)',
    '0-100': '0-100 km/h (s)',
    'top_speed': 'Velocidade Máxima (km/h)'
};

// Elementos do DOM
const elements = {
    gameStatus: document.getElementById('gameStatus'),
    startSection: document.getElementById('startSection'),
    startGameBtn: document.getElementById('startGameBtn'),
    difficultyMenu: document.getElementById('difficultyMenu'),
    gameContainer: document.getElementById('gameContainer'),
    playerDeckContainer: document.getElementById('playerDeckContainer'),
    playerCardDisplay: document.getElementById('playerCardDisplay'),
    aiCardDisplay: document.getElementById('aiCardDisplay'),
    playerScore: document.getElementById('playerScore'),
    aiScore: document.getElementById('aiScore'),
    playerDeckCount: document.getElementById('playerDeckCount'),
    aiDeckCount: document.getElementById('aiDeckCount'),
    resultMessage: document.getElementById('resultMessage'),
    playButton: document.getElementById('playButton')
};

/**
 * Inicializa a aplicação.
 */
async function init() {
    try {
        // Verifica se a API está disponível
        const health = await api.health();
        console.log('API Status:', health);
        
        elements.gameStatus.textContent = 'Pronto para jogar!';
        
        // Event listeners
        elements.startGameBtn.addEventListener('click', showDifficultyMenu);
        
        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const difficulty = e.target.dataset.difficulty;
                startGame(difficulty);
            });
        });
        
        elements.playButton.addEventListener('click', playRound);
        
    } catch (error) {
        console.error('Erro ao inicializar:', error);
        elements.gameStatus.textContent = 'Erro ao conectar com o servidor';
        elements.gameStatus.classList.add('text-red-500');
    }
}

/**
 * Mostra menu de dificuldade.
 */
function showDifficultyMenu() {
    elements.startSection.classList.add('hidden');
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
        cardEl.className = `
            bg-gray-700 p-2 rounded cursor-pointer hover:bg-gray-600 
            transition-all border-2 border-transparent
            ${gameState.selectedCard?.id === card.id ? 'border-green-400 bg-gray-600' : ''}
        `;
        cardEl.style.minWidth = '120px';
        
        cardEl.innerHTML = `
            <p class="text-xs font-bold text-center mb-1">${card.name}</p>
            <p class="text-xs text-gray-400 text-center">${card.brand}</p>
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
    
    elements.gameStatus.textContent = 'Carta selecionada! Escolha um atributo.';
    elements.playButton.disabled = true;
}

/**
 * Exibe a carta do jogador.
 */
function displayPlayerCard(card) {
    elements.playerCardDisplay.innerHTML = `
        <h4 class="text-xl font-bold mb-2">${card.name}</h4>
        <p class="text-sm text-gray-400 mb-4">${card.brand} (${card.year})</p>
        <div class="space-y-2">
            ${Object.keys(ATTRIBUTE_NAMES).map(attr => `
                <div class="attribute-option bg-gray-700 p-3 rounded cursor-pointer hover:bg-gray-600 transition-all ${gameState.selectedAttribute === attr ? 'bg-blue-600' : ''}"
                     data-attribute="${attr}">
                    <div class="flex justify-between">
                        <span class="text-sm">${ATTRIBUTE_NAMES[attr]}</span>
                        <span class="font-bold">${formatAttributeValue(card[attr], attr)}</span>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    
    // Event listeners para atributos
    document.querySelectorAll('.attribute-option').forEach(el => {
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
    document.querySelectorAll('.attribute-option').forEach(el => {
        if (el.dataset.attribute === attribute) {
            el.classList.add('bg-blue-600');
            el.classList.remove('bg-gray-700');
        } else {
            el.classList.remove('bg-blue-600');
            el.classList.add('bg-gray-700');
        }
    });
    
    elements.gameStatus.textContent = `Atributo selecionado: ${ATTRIBUTE_NAMES[attribute]}`;
    elements.playButton.disabled = false;
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
        elements.playButton.disabled = true;
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
            // Atualiza deck do jogador
            const status = await api.getGameStatus(gameState.gameId);
            gameState.playerDeck = status.current_player_deck;
            
            // Reseta seleção
            gameState.selectedCard = null;
            gameState.selectedAttribute = null;
            
            renderPlayerDeck();
            elements.playerCardDisplay.innerHTML = '<p class="text-gray-500">Selecione uma carta</p>';
            elements.aiCardDisplay.innerHTML = '<p class="text-gray-500">Aguardando...</p>';
            
            elements.gameStatus.textContent = 'Selecione sua próxima carta';
        }
        
    } catch (error) {
        console.error('Erro ao jogar rodada:', error);
        elements.gameStatus.textContent = `Erro: ${error.message}`;
        elements.gameStatus.classList.add('text-red-500');
        elements.playButton.disabled = false;
    }
}

/**
 * Exibe resultado da rodada.
 */
function displayRoundResult(response) {
    const result = response.round_result;
    
    // Exibe carta da IA
    elements.aiCardDisplay.innerHTML = `
        <h4 class="text-xl font-bold mb-2">${result.ai_card.name}</h4>
        <p class="text-sm text-gray-400 mb-4">${result.ai_card.brand} (${result.ai_card.year})</p>
        <div class="space-y-2">
            ${Object.keys(ATTRIBUTE_NAMES).map(attr => `
                <div class="bg-gray-700 p-3 rounded ${attr === result.attribute ? 'border-2 border-yellow-400' : ''}">
                    <div class="flex justify-between">
                        <span class="text-sm">${ATTRIBUTE_NAMES[attr]}</span>
                        <span class="font-bold">${formatAttributeValue(result.ai_card[attr], attr)}</span>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    
    // Mensagem de resultado
    let messageClass = '';
    if (result.winner === 'player') {
        messageClass = 'text-green-400';
    } else if (result.winner === 'ai') {
        messageClass = 'text-red-400';
    } else {
        messageClass = 'text-yellow-400';
    }
    
    elements.resultMessage.textContent = result.message;
    elements.resultMessage.className = `text-center text-xl font-bold mb-4 h-8 ${messageClass}`;
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
        messageClass = 'text-green-400';
    } else if (winner === 'ai') {
        message = '😢 A IA VENCEU! 😢';
        messageClass = 'text-red-400';
    } else {
        message = '🤝 EMPATE! 🤝';
        messageClass = 'text-yellow-400';
    }
    
    elements.gameStatus.textContent = message;
    elements.gameStatus.className = `text-2xl font-bold ${messageClass}`;
    
    elements.playButton.textContent = 'Jogar Novamente';
    elements.playButton.disabled = false;
    elements.playButton.onclick = () => location.reload();
}

/**
 * Formata valor de atributo para exibição.
 */
function formatAttributeValue(value, attribute) {
    if (attribute === '0-100') {
        return `${value.toFixed(1)}s`;
    } else if (attribute === 'top_speed') {
        return `${Math.round(value)} km/h`;
    } else if (attribute === 'weight') {
        return `${Math.round(value)} kg`;
    } else {
        return Math.round(value);
    }
}

// Inicializa quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', init);
