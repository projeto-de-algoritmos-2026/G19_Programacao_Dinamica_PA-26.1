#ifndef DP_CORE_H
#define DP_CORE_H
#include <vector>
#include <string>

struct FragmentoTexto {
    std::string identificador;
    int custo_tokens;
    double score_relevancia;
};

std::vector<std::vector<double>> construir_matriz_dp(int capacidade_maxima, const std::vector<FragmentoTexto>& base_de_chunks);

#endif
