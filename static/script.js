// Global state
let currentPlayers = 3;
const MAX_PLAYERS = 9;
const MIN_PLAYERS = 2;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    renderInputFields();
    loadExamples();
    
    document.getElementById('playerIncrease').addEventListener('click', increasePlayer);
    document.getElementById('playerDecrease').addEventListener('click', decreasePlayer);
    document.getElementById('playerCount').addEventListener('change', updatePlayerCount);
});

// Player count controls
function increasePlayer() {
    if (currentPlayers < MAX_PLAYERS) {
        currentPlayers++;
        updatePlayerUI();
    }
}

function decreasePlayer() {
    if (currentPlayers > MIN_PLAYERS) {
        currentPlayers--;
        updatePlayerUI();
    }
}

function updatePlayerCount() {
    const input = document.getElementById('playerCount');
    const count = parseInt(input.value);
    if (count >= MIN_PLAYERS && count <= MAX_PLAYERS) {
        currentPlayers = count;
        updatePlayerUI();
    } else {
        input.value = currentPlayers;
    }
}

function updatePlayerUI() {
    document.getElementById('playerCount').value = currentPlayers;
    renderInputFields();
    clearResults();
}

// Render input fields dynamically
function renderInputFields() {
    renderStacksInput();
    renderPayoutsInput();
}

function renderStacksInput() {
    const container = document.getElementById('stacksContainer');
    container.innerHTML = '';
    
    for (let i = 0; i < currentPlayers; i++) {
        const div = document.createElement('div');
        div.className = 'input-row';
        div.innerHTML = `
            <label>P${i + 1}</label>
            <input type="number" class="form-control stack-input" 
                   id="stack_${i}" value="100" min="0" step="0.01" placeholder="0">
        `;
        container.appendChild(div);
    }
}

function renderPayoutsInput() {
    const container = document.getElementById('payoutsContainer');
    container.innerHTML = '';
    
    for (let i = 0; i < currentPlayers; i++) {
        const div = document.createElement('div');
        div.className = 'input-row';
        const defaultValue = currentPlayers === 2 ? (i === 0 ? 100 : 50) :
                            currentPlayers === 3 ? [50, 30, 20][i] :
                            100 - (i * 20);
        div.innerHTML = `
            <label>#${i + 1}</label>
            <input type="number" class="form-control payout-input" 
                   id="payout_${i}" value="${defaultValue}" min="0" step="0.01" placeholder="0">
        `;
        container.appendChild(div);
    }
}

// Get values from input fields
function getStacks() {
    const stacks = [];
    for (let i = 0; i < currentPlayers; i++) {
        const value = parseFloat(document.getElementById(`stack_${i}`).value) || 0;
        stacks.push(value);
    }
    return stacks;
}

function getPayouts() {
    const payouts = [];
    for (let i = 0; i < currentPlayers; i++) {
        const value = parseFloat(document.getElementById(`payout_${i}`).value) || 0;
        payouts.push(value);
    }
    return payouts;
}

// Load and set example scenario
function loadExample() {
    const select = document.getElementById('examplesSelect');
    const index = select.value;
    if (index === '') return;
    
    fetch('/api/examples')
        .then(r => r.json())
        .then(examples => {
            const example = examples[index];
            currentPlayers = example.players;
            updatePlayerUI();
            
            setTimeout(() => {
                for (let i = 0; i < example.stacks.length; i++) {
                    document.getElementById(`stack_${i}`).value = example.stacks[i];
                }
                for (let i = 0; i < example.payouts.length; i++) {
                    document.getElementById(`payout_${i}`).value = example.payouts[i];
                }
                select.value = '';
            }, 50);
        });
}

// Load examples dropdown
function loadExamples() {
    fetch('/api/examples')
        .then(r => r.json())
        .then(examples => {
            const select = document.getElementById('examplesSelect');
            examples.forEach((ex, idx) => {
                const option = document.createElement('option');
                option.value = idx;
                option.textContent = ex.name;
                select.appendChild(option);
            });
        });
}

// Main calculation
async function calculateICM() {
    clearAlerts();
    
    const stacks = getStacks();
    const payouts = getPayouts();
    
    // Client-side validation
    if (!validateInputs(stacks, payouts)) {
        return;
    }
    
    const btn = document.getElementById('calculateBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Calculating...';
    
    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                players: currentPlayers,
                stacks: stacks,
                payouts: payouts
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            showAlert(data.error || 'Calculation failed', 'danger');
            return;
        }
        
        displayResults(data, stacks, payouts);
    } catch (error) {
        showAlert('Network error: ' + error.message, 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Calculate';
    }
}

// Validation
function validateInputs(stacks, payouts) {
    const errors = [];
    
    if (stacks.length !== currentPlayers) {
        errors.push('Please enter all player stacks');
    }
    
    if (payouts.length !== currentPlayers) {
        errors.push('Please enter all payouts');
    }
    
    if (stacks.some(s => s < 0)) {
        errors.push('Stacks cannot be negative');
    }
    
    if (payouts.some(p => p < 0)) {
        errors.push('Payouts cannot be negative');
    }
    
    if (stacks.reduce((a, b) => a + b, 0) === 0) {
        errors.push('Total chips must be greater than 0');
    }
    
    if (errors.length > 0) {
        errors.forEach(err => showAlert(err, 'danger'));
        return false;
    }
    
    return true;
}

// Display results
function displayResults(data, stacks, payouts) {
    displayICMResults(data.icm, stacks, payouts);
    displayBFResults(data.bf, data.icm, payouts);
}

function displayICMResults(icm, stacks, payouts) {
    const container = document.getElementById('icmResults');
    const total = icm.reduce((a, b) => a + b, 0);
    const totalChips = stacks.reduce((a, b) => a + b, 0);

    // Mobile-friendly card layout
    let html = '<div class="icm-cards">';
    for (let i = 0; i < icm.length; i++) {
        const equity = ((stacks[i] / totalChips) * 100).toFixed(1);
        html += `
            <div class="player-card">
                <div class="player-header">
                    <div>
                        <div><strong>P${i + 1}</strong></div>
                        <div class="meta">Stack: ${formatNumber(stacks[i])} • Equity: ${equity}%</div>
                    </div>
                    <div>
                        <div class="result-badge neutral">ICM</div>
                        <div style="margin-top:6px;text-align:right"><strong class="text-success">$${formatNumber(icm[i])}</strong></div>
                    </div>
                </div>
            </div>
        `;
    }
    html += '</div>';
    html += `<div class="mt-2"><strong>Total ICM:</strong> $${formatNumber(total)} (Pot: $${formatNumber(payouts.reduce((a, b) => a + b, 0))})</div>`;

    container.innerHTML = html;
}

function displayBFResults(bf, icm, payouts) {
    const container = document.getElementById('bfResults');

    // bf is expected to be an array of player objects: { player, vs_opponents: [{opponent, bf, ev_gain, ev_loss, reason}], average_bf }
    let html = '';

    for (let i = 0; i < bf.length; i++) {
        const playerObj = bf[i];
        const playerName = playerObj.player || `P${i+1}`;
        const avg = (playerObj.average_bf !== undefined) ? (isFinite(playerObj.average_bf) ? Number(playerObj.average_bf).toFixed(2) + 'x' : '∞x') : '';

        html += `<div class="player-card" data-player="${playerName}">`;
        html += `<div class="player-header"><div><strong>${playerName}</strong><div class="meta">Avg BF: <span class="bf-label">${avg}</span></div></div>`;
        html += `<div><button class="bf-toggle" aria-expanded="false" onclick="toggleBF(this)">Vs opponents <span class="small">▾</span></button></div></div>`;
        html += `<div class="bf-accordion"><div class="bf-content">`;

        if (Array.isArray(playerObj.vs_opponents) && playerObj.vs_opponents.length > 0) {
            playerObj.vs_opponents.forEach(op => {
                let bfVal = op.bf;
                let display = isFinite(bfVal) ? Number(bfVal).toFixed(2) + 'x' : '∞x';
                const label = getInterpretationLabel(bfVal);
                const colorClass = label === 'Standard' ? 'positive' : label === 'Be cautious' ? 'neutral' : 'negative';

                html += `<div class="bf-row"><div><strong>${op.opponent}</strong><div class="meta">EV gain: ${formatNumber(op.ev_gain || 0)} • EV loss: ${formatNumber(op.ev_loss || 0)}</div></div>`;
                html += `<div style="display:flex;align-items:center;gap:0.5rem"><div class="bf-badge ${colorClass}">${display}</div><div class="bf-label">${label}</div></div></div>`;
            });
        } else {
            html += `<div class="small text-muted">No opponent data</div>`;
        }

        html += `</div></div></div>`;
    }

    container.innerHTML = html;
}

// Toggle accordion content (simple, no dependency)
function toggleBF(btn) {
    const card = btn.closest('.player-card');
    const content = card.querySelector('.bf-content');
    const expanded = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', expanded ? 'false' : 'true');
    if (expanded) {
        content.style.display = 'none';
    } else {
        content.style.display = 'block';
    }
}

function getInterpretationLabel(bfVal) {
    if (!isFinite(bfVal)) return 'Very cautious';
    const v = Number(bfVal);
    if (v <= 1.3) return 'Standard';
    if (v <= 1.8) return 'Be cautious';
    return 'Very cautious';
}

// Utility functions
function formatNumber(num) {
    return parseFloat(num).toFixed(2);
}

function clearResults() {
    document.getElementById('icmResults').innerHTML = '<p class="text-muted text-center py-4">Enter values and click Calculate</p>';
    document.getElementById('bfResults').innerHTML = '<p class="text-muted text-center py-4">Enter values and click Calculate</p>';
    document.getElementById('icmTotal').innerHTML = '';
}

function clearAlerts() {
    document.getElementById('alertContainer').innerHTML = '';
}

function showAlert(message, type = 'info') {
    const container = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    container.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 5000);
}
