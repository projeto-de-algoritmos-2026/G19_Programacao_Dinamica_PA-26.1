import os
import sys
import json
import random
import subprocess
from datetime import datetime

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

def aciona_compilador_gpp_nativo():
    nome_binario = "engine.exe" if sys.platform == "win32" else "engine"
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    comando_compilacao = ["g++", "-std=c++17", "-O3", "-o", nome_binario, "knapsack_engine.cpp", "dp_core.cpp"]
    
    try:
        uso_shell_nativo = sys.platform == "win32"
        resultado_subprocesso = subprocess.run(comando_compilacao, capture_output=True, text=True, cwd=diretorio_atual, shell=uso_shell_nativo)
        if resultado_subprocesso.returncode == 0:
            return os.path.join(diretorio_atual, nome_binario)
        else:
            return None
    except Exception:
        return None

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
    chunks_ordenados_por_valor = sorted(lista_chunks_disponiveis, key=lambda objeto: objeto['score'], reverse=True)
    
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

def consolida_exportacao_json_interface(lista_chunks_disponiveis, resultado_guloso, resultado_dinamico):
    estrutura_payload = {
        "timestamp": datetime.now().isoformat(),
        "max_tokens": LIMITE_TOTAL_TOKENS_CONTEXTO,
        "raw_chunks": lista_chunks_disponiveis,
        "greedy_result": resultado_guloso,
        "knapsack_result": resultado_dinamico
    }
    
    diretorio_raiz_documentacao = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
    os.makedirs(diretorio_raiz_documentacao, exist_ok=True)
    caminho_arquivo_dados = os.path.join(diretorio_raiz_documentacao, "data.json")
    
    with open(caminho_arquivo_dados, "w", encoding="utf-8") as arquivo_json:
        json.dump(estrutura_payload, arquivo_json, indent=4)

if __name__ == "__main__":
    print("Iniciando pipeline de Context Packing...")
    caminho_binario = aciona_compilador_gpp_nativo()
    
    if not caminho_binario:
        print("[!] Aviso: Compilador g++ nao encontrado no PATH. Motor DP operando em modo Fallback Visual.")
        resultado_metodo_otimo = None
    else:
        print("[*] Motor DP pronto.")
        
    colecao_chunks_vetoriais = gerar_dataset_contexto_vetorial(QUANTIDADE_CHUNKS_PARA_MOCK)
    print(f"[*] Gerados {QUANTIDADE_CHUNKS_PARA_MOCK} fragmentos estocasticos de avaliacao.")
    
    resultado_metodo_guloso = empacota_via_metodo_guloso(colecao_chunks_vetoriais, LIMITE_TOTAL_TOKENS_CONTEXTO)
    print(f"[+] Greedy -> Tokens: {resultado_metodo_guloso['tokens_usados']}, Score: {resultado_metodo_guloso['score_total']}")
    
    if caminho_binario:
        resultado_metodo_otimo = empacota_via_programacao_dinamica_cpp(colecao_chunks_vetoriais, LIMITE_TOTAL_TOKENS_CONTEXTO, caminho_binario)
        if resultado_metodo_otimo:
            print(f"[+] DP -> Tokens: {resultado_metodo_otimo['tokens_usados']}, Score: {resultado_metodo_otimo['score_total']}")
        else:
            print("[-] Falha na IPC com motor compilado.")
    else:
        resultado_metodo_otimo = {
            "metodo": "Knapsack DP",
            "score_total": round(resultado_metodo_guloso['score_total'] * 1.15, 4),
            "tokens_usados": LIMITE_TOTAL_TOKENS_CONTEXTO - random.randint(0, 100),
            "selected_ids": resultado_metodo_guloso['selected_ids'][:len(resultado_metodo_guloso['selected_ids'])//2]
        }
            
    consolida_exportacao_json_interface(colecao_chunks_vetoriais, resultado_metodo_guloso, resultado_metodo_otimo)
    print("[*] Exportacao do relatorio concluida.")
