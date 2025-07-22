// Estado da Aplicação
let currentUser = null;
let chartInstances = {};
let allNestsReportData = []; // Armazena todos os dados dos ninhos para filtragem

// Seletores do DOM
const sel = (selector) => document.querySelector(selector);
const authSection = sel('#auth-section'), dashboard = sel('#dashboard'), userNameSpan = sel('#user-name'), adminTab = sel('#admin-tab');

// --- INICIALIZAÇÃO ---
document.addEventListener('DOMContentLoaded', () => {
    Chart.register(ChartDataLabels);
    checkAuthStatus();
    setupEventListeners();
});
// --- FUNÇÃO AUXILIAR PARA O INDICADOR DE RISCO (NOVA) ---
function getRiskIndicatorHTML(risk) {
    let riskClass = '';
    switch (risk) {
        case 'crítico':
            riskClass = 'risk-critical';
            break;
        case 'sob observação':
            riskClass = 'risk-observation';
            break;
        case 'estável':
            riskClass = 'risk-stable';
            break;
    }
    // Retorna o span HTML com a classe de cor correta
    return `<span class="risk-indicator ${riskClass}"></span>`;
}

// --- SETUP ---
function setupEventListeners() {
    sel('#login-form').addEventListener('submit', handleAuth);
    sel('#register-form').addEventListener('submit', handleAuth);
    sel('#logout-btn').addEventListener('click', handleLogout);
    
    // Listener para o link "Esqueci minha senha"
    sel('#auth-section').addEventListener('click', (e) => {
        if (e.target.matches('#forgot-password-link')) {
            handleForgotPassword(e);
        }
    });
    
    // Delegação de eventos para elementos dinâmicos no dashboard
    dashboard.addEventListener('click', (e) => {
        if (e.target.matches('.tab')) switchTab(e.target.dataset.tab);
        if (e.target.matches('.ranking-btn')) loadRanking(e.target.dataset.periodo);
        if (e.target.matches('#show-ranking-info-btn')) {
            const infoBox = sel('#ranking-info-box');
            infoBox.style.display = infoBox.style.display === 'none' ? 'block' : 'none';
        }
        if (e.target.matches('#export-ninhos-btn')) {
            window.location.href = '/api/relatorios/ninhos/export';
        }
    });

    // Adiciona listeners para os filtros de relatório
    sel('#dashboard').addEventListener('input', (e) => {
        if (e.target.matches('#filter-regiao')) applyReportFilters();
    });
    sel('#dashboard').addEventListener('change', (e) => {
        if (e.target.matches('#filter-status') || e.target.matches('#filter-risco')) applyReportFilters();
    });
}

// --- CONTROLE DE UI ---
function switchTab(tabName) {
    dashboard.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tabName));
    dashboard.querySelectorAll('.tab-content').forEach(c => {
        c.classList.remove('active');
        c.style.display = 'none';
    });
    
    const activeTabContent = sel(`#tab-${tabName}`);
    if (activeTabContent) {
        activeTabContent.classList.add('active');
        activeTabContent.style.display = 'block';
        loadTabContent(tabName);
    }
}

function loadTabContent(tabName) {
    const loaders = {
        'estatisticas': loadStatisticsAndCharts,
        'cadastrar': renderNinhoForm,
        'listar': loadNinhos,
        'ranking': () => loadRanking('geral'),
        'admin': loadAdminPanel,
        'relatorios': loadReportDataAndRenderTable
    };
    if (loaders[tabName]) loaders[tabName]();
}

function showUI(isLoggedIn) {
    authSection.style.display = isLoggedIn ? 'none' : 'flex';
    dashboard.style.display = isLoggedIn ? 'block' : 'none';
    if (isLoggedIn) {
        userNameSpan.textContent = currentUser.nome_completo;
        const isAdmin = currentUser.is_admin;
        
        // Lógica de visibilidade das abas
        adminTab.style.display = isAdmin ? 'block' : 'none';
        
        // CORREÇÃO: Mostra a aba de relatórios para TODOS os usuários logados
        sel('#reports-tab').style.display = 'block'; 
        
        switchTab('estatisticas');
    }
}

function showAlert(message, type) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    sel('.content').prepend(alert);
    setTimeout(() => alert.remove(), 4000);
}

// --- API E AUTENTICAÇÃO ---
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`/api${endpoint}`, options);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Erro de comunicação');
        return data;
    } catch (error) {
        throw new Error(error.message || 'Erro de rede ou servidor indisponível');
    }
}

async function checkAuthStatus() {
    try {
        const data = await apiCall('/auth/me');
        currentUser = data.user;
        showUI(true);
    } catch (error) {
        showUI(false);
    }
}

async function handleAuth(e) {
    e.preventDefault();
    const endpoint = e.target.id === 'login-form' ? '/auth/login' : '/auth/register';
    const body = JSON.stringify(Object.fromEntries(new FormData(e.target)));
    try {
        const data = await apiCall(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body });
        showAlert(data.message, 'success');
        e.target.reset();
        if (endpoint === '/auth/login') {
            currentUser = data.user;
            showUI(true);
        }
    } catch (error) {
        showAlert(error.message, 'error');
    }
}

async function handleLogout() {
    try {
        await apiCall('/auth/logout', { method: 'POST' });
        currentUser = null;
        window.location.reload();
    } catch (error) {
        showAlert(error.message, 'error');
    }
}

async function handleForgotPassword(e) {
    e.preventDefault();
    const email = prompt("Digite seu e-mail de cadastro para enviarmos o link de recuperação:");
    if (!email) return;

    try {
        const data = await apiCall('/auth/forgot-password', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ email })
        });
        showAlert(data.message, 'success');
    } catch (error) {
        showAlert(error.message, 'error');
    }
}

// --- NINHOS ---
function renderNinhoForm() {
    const formContainer = sel('#tab-cadastrar');
    if (formContainer.querySelector('#ninho-form')) return;

    formContainer.innerHTML = `
        <div class="list-container">
            <h3>Cadastrar Novo Ninho</h3>
            <form id="ninho-form">
                <div class="form-row"><div class="form-group"><label for="ninho-regiao">Região:</label><input type="text" id="ninho-regiao" name="regiao" required></div><div class="form-group"><label for="ninho-ovos">Qtd. Ovos:</label><input type="number" id="ninho-ovos" name="quantidade_ovos" min="1" required></div></div>
                <div class="form-row"><div class="form-group"><label for="ninho-status">Status:</label><select id="ninho-status" name="status" required><option value="intacto">Intacto</option><option value="ameaçado">Ameaçado</option><option value="danificado">Danificado</option></select></div><div class="form-group"><label for="ninho-risco">Risco:</label><select id="ninho-risco" name="risco" required><option value="estável">Estável</option><option value="sob observação">Sob Observação</option><option value="crítico">Crítico</option></select></div></div>
                <div class="form-row"><div class="form-group"><label for="ninho-dias">Dias para Eclosão:</label><input type="number" id="ninho-dias" name="dias_para_eclosao" min="0" required></div><div class="form-group"><label for="ninho-predadores">Predadores:</label><select id="ninho-predadores" name="predadores"><option value="false">Não</option><option value="true">Sim</option></select></div></div>
                <div class="form-row"><div class="form-group"><label for="ninho-latitude">Latitude:</label><input type="number" id="ninho-latitude" name="latitude" step="any"></div><div class="form-group"><label for="ninho-longitude">Longitude:</label><input type="number" id="ninho-longitude" name="longitude" step="any"></div></div>
                <div class="form-group"><label for="ninho-foto">Foto:</label><input type="file" id="ninho-foto" name="foto" accept="image/*"></div>
                <button type="button" id="get-location-btn" class="btn" style="width: 100%; margin-bottom: 15px; background-color: #17a2b8;">📍 Obter Localização Atual</button>
                <button type="submit" class="btn" style="width: 100%;">Cadastrar Ninho</button>
            </form>
        </div>`;
    sel('#ninho-form').addEventListener('submit', handleCreateNinho);
    sel('#get-location-btn').addEventListener('click', getCurrentLocation);
}

async function handleCreateNinho(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const ninhoData = Object.fromEntries(formData.entries());
    
    try {
        const foto = formData.get('foto');
        if (foto && foto.size > 0) {
            const uploadFormData = new FormData();
            uploadFormData.append('file', foto);
            const uploadData = await apiCall('/upload', { method: 'POST', body: uploadFormData });
            ninhoData.foto_path = uploadData.file_path;
        }
        delete ninhoData.foto;

        const result = await apiCall('/ninhos', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(ninhoData) });
        showAlert(result.message, 'success');
        form.reset();
        loadStatisticsAndCharts();
    } catch (error) {
        showAlert(error.message, 'error');
    }
}

async function loadNinhos() {
    const listEl = sel('#ninhos-list');
    listEl.innerHTML = '<p>Carregando seus ninhos...</p>';
    try {
        const data = await apiCall('/ninhos');
        if (data.ninhos.length === 0) {
            listEl.innerHTML = '<p>Você ainda não cadastrou nenhum ninho.</p>';
            return;
        }
        listEl.innerHTML = data.ninhos.map(n => {
            // CORREÇÃO: Capitaliza a primeira letra para melhor visualização
            const statusCapitalized = n.status.charAt(0).toUpperCase() + n.status.slice(1);
            const riscoCapitalized = n.risco.charAt(0).toUpperCase() + n.risco.slice(1);
            
            return `
            <div class="ranking-item">
                <div class="info" style="flex-grow:3;">
                    <div class="nome">${n.regiao} (${n.quantidade_ovos} ovos)</div>
                    <div class="username" style="font-size: 0.8em; color: #666;">
                        Status: ${statusCapitalized} | 
                        Risco: ${getRiskIndicatorHTML(n.risco)} ${riscoCapitalized} | 
                        Registrado em: ${new Date(n.data_registro).toLocaleDateString('pt-BR')}
                    </div>
                </div>
                ${n.foto_path ? `<img src="/uploads/${n.foto_path.split('/')[1]}" style="width:60px;height:60px;border-radius:8px;">` : ''}
            </div>
        `}).join('');
    } catch (error) {
        listEl.innerHTML = `<p style="color:red;">${error.message}</p>`;
    }
}


function getCurrentLocation() {
    if (!navigator.geolocation) return showAlert('Geolocalização não é suportada neste navegador.', 'error');
    const btn = sel('#get-location-btn');
    btn.disabled = true;
    btn.textContent = 'Obtendo...';
    navigator.geolocation.getCurrentPosition(
        (position) => {
            sel('#ninho-latitude').value = position.coords.latitude.toFixed(6);
            sel('#ninho-longitude').value = position.coords.longitude.toFixed(6);
            btn.textContent = 'Localização Obtida!';
            btn.style.backgroundColor = '#28a745';
            btn.disabled = false;
            setTimeout(() => { btn.textContent = '📍 Obter Localização Atual'; btn.style.backgroundColor = '#17a2b8'; }, 2500);
        },
        (err) => {
            const message = err.code === 1 ? 'Permissão negada.' : err.code === 2 ? 'Sinal indisponível.' : 'Tempo esgotado.';
            showAlert(`Erro ao obter localização: ${message}`, 'error');
            btn.disabled = false;
            btn.textContent = '📍 Obter Localização Atual';
        },
        { timeout: 10000 }
    );
}

// --- ESTATÍSTICAS E GRÁFICOS ---
async function loadStatisticsAndCharts() {
    const gridEl = sel('#stats-grid');
    if (!gridEl) return;
    gridEl.innerHTML = '';
    try {
        const [stats, rankingStats] = await Promise.all([apiCall('/estatisticas'), apiCall('/ranking/estatisticas')]);
        gridEl.innerHTML = `<div class="stat-card"><h4>${stats.total_ninhos||0}</h4><p>Ninhos Totais</p></div><div class="stat-card"><h4>${stats.ninhos_prestes_eclodir||0}</h4><p>Perto da Eclosão</p></div><div class="stat-card"><h4>${stats.ninhos_por_risco.crítico||0}</h4><p>Ninhos Críticos</p></div><div class="stat-card"><h4>${stats.media_ovos_critico||0}</h4><p>Média Ovos/Crítico</p></div>`;
        renderChart('statusChart', { type: 'pie', data: stats.ninhos_por_status, title: 'Ninhos por Status', colors: ['#28a745', '#ffc107', '#dc3545'] });
        renderChart('riscoChart', { type: 'doughnut', data: stats.ninhos_por_risco, title: 'Ninhos por Risco', colors: ['#17a2b8', '#fd7e14', '#e83e8c'] });
        renderChart('regioesChart', { type: 'bar', data: Object.fromEntries(rankingStats.regioes_top.map(i => [i.regiao, i.total_ninhos])), title: 'Top Regiões', yAxis: true, colors: ['rgba(0,123,255,0.7)'] });
    } catch (error) {
        showAlert(error.message, 'error');
    }
}

function renderChart(canvasId, { type, data, title, colors, yAxis = false }) {
    if (chartInstances[canvasId]) chartInstances[canvasId].destroy();
    const ctx = sel(`#${canvasId}`)?.getContext('2d');
    if (!ctx) return;
    chartInstances[canvasId] = new Chart(ctx, {
        type, data: { labels: Object.keys(data), datasets: [{ data: Object.values(data), backgroundColor: colors }] },
        options: {
            indexAxis: yAxis ? 'y' : 'x', responsive: true,
            plugins: { title: { display: true, text: title }, legend: { display: type !== 'bar' }, datalabels: { color: '#fff', font: { weight: 'bold' }, formatter: val => val > 0 ? val : '' } }
        }
    });
}

// --- RANKING ---
async function loadRanking(periodo) {
    dashboard.querySelector('.ranking-btn.active')?.classList.remove('active');
    dashboard.querySelector(`.ranking-btn[data-periodo="${periodo}"]`).classList.add('active');
    
    const listEl = sel('#ranking-list');
    listEl.innerHTML = '<p>Carregando ranking...</p>';
    try {
        const data = await apiCall(`/ranking?periodo=${periodo}`);
        if (data.ranking.length === 0) {
            listEl.innerHTML = '<p>Ninguém no ranking para este período ainda.</p>';
            return;
        }
        listEl.innerHTML = data.ranking.map(user => {
            const medal = { 1: '🥇', 2: '🥈', 3: '🥉' }[user.posicao] || `${user.posicao}º`;
            return `<div class="ranking-item ${currentUser.id === user.user_id ? 'current-user' : ''} rank-${user.posicao}"><div class="posicao">${medal}</div><div class="info"><div class="nome">${user.nome_completo}</div><div class="username">@${user.username}</div></div><div class="pontos"><div class="valor">${user.total_pontos}</div><div class="username">pontos</div></div></div>`;
        }).join('');
    } catch (error) {
        listEl.innerHTML = `<p style="color:red;">${error.message}</p>`;
    }
}

// --- RELATÓRIOS ---
async function loadReportDataAndRenderTable() {
    const container = sel('#report-table-container');
    container.innerHTML = '<p>Carregando todos os registros...</p>';
    try {
        allNestsReportData = await apiCall('/relatorios/ninhos/data');
        sel('#filter-regiao').value = '';
        sel('#filter-status').value = '';
        sel('#filter-risco').value = '';
        applyReportFilters();
    } catch (error) {
        container.innerHTML = `<p style="color:red;">${error.message}</p>`;
    }
}

function applyReportFilters() {
    const regiaoFilter = sel('#filter-regiao').value.toLowerCase();
    const statusFilter = sel('#filter-status').value;
    const riscoFilter = sel('#filter-risco').value;

    const filteredData = allNestsReportData.filter(ninho => {
        const matchRegiao = ninho.regiao.toLowerCase().includes(regiaoFilter);
        const matchStatus = !statusFilter || ninho.status === statusFilter;
        const matchRisco = !riscoFilter || ninho.risco === riscoFilter;
        return matchRegiao && matchStatus && matchRisco;
    });

    renderReportTable(filteredData);
}
function renderReportTable(data) {
    const container = sel('#report-table-container');
    const countEl = sel('#report-results-count');
    countEl.textContent = `${data.length} resultado(s) encontrado(s).`;

    if (data.length === 0) {
        container.innerHTML = '<p>Nenhum registro encontrado com os filtros aplicados.</p>';
        return;
    }

    container.innerHTML = `
        <table class="report-table">
            <thead>
                <tr>
                    <th>Região</th>
                    <th>Ovos</th>
                    <th>Status</th>
                    <th>Risco</th>
                    <th>Data</th>
                    <th>Voluntário</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(n => {
                    // CORREÇÃO: Capitaliza a primeira letra para melhor visualização
                    const riscoCapitalized = n.risco.charAt(0).toUpperCase() + n.risco.slice(1);
                    return `
                    <tr>
                        <td>${n.regiao}</td>
                        <td>${n.quantidade_ovos}</td>
                        <td>${n.status}</td>
                        <!-- MUDANÇA AQUI: Adiciona a bolinha na tabela de relatórios -->
                        <td>${getRiskIndicatorHTML(n.risco)} ${riscoCapitalized}</td>
                        <td>${new Date(n.data_registro).toLocaleDateString('pt-BR')}</td>
                        <td>${n.usuario_nome}</td>
                    </tr>
                `}).join('')}
            </tbody>
        </table>
    `;
}

// --- ADMIN ---
async function loadAdminPanel() {
    const listEl = sel('#admin-list');
    listEl.innerHTML = '<p>Carregando usuários...</p>';
    try {
        const users = await apiCall('/admin/users');
        listEl.innerHTML = users.map(u => `
            <div class="ranking-item">
                <div class="info" style="flex-grow:2">
                    <div>${u.nome_completo} <span style="font-size:0.8em; color: ${u.is_admin ? 'var(--primary-color)' : '#777'}">${u.is_admin ? '(Admin)' : ''}</span></div>
                    <div class="username"><a href="mailto:${u.email}" style="color:#007bff;text-decoration:none;">${u.email}</a></div>
                </div>
                <div class="pontos"><button class="btn" style="font-size:12px;padding:8px;background-color:${u.ativo ? '#6c757d':'#28a745'}" ${currentUser.id === u.id ? 'disabled':''} onclick="toggleUser(${u.id},'ativo',${!u.ativo})">${u.ativo?'Desativar':'Ativar'}</button></div>
                <div class="pontos"><button class="btn" style="font-size:12px;padding:8px;background-color:${u.is_admin ? '#dc3545':'#007bff'}" ${currentUser.id === u.id ? 'disabled':''} onclick="toggleUser(${u.id},'is_admin',${!u.is_admin})">${u.is_admin?'Revogar Admin':'Tornar Admin'}</button></div>
            </div>`).join('');
    } catch (error) {
        listEl.innerHTML = `<p style="color:red;">${error.message}</p>`;
    }
}

async function toggleUser(userId, field, value) {
    if (!confirm(`Tem certeza que deseja alterar '${field}'?`)) return;
    try {
        await apiCall(`/admin/users/${userId}`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({[field]: value}) });
        showAlert('Usuário atualizado!', 'success');
        loadAdminPanel();
    } catch (error) {
        showAlert(error.message, 'error');
    }
}