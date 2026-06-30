# RAG_Context_Packing_Knapsack

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

O projeto resolve o problema de otimização de contexto (Context Packing) para sistemas RAG (Retrieval-Augmented Generation) utilizando o algoritmo clássico da **Mochila Booleana (Knapsack 0/1)**. O objetivo é selecionar estrategicamente o conjunto mais informativo de fragmentos de texto (chunks) para injetar no prompt de um LLM, respeitando rigorosamente o limite rígido de tokens da janela de contexto sem desperdiçar espaço.

### Modelagem do Pipeline de Contexto
Cada fragmento de texto recuperado de um banco de dados vetorial possui um tamanho em tokens (que atua como o **peso**) e uma pontuação de relevância ou similaridade de cosseno (que atua como o **valor**). O sistema calcula a matriz de otimização para garantir que a combinação final de informações passadas ao modelo de linguagem maximize o ganho de informação (`score_total`), evitando estouros de contexto.

### Programação Dinâmica vs Abordagem Gulosa
Estratégias gulosas baseadas apenas na ordenação decrescente de scores falham em preencher a janela de contexto de forma ótima quando se deparam com fragmentos grandes, deixando buracos vazios de tokens. A aplicação da **Programação Dinâmica Bottom-Up** garante a solução matematicamente ótima para o preenchimento do espaço, realizando trocas inteligentes de blocos pesados por múltiplos fragmentos menores de alto valor informacional.


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
- pip

```bash
sudo apt update
sudo apt install g++ make python3-pip -y
```

O uv já cria/ativa o ambiente virtual automaticamente com base no pyproject.toml

## Uso

Após clonar o repositório e ativar as dependências, execute o script orquestrador do ecossistema:

```bash
uv run python3 rag_orchestrator.py 
```
Depois disso, acesse o link do GitHub Pages para ter acesso à interface gráfica da aplicação.

![Interface da Aplicação](./caminho/para/sua/imagem.png)

A aplicação possui dois modos de operação para alimentar o motor em C++:

### Mockado

Esse modo é utilizado de forma automática caso não seja configurada uma API de LLM no arquivo `.env`. 
Nesse modo, o sistema gera um dataset simulado com 100 fragmentos (`QUANTIDADE_CHUNKS_PARA_MOCK = 100`) usando uma semente pseudoaleatória fixa. Cada fragmento recebe um tamanho de tokens e uma nota de relevância fictícios para que você possa testar o funcionamento e a velocidade da aplicação sem gastar cota de API.

### Integração com API

Nesse modo, o ecossistema funciona como um RAG (Retrieval-Augmented Generation) realista. 
O servidor lê o arquivo de texto local `knowledge_base.txt` (que contém a base de conhecimento sobre Dom Casmurro) e utiliza o modelo `gemini-embedding-001` para gerar os vetores de cada parágrafo. Em seguida, calcula a **similaridade cosseno** entre a pergunta fixa do usuário (*"Quem é Capitu e por que Bentinho desconfiava dela?"*) e os blocos de texto, gerando scores reais baseados na semântica do conteúdo.

---

### Configurando a API (RAG Realista)

Caso deseje integrar a API para gerar os scores com embeddings reais e tornar o RAG realista, siga estes passos:

1. **Criar o arquivo de ambiente:** Crie um arquivo chamado `.env` no mesmo diretório em que se encontra o arquivo `.env.example`.
2. **Acessar o painel do Google:** Entre na plataforma do [Google AI Studio](https://aistudio.google.com/).
3. **Criar a Chave de API:** Clique no botão para criar uma nova chave de API (*Get API Key*).
4. **Vincular ao Projeto:** Vincule essa nova chave a um projeto Google Cloud existente (caso não tenha nenhum projeto criado na sua conta, crie um novo na hora).
5. **Configurar as variáveis:** Copie a chave alfanumérica gerada, abra o seu arquivo `.env` e cole-a seguindo a estrutura do `.env.example`:

```bash
GEMINI_API_KEY=sua_chave_aqui
```
Ao reiniciar o script rag_orchestrator.py, o terminal indicará que a chave foi detectada com sucesso e iniciará o processamento dos lotes de embeddings.

> **Nota** O processamento dos embeddings é feito em lotes para respeitar o limite de requisições da API do Gemini. O processo total demora cerca de **120 a 200 segundos**. Não feche o terminal, o script continuará automaticamente até liberar a porta 5000.

## Histórico de Versões

| Versão | Descrição | Autor(es) | Data | Revisor(es) |
|--------|-----------|-----------|------|-------------|
| 1.0 | Adicionando seções iniciais e imagens de screenshots | Lucas Mendonça Arruda | 29/06/2026 | Artur Mendonça Arruda |

