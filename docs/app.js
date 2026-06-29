document.addEventListener("DOMContentLoaded", async () => {
    let payload_dados;
    try {
        const resposta = await fetch('data.json');
        if (!resposta.ok) throw new Error("Erro 404");
        payload_dados = await resposta.json();
    } catch (e) {
        console.warn("[WARN] Arquivo data.json ausente. Carregando snapshot offline de contingencia.");
        payload_dados = {
            max_tokens: 4096,
            raw_chunks: [],
            greedy_result: {
                score_total: 12.4500,
                tokens_usados: 4010,
                selected_ids: ["chunk_001", "chunk_005", "chunk_012"]
            },
            knapsack_result: {
                score_total: 14.8900,
                tokens_usados: 4090,
                selected_ids: ["chunk_002", "chunk_003", "chunk_008", "chunk_015", "chunk_020"]
            }
        };
        
        for(let i = 0; i < 100; i++) {
            payload_dados.raw_chunks.push({
                id: `chunk_${i.toString().padStart(3, '0')}`,
                tokens: Math.floor(Math.random() * 500) + 50,
                score: (Math.random() * 0.9).toFixed(4)
            });
        }
    }

    document.getElementById("max-tokens").textContent = `${payload_dados.max_tokens} TOKENS`;
    
    const greedy = payload_dados.greedy_result;
    document.getElementById("greedy-score").textContent = greedy.score_total.toFixed(4);
    document.getElementById("greedy-tokens").textContent = `${greedy.tokens_usados} / ${payload_dados.max_tokens}`;
    
    const greedyPct = (greedy.tokens_usados / payload_dados.max_tokens) * 100;
    setTimeout(() => {
        document.getElementById("greedy-bar").style.width = `${greedyPct}%`;
    }, 500);

    renderChunks(greedy.selected_ids, payload_dados.raw_chunks, "greedy-chunks");

    const dp = payload_dados.knapsack_result;
    document.getElementById("dp-score").textContent = dp.score_total.toFixed(4);
    document.getElementById("dp-tokens").textContent = `${dp.tokens_usados} / ${payload_dados.max_tokens}`;
    
    const dpPct = (dp.tokens_usados / payload_dados.max_tokens) * 100;
    setTimeout(() => {
        document.getElementById("dp-bar").style.width = `${dpPct}%`;
    }, 500);

    renderChunks(dp.selected_ids, payload_dados.raw_chunks, "dp-chunks");
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
