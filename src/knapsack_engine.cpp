#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include "dp_core.h"

using namespace std;

vector<string> realizar_traceback(const vector<vector<double>>& matriz_otimizacao_dp, int capacidade_maxima, const vector<FragmentoTexto>& base_de_chunks, int& out_tokens_usados) {
    vector<string> ids_escolhidos;
    int total_fragmentos = base_de_chunks.size();
    int capacidade_restante = capacidade_maxima;
    out_tokens_usados = 0;
    
    for (int iterador_reverso = total_fragmentos; iterador_reverso > 0 && capacidade_restante > 0; --iterador_reverso) {
        if (matriz_otimizacao_dp[iterador_reverso][capacidade_restante] != matriz_otimizacao_dp[iterador_reverso - 1][capacidade_restante]) {
            ids_escolhidos.push_back(base_de_chunks[iterador_reverso - 1].identificador);
            capacidade_restante -= base_de_chunks[iterador_reverso - 1].custo_tokens;
            out_tokens_usados += base_de_chunks[iterador_reverso - 1].custo_tokens;
        }
    }

    reverse(ids_escolhidos.begin(), ids_escolhidos.end());
    return ids_escolhidos;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int capacidade_maxima_tokens;
    if (!(cin >> capacidade_maxima_tokens)) return 0;

    int total_fragmentos;
    if (!(cin >> total_fragmentos)) return 0;

    vector<FragmentoTexto> base_de_chunks(total_fragmentos);
    for (int i = 0; i < total_fragmentos; ++i) {
        cin >> base_de_chunks[i].identificador >> base_de_chunks[i].custo_tokens >> base_de_chunks[i].score_relevancia;
    }

    vector<vector<double>> matriz_dp = construir_matriz_dp(capacidade_maxima_tokens, base_de_chunks);

    int tokens_usados = 0;
    vector<string> escolhidos = realizar_traceback(matriz_dp, capacidade_maxima_tokens, base_de_chunks, tokens_usados);

    double max_score = matriz_dp[total_fragmentos][capacidade_maxima_tokens];

    cout << "MAX_SCORE=" << max_score << "\n";
    cout << "TOKENS_USED=" << tokens_usados << "\n";
    cout << "SELECTED_COUNT=" << escolhidos.size() << "\n";
    cout << "SELECTED_IDS=";
    
    for (size_t i = 0; i < escolhidos.size(); ++i) {
        cout << escolhidos[i] << (i + 1 == escolhidos.size() ? "" : ",");
    }
    cout << "\n";

    return 0;
}
