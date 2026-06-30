# RAG Context Packer Knapsack

Número da Lista: 19  
Conteúdo da Disciplina: Programação Dinâmica

---

## Alunos

| Matrícula | Aluno |
|-----------|--------|
| 231033737 | Artur Mendonça Arruda |
| 231035464 | Lucas Mendonça Arruda |

---

## Sobre

O projeto resolve o problema de otimização de contexto (Context Packing) para sistemas RAG (Retrieval-Augmented Generation) aplicando o algoritmo clássico da Mochila Booleana (Knapsack 0/1). O objetivo é selecionar estrategicamente o conjunto mais informativo de fragmentos de texto (chunks) para injeção no prompt de um LLM, respeitando o limite da janela de contexto.

### Modelagem do Pipeline de Contexto
Cada fragmento de texto recuperado de um banco de dados vetorial possui um tamanho em tokens (peso) e uma pontuação de relevância gerada via similaridade de cosseno (lucro). O sistema constrói uma matriz de otimização para determinar a combinação exata de fragmentos que maximiza o ganho informacional total sem exceder a cota restrita de tokens.

### Programação Dinâmica vs Abordagem Gananciosa
Estratégias gananciosas baseadas em ordenação decrescente de scores desperdiçam espaço ao processar fragmentos densos, criando lacunas subótimas no prompt. A aplicação da Programação Dinâmica Bottom-Up garante a solução matematicamente ótima, orquestrando trocas precisas de blocos pesados por múltiplos fragmentos menores de alto valor semântico.

## Vídeo

[Link Vídeo](https://youtu.be/m_3WlgFVDOA)

## Screenshots

![Erro(backend nao inicializado)](../G19_Programacao_Dinamica_PA-26.1/docs/imagens/erro_site.png)
![Interface do site](../G19_Programacao_Dinamica_PA-26.1/docs/imagens/site.png)
![Knapsack - Matriz DP](../G19_Programacao_Dinamica_PA-26.1/docs/imagens/matriz_dp.png)
![knapsack - find solution](../G19_Programacao_Dinamica_PA-26.1/docs/imagens/traceback.png)
![terminal - Mock](../G19_Programacao_Dinamica_PA-26.1/docs/imagens/terminal_mock.png)
![terminal - Gemini](../G19_Programacao_Dinamica_PA-26.1/docs/imagens/terminal_gemini.png)

## Instalação

Linguagem: Python, C++17  
Biblioteca: google-genai, python-dotenv 

Pré-requisitos:
- Python 3.x
- Compilador GCC (`g++`) habilitado com suporte a C++17
- uv (gerenciador de dependências)

```bash
sudo apt update
sudo apt install g++ make python3-pip -y
```

O gerenciador `uv` cria e ativa o ambiente virtual automaticamente com base nas configurações do projeto.

## Uso

Clone o repositório e inicie o orquestrador do backend:

```bash
uv run python src/rag_orchestrator.py 
```

Acesse a URL do GitHub Pages do repositório ou abra o arquivo `docs/index.html` localmente para interagir com a interface gráfica.

O sistema opera em dois modos distintos de orquestração:

### Operação Simulada (com mock)
Acionado automaticamente pela ausência de credenciais de API. O backend gera um dataset vetorial sintético contendo 100 fragmentos. Os pesos (tokens) e lucros (scores) são distribuídos através de uma semente pseudoaleatória, permitindo validações de carga e estresse da engine C++ sem consumo de cotas de rede.

### Operação Realista (embeddings via API)
Acionado pela presença da chave do Google Gemini. O backend processa o arquivo texto local (knowledge_base.txt) contendo a obra Dom Casmurro. O modelo gemini-embedding-001 realiza a vetorização de cada parágrafo. O motor calcula a similaridade de cosseno contra a pergunta base ("Quem é Capitu e por que Bentinho desconfiava dela?"), com o objetivo de extrair a maior relevância semântica de cada chunk textual.

---

### Configuração de Infraestrutura (API)

Para habilitar a operação realista:

1. Crie o arquivo de variáveis de ambiente (`.env`) no diretório raiz do projeto.
2. Acesse o [Google AI Studio](https://aistudio.google.com/) e gere uma chave de acesso (API Key).
3. Adicione a credencial ao arquivo `.env`:

```bash
GEMINI_API_KEY=sua_chave_aqui
```

A reinicialização do orquestrador ativará o consumo da API.

> **Nota:** A vetorização do conteúdo extenso ocorre em sub-lotes programados para evitar bloqueios por rate limit (Resource Exhausted). O processamento inicial completo exige entre 120 e 200 segundos. Aguarde a inicialização da porta 5000 no terminal.

## Histórico de Versões

| Versão | Descrição | Autor(es) | Data | Revisor(es) | Data de Revisão |
|--------|-----------|-----------|------|-------------|-----------------|
| 1.0 | Adicionando seções iniciais e imagens de screenshots. | [Lucas Mendonça Arruda](https://github.com/lucasarruda9) | 29/06/2026 | [Artur Mendonça Arruda](https://github.com/ArtyMend07) | 30/06/2026 |
| 1.1 | Refatoração estrutural da documentação e correção de sintaxe de execução. | [Artur Mendonça Arruda](https://github.com/ArtyMend07) | 30/06/2026 | [Artur Mendonça Arruda](https://github.com/ArtyMend07) | 30/06/2026 |
