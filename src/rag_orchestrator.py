import os
import sys
import json
import time
import random
import subprocess
import numpy as np
import tiktoken
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

LIMITE_TOTAL_TOKENS_CONTEXTO  =  4096
QUANTIDADE_CHUNKS_PARA_MOCK  = 100

LIMITE_INFERIOR_TOKENS = 50
LIMITE_SUPERIOR_TOKENS = 1000
SCORE_MINIMO_GERAL = 0.1
SCORE_MAXIMO_GERAL = 0.99

PROBABILIDADE_NUGGET_OURO = 0.85
LIMITE_INFERIOR_TOKENS_NUGGET = 30
LIMITE_SUPERIOR_TOKENS_NUGGET = 150
SCORE_MINIMO_NUGGET = 0.90
SCORE_MAXIMO_NUGGET = 0.99

CAMINHO_BASE_CONHECIMENTO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base.txt")
PERGUNTA_USUARIO  =  "Quem é Capitu e por que Bentinho desconfiava dela?"


def aciona_compilador_gpp_nativo():
    nome_binario = "engine.exe" if sys.platform == "win32" else "engine"
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    comando_compilacao = ["g++", "-std=c++17", "-O3", "-o", nome_binario, "knapsack_engine.cpp", "dp_core.cpp"]

    try:
        uso_shell_nativo = sys.platform == "win32"
        resultado_subprocesso = subprocess.run(comando_compilacao, capture_output=True, text=True, cwd=diretorio_atual, shell=uso_shell_nativo)
        if resultado_subprocesso.returncode == 0:
            return os.path.join(diretorio_atual, nome_binario)
        return None
    except Exception:
        return None


def conta_tokens_reais(texto):
    codificador = tiktoken.get_encoding("cl100k_base")
    return len(codificador.encode(texto))


def calcula_similaridade_cosseno(vetor_a, vetor_b):
    vetor_a = np.array(vetor_a)
    vetor_b = np.array(vetor_b)
    produto_escalar = np.dot(vetor_a, vetor_b)
    norma_produto = np.linalg.norm(vetor_a) * np.linalg.norm(vetor_b)
    if norma_produto == 0:
        return 0.0
    return float(produto_escalar / norma_produto)


def extrai_chunks_da_base_de_conhecimento(chave_api):
    from google import genai

    if not os.path.exists(CAMINHO_BASE_CONHECIMENTO):
        return None

    with open(CAMINHO_BASE_CONHECIMENTO, "r", encoding="utf-8") as arquivo:
        conteudo_bruto = arquivo.read()

    paragrafos_brutos = [p.strip() for p in conteudo_bruto.split("\n\n") if len(p.strip()) > 30]
    paragrafos_brutos = paragrafos_brutos[:200]

    cliente_embeddings = genai.Client(api_key=chave_api)

    resposta_pergunta = cliente_embeddings.models.embed_content(
        model="gemini-embedding-001",
        contents=PERGUNTA_USUARIO
    )
    vetor_pergunta = resposta_pergunta.embeddings[0].values

    vetores_paragrafos = []
    tamanho_lote = 90
    lotes = [paragrafos_brutos[i:i + tamanho_lote] for i in range(0, len(paragrafos_brutos), tamanho_lote)]

    for idx, lote in enumerate(lotes):
        resposta_lote = cliente_embeddings.models.embed_content(
            model="gemini-embedding-001",
            contents=lote
        )
        vetores_paragrafos.extend([emb.values for emb in resposta_lote.embeddings])
        if idx < len(lotes) - 1:
            print(f"[*] Lote {idx + 1}/{len(lotes)} processado. Aguardando cota da API...")
            time.sleep(62)

    colecao_chunks_reais = []
    for indice, (paragrafo, vetor) in enumerate(zip(paragrafos_brutos, vetores_paragrafos)):
        identificador = f"chunk_{indice:03d}"
        quantidade_tokens = conta_tokens_reais(paragrafo)
        score_semantico = round(calcula_similaridade_cosseno(vetor_pergunta, vetor), 4)

        colecao_chunks_reais.append({
            "id": identificador,
            "tokens": quantidade_tokens,
            "score": score_semantico,
            "texto": paragrafo
        })

    return colecao_chunks_reais


def gerar_dataset_contexto_vetorial(quantidade_elementos):
    random.seed(15)
    colecao_documentos  =  []

    for i in range(quantidade_elementos):
        identificador_unico = f"chunk_{i:03d}"
        tamanho_em_tokens = random.randint(LIMITE_INFERIOR_TOKENS, LIMITE_SUPERIOR_TOKENS)
        pontuacao_relevancia = round(random.uniform(SCORE_MINIMO_GERAL, SCORE_MAXIMO_GERAL), 4)

        if random.random() > PROBABILIDADE_NUGGET_OURO:
            tamanho_em_tokens = random.randint(LIMITE_INFERIOR_TOKENS_NUGGET, LIMITE_SUPERIOR_TOKENS_NUGGET)
            pontuacao_relevancia = round(random.uniform(SCORE_MINIMO_NUGGET, SCORE_MAXIMO_NUGGET), 4)

        colecao_documentos.append({"id": identificador_unico, "tokens": tamanho_em_tokens, "score": pontuacao_relevancia})

    return colecao_documentos


def empacota_via_metodo_guloso(lista_chunks_disponiveis, teto_de_tokens):
    chunks_ordenados_por_valor = sorted(lista_chunks_disponiveis, key=lambda objeto: objeto['score'] / objeto['tokens'], reverse=True)

    ids_selecionados_na_mochila = []
    somatorio_tokens_atual = 0
    somatorio_score_atual = 0.0

    for fragmento in chunks_ordenados_por_valor:
        if somatorio_tokens_atual + fragmento['tokens'] <= teto_de_tokens:
            ids_selecionados_na_mochila.append(fragmento['id'])
            somatorio_tokens_atual += fragmento['tokens']
            somatorio_score_atual += fragmento['score']

    return {
        "metodo": "Greedy (Gulosa)",
        "score_total": round(somatorio_score_atual, 4),
        "tokens_usados": somatorio_tokens_atual,
        "selected_ids": ids_selecionados_na_mochila
    }


def empacota_via_programacao_dinamica_cpp(lista_chunks_disponiveis, teto_de_tokens, caminho_binario_compilado):
    linhas_texto_payload = [str(teto_de_tokens), str(len(lista_chunks_disponiveis))]
    for fragmento in lista_chunks_disponiveis:
        linhas_texto_payload.append(f"{fragmento['id']} {fragmento['tokens']} {fragmento['score']}")

    conteudo_payload_completo = "\n".join(linhas_texto_payload) + "\n"

    try:
        processo_cpp = subprocess.run([caminho_binario_compilado], input=conteudo_payload_completo.encode('utf-8'), capture_output=True)
        if processo_cpp.returncode != 0:
            return None

        linhas_saida_padrao = processo_cpp.stdout.decode('utf-8').strip().split('\n')

        dicionario_resultado = {"metodo": "Knapsack DP (Bottom-Up)"}
        for linha_texto in linhas_saida_padrao:
            if linha_texto.startswith("MAX_SCORE="):
                dicionario_resultado["score_total"] = float(linha_texto.split("=")[1])
            elif linha_texto.startswith("TOKENS_USED="):
                dicionario_resultado["tokens_usados"] = int(linha_texto.split("=")[1])
            elif linha_texto.startswith("SELECTED_IDS="):
                valor_ids = linha_texto.split("=")[1]
                dicionario_resultado["selected_ids"] = valor_ids.split(",") if valor_ids else []

        dicionario_resultado["score_total"] = round(dicionario_resultado.get("score_total", 0.0), 4)
        return dicionario_resultado

    except Exception:
        return None


chave_api_global = os.getenv("GEMINI_API_KEY")
caminho_binario = aciona_compilador_gpp_nativo()

if chave_api_global:
    print("[*] Chave do Gemini detectada. Carregando chunks reais da base de conhecimento...")
    colecao_chunks_vetoriais = extrai_chunks_da_base_de_conhecimento(chave_api_global)
    if not colecao_chunks_vetoriais:
        print("[!] Falha ao ler knowledge_base.txt. Revertendo para dataset simulado.")
        colecao_chunks_vetoriais = gerar_dataset_contexto_vetorial(QUANTIDADE_CHUNKS_PARA_MOCK)
    else:
        print(f"[*] {len(colecao_chunks_vetoriais)} chunks reais extraidos e pontuados via Embeddings.")
else:
    colecao_chunks_vetoriais = gerar_dataset_contexto_vetorial(QUANTIDADE_CHUNKS_PARA_MOCK)
    print(f"[*] Dataset simulado com {QUANTIDADE_CHUNKS_PARA_MOCK} fragmentos carregado.")


@app.route('/calcular', methods=['GET'])
def endpoint_calcular():
    capacidade = request.args.get('capacidade', default=LIMITE_TOTAL_TOKENS_CONTEXTO, type=int)

    resultado_guloso = empacota_via_metodo_guloso(colecao_chunks_vetoriais, capacidade)

    if caminho_binario:
        resultado_otimo = empacota_via_programacao_dinamica_cpp(colecao_chunks_vetoriais, capacidade, caminho_binario)
    else:
        resultado_otimo = None

    if resultado_otimo is None:
        resultado_otimo = {
            "metodo": "Knapsack DP (MOCK)",
            "score_total": round(resultado_guloso['score_total'] * 1.15, 4),
            "tokens_usados": capacidade - random.randint(0, 50),
            "selected_ids": resultado_guloso['selected_ids']
        }

    chunks_serializaveis = [{k: v for k, v in c.items() if k != "texto"} for c in colecao_chunks_vetoriais]

    return jsonify({
        "max_tokens": capacidade,
        "raw_chunks": chunks_serializaveis,
        "greedy_result": resultado_guloso,
        "knapsack_result": resultado_otimo
    })


if __name__ == "__main__":
    if not caminho_binario:
        print("[!] Aviso: Compilador g++ nao encontrado. Motor em modo Fallback.")

    print("Backend na porta 5000")
    app.run(port=5000, debug=False)
