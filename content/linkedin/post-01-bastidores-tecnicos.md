# Post 01 — Bastidores Técnicos (Arquitetura)
**Tipo:** Post de texto
**Objetivo:** Mostrar a arquitetura enquanto a curiosidade está no pico. Hook para engenheiros, cientistas de dados e tech leads.
**Tom:** Técnico mas acessível. Decisões de design explicadas.

---

No carrossel que publiquei ontem, você viu o que o sistema entrega.

Hoje: o que está por trás.

**3 agentes. 2 bancos de dados. 1 pergunta em linguagem natural.**

---

🏗️ **A arquitetura: The Ledger + The Memory**

O sistema separa dois tipos de conhecimento:

**📊 The Ledger (Postgres)**
Dados exatos de sell-out — faturamento, volume, share, sazonalidade.
O agente SalesAnalyst gera SQL automaticamente e faz JOINs entre vendas, SKUs, marcas e lojas.

**🧠 The Memory (Qdrant)**
Reviews de consumidores convertidos em vetores.
O agente MarketResearcher busca por *significado*, não por palavra-chave — entende que "sabor que decepcionou" é uma reclamação mesmo sem a palavra "ruim".

**✍️ O Reporter**
Recebe os outputs dos dois e sintetiza o relatório final.
Não acessa banco de dados — só raciocina sobre o que os outros trouxeram.

---

⚙️ **Stack técnica**

- **Orquestração:** CrewAI 1.14 (processo sequencial, contexto compartilhado)
- **LLM:** Groq + Llama 3.3 70B (inferência rápida, gratuito)
- **Vector DB:** Qdrant 1.8 (busca semântica dos reviews)
- **SQL:** Postgres 16 com dados gerados via ShadowTraffic
- **Interface:** Chainlit 2.11 (chat com steps visíveis em tempo real)

---

💡 **O maior desafio técnico**

A coluna `periodo` no Postgres é `VARCHAR(10)` no formato `'YYYY-MM'`.

O LLM gerava `EXTRACT(MONTH FROM periodo)` — que explodia com erro de tipo.

A solução: instruir o agente explicitamente no description da tool:

```
IMPORTANTE: use SUBSTRING(periodo, 6, 2)::integer
para extrair o mês. NUNCA use EXTRACT() nessa coluna.
```

Pequeno detalhe. Grande diferença na confiabilidade do sistema.

---

No próximo post: o que esse sistema responde que uma dashboard tradicional não conseguiria responder. 👇

---

#EngenhariaDeDados #AIEngineering #CrewAI #LLM #Qdrant #Postgres #Chainlit #MultiAgent #Python #DataEngineering
