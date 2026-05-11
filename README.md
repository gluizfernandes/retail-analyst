# Malu Doces — Retail Analyst

Sistema multi-agente de inteligencia de mercado para o setor de chocolates.
Combina dados estruturados de sell-out (SQL) com voz do consumidor via RAG (vetores)
para gerar relatorios executivos automaticamente.

Dados 100% sinteticos gerados via ShadowTraffic — marcas reais, numeros ficticios.

---

## Arquitetura

```
ShadowTraffic
    |
    +---> Postgres (The Ledger)     <--- SalesAnalyst (SQL queries)
    |     marcas, skus, lojas,                    |
    |     vendas (50k registros)                  |
    |                                             v
    +---> Qdrant (The Memory)  <--- MarketResearcher (busca semantica)
          chocolate_reviews                       |
          (800 reviews PT-BR)                     |
                                                  v
                                          Reporter (sintese)
                                                  |
                                                  v
                                     Relatorio Executivo em PT-BR
                                     Interface Chainlit
```

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Dados sinteticos | ShadowTraffic |
| Ledger (SQL) | Postgres 16 via Docker |
| Memory (vetores) | Qdrant 1.8 via Docker |
| Embeddings | fastembed (BAAI/bge-small-en-v1.5) |
| Agentes | CrewAI 1.14 |
| LLM | Groq — Llama 3.3 70B Versatile |
| Interface | Chainlit 2.11 |

## Dataset

**20 marcas reais** de 6 fabricantes:

| Fabricante | Marcas |
|-----------|--------|
| Mondelez | Lacta, Bis, Sonho de Valsa, Ouro Branco, Diamante Negro |
| Nestle | Kit Kat, Prestigio, Alpino, Charge, Sensacao, Garoto, Serenata, Talento |
| Hersheys | Hersheys, Special Dark |
| Ferrero | Ferrero Rocher, Raffaello |
| Harald | Melken, Unique |
| Arcor | Bon o Bon |

**44 SKUs** em 6 categorias: tablete, bombom, trufas, drageados, kit_presente, paes_de_mel

**50.000 registros de vendas** — 12 meses (2024) com sazonalidade simulada:
Pascoa (+40%), Natal (+30%), Dia dos Namorados (+20%), Dia das Criancas (+15%)

**800 reviews** em portugues com sentimento, canal de compra e marca.

## Quickstart

### 1. Pre-requisitos

- Docker e Docker Compose
- Python 3.11+
- Chave de API Anthropic

### 2. Configurar variaveis de ambiente

```bash
cp .env.example .env
# editar .env e inserir GROQ_API_KEY (gratuito em console.groq.com)
```

### 3. Subir infraestrutura e gerar dados

```bash
cd gen
docker compose up
# aguardar ShadowTraffic finalizar (~2 min)
```

### 4. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### 5. Ingerir reviews no Qdrant

```bash
# copiar o JSONL gerado pelo ShadowTraffic
docker cp $(docker ps -qf "name=shadowtraffic"):/data/reviews gen/data/

python src/ingest_reviews.py
```

### 6. Rodar a crew direto (CLI)

```bash
python src/crew/crew.py
```

### 7. Interface conversacional (Chainlit)

```bash
chainlit run src/app.py
# abrir http://localhost:8000
```

## Exemplos de Perguntas

```
Quais marcas tiveram maior faturamento em 2024?

Como foi a performance na Pascoa comparado ao Natal?

Qual o share da Mondelez no canal farmacia?

O que os consumidores falam sobre o Kit Kat?

Quais tendencias aparecem nas avaliacoes de chocolates premium?

Qual a marca com melhor custo-beneficio segundo os consumidores?
```

## Estrutura do Projeto

```
retail-analyst/
  gen/
    init.sql              # Schema + marcas e SKUs estaticos
    shadowtraffic.json    # Geracao de lojas, vendas, reviews
    docker-compose.yml    # Postgres (5433) + Qdrant (6334)
  src/
    app.py                # Interface Chainlit
    ingest_reviews.py     # JSONL -> Qdrant
    crew/
      config/
        agents.yaml       # Perfis dos 3 agentes
        tasks.yaml        # Tarefas encadeadas
      tools.py            # postgres_execute_sql + qdrant_semantic_search
      crew.py             # RetailAnalystCrew (CrewBase)
  .claude/
    agents/               # Agentes Claude Code (sales-analyst, market-researcher, reporter)
    kb/chocolate-retail/  # Base de conhecimento do dominio
  public/
    custom.css            # Identidade visual Malu Doces
  .chainlit/
    config.toml           # Tema rosa pastel
  .env.example
  requirements.txt
  README.md
```

## Identidade Visual — Malu Doces

| Token | Valor | Uso |
|-------|-------|-----|
| Rosa principal | `#F2A7BB` | Destaques, botoes |
| Lilas acento | `#C8A8E9` | Titulos, bordas |
| Creme fundo | `#FFF5E6` | Background |
| Menta positivo | `#A8D8C8` | Indicadores de crescimento |
| Chocolate texto | `#3D1C02` | Corpo do texto |
| Fonte titulos | Dancing Script | Manuscrita, artesanal |
| Fonte corpo | Lato | Sans-serif limpa |

## Agentes

| Agente | Ferramenta | Responsabilidade |
|--------|-----------|-----------------|
| SalesAnalyst | `postgres_execute_sql` | Ranking, share, sazonalidade, canais |
| MarketResearcher | `qdrant_semantic_search` | Sentimento, temas, citacoes de reviews |
| Reporter | (sintese) | Relatorio executivo em PT-BR com recomendacoes |

## Variaveis de Ambiente

| Variavel | Padrao | Descricao |
|---------|--------|----------|
| `GROQ_API_KEY` | — | Obrigatoria (gratuito em console.groq.com) |
| `RETAIL_POSTGRES_HOST` | localhost | Host do Postgres |
| `RETAIL_POSTGRES_PORT` | 5433 | Porta (nao conflita com ShopAgent) |
| `RETAIL_POSTGRES_DB` | malu_doces | Nome do banco |
| `RETAIL_QDRANT_URL` | http://localhost:6334 | URL do Qdrant |
| `RETAIL_QDRANT_COLLECTION` | chocolate_reviews | Colecao de reviews |

---

Projeto derivado do [ShopAgent](https://github.com/owshq-mec/semana-ai-data-engineer) —
Semana AI Data Engineer 2026.
