#include "dp_core.h"
#include <algorithm>

using namespace std;

vector<vector<double>> construir_matriz_dp(int capacidade_maxima, const vector<FragmentoTexto>& base_de_chunks) {
    int total_fragmentos = base_de_chunks.size();
    vector<vector<double>> matriz_otimizacao_dp(total_fragmentos + 1, vector<double>(capacidade_maxima + 1, 0.0));

    for (int iterador_item = 1; iterador_item <= total_fragmentos; ++iterador_item) {
        int peso_atual = base_de_chunks[iterador_item - 1].custo_tokens;
        double valor_atual = base_de_chunks[iterador_item - 1].score_relevancia;

        for (int peso_teste = 1; peso_teste <= capacidade_maxima; ++peso_teste) {
            if (peso_atual <= peso_teste) {
                double incluir_fragmento = valor_atual + matriz_otimizacao_dp[iterador_item - 1][peso_teste - peso_atual];
                double ignorar_fragmento = matriz_otimizacao_dp[iterador_item - 1][peso_teste];
                matriz_otimizacao_dp[iterador_item][peso_teste] = max(incluir_fragmento, ignorar_fragmento);
            } else {
                matriz_otimizacao_dp[iterador_item][peso_teste] = matriz_otimizacao_dp[iterador_item - 1][peso_teste];
            }
        }
    }

    return matriz_otimizacao_dp;
}
