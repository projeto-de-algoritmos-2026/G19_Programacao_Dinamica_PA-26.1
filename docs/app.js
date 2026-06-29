document.addEventListener("DOMContentLoaded", () => {
    const slider = document.getElementById("tokens-slider");
    const inputNum = document.getElementById("tokens-input");

    // Função centralizada para buscar os dados na sua API Flask
    async function buscarDadosDaAPI(capacidade) {
        // Validação estrita dos limites solicitados
        let valorValidado = parseInt(capacidade);
        
        if (isNaN(valorValidado) || valorValidado < 10) {
            valorValidado = 10;
        } else if (valorValidado > 100000) {
            valorValidado = 100000;
        }
        
        // Atualiza os campos visuais para o valor corrigido/validado
        inputNum.value = valorValidado;
        if (valorValidado <= slider.max) {
            slider.value = valorValidado;
        }

        try {
            // Dispara a chamada HTTP para o servidor Flask local
            const resposta = await fetch(`http://127.0.0.1:5000/calcular?capacidade=${valorValidado}`);
            if (!resposta.ok) throw new Error("Erro na API");
            
            const payload_dados = await resposta.json();
            const jsonPreview = document.getElementById("json-preview");
            if (jsonPreview) {
                // Transforma o objeto em texto JSON identado com 2 espaços
                jsonPreview.textContent = JSON.stringify(payload_dados, null, 2);
            }
            // Atualiza os componentes do seu layout escuro estilizado
            document.getElementById("max-tokens").textContent = `${payload_dados.max_tokens} TOKENS`;
            
            // Renderiza o painel Guloso (Greedy)
            const greedy = payload_dados.greedy_result;
            document.getElementById("greedy-score").textContent = greedy.score_total.toFixed(4);
            document.getElementById("greedy-tokens").textContent = `${greedy.tokens_usados} / ${payload_dados.max_tokens}`;
            document.getElementById("greedy-bar").style.width = `${(greedy.tokens_usados / payload_dados.max_tokens) * 100}%`;
            renderChunks(greedy.selected_ids, payload_dados.raw_chunks, "greedy-chunks");

            // Renderiza o painel de Programação Dinâmica (C++)
            const dp = payload_dados.knapsack_result;
            document.getElementById("dp-score").textContent = dp.score_total.toFixed(4);
            document.getElementById("dp-tokens").textContent = `${dp.tokens_usados} / ${payload_dados.max_tokens}`;
            document.getElementById("dp-bar").style.width = `${(dp.tokens_usados / payload_dados.max_tokens) * 100}%`;
            renderChunks(dp.selected_ids, payload_dados.raw_chunks, "dp-chunks");

        } catch (error) {
            console.error("[ERRO] Certifique-se de que o servidor Flask está rodando:", error);
        }
    }

    // Evento 1: Usuário alterou o Slider
    slider.addEventListener("change", (e) => {
        buscarDadosDaAPI(e.target.value);
    });

    // Sincronização visual em tempo real enquanto arrasta
    slider.addEventListener("input", (e) => {
        inputNum.value = e.target.value;
    });

    // Evento 2: Usuário digitou na caixinha e apertou Enter ou mudou de campo
    inputNum.addEventListener("change", (e) => {
        buscarDadosDaAPI(e.target.value);
    });

    // Carrega o cenário inicial (4096 tokens) automaticamente ao abrir a página
    buscarDadosDaAPI(4096);
});

function renderChunks(selectedIds, allChunks, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    const chunkMap = {};
    allChunks.forEach(c => chunkMap[c.id] = c);

    selectedIds.forEach(id => {
        const chunk = chunkMap[id] || { id: id, tokens: '?', score: '?' };
        const div = document.createElement("div");
        div.className = "chunk";
        div.innerHTML = `
            <span class="id">${chunk.id}</span>
            <span class="score">⭐ ${chunk.score}</span>
            <span class="tokens">📦 ${chunk.tokens} tk</span>
        `;
        container.appendChild(div);
    });
}