"""
Constrói o notebook analise.ipynb programaticamente com nbformat.

Manter o notebook como código Python facilita a revisão em diff e garante
consistência. Rodar:  python construir_notebook.py
Depois execute o notebook com nbconvert para popular as saídas.
"""

import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []


def md(texto):
    cells.append(nbf.v4.new_markdown_cell(texto.strip("\n")))


def code(texto):
    cells.append(nbf.v4.new_code_cell(texto.strip("\n")))


# ===========================================================================
# 1. INTRODUÇÃO
# ===========================================================================
md(r"""
# ☕ CaféBR — Análise Exploratória de Vendas (2024–2025)

**Autor:** analista de dados · **Ferramentas:** Python · pandas · SQL (sqlite3) · matplotlib · seaborn

> ⚠️ **AVISO — DADOS FICTÍCIOS.** A "CaféBR" **não existe**: é uma empresa **inventada**
> para este projeto de portfólio. Todas as vendas, lojas, preços e números foram
> **gerados sinteticamente por código** (`gerar_dados.py`). **Nenhum dado é real,
> sigiloso, confidencial ou vazado** — não há relação com nenhuma empresa ou pessoa
> existente. O conteúdo pode ser visto e compartilhado livremente.

---

## 1. Introdução

A **CaféBR** é uma rede fictícia de cafeterias com 5 unidades em capitais brasileiras
(São Paulo, Rio de Janeiro, Belo Horizonte, Curitiba e Porto Alegre). A diretoria quer
entender o comportamento de vendas para orientar decisões de estoque, promoções e
expansão.

### Pergunta de negócio
> **Onde, quando e como a CaféBR vende mais — e o que isso sugere para aumentar a receita?**

### Perguntas de análise
1. Quais **lojas** e **produtos** mais faturam?
2. Como a **receita evolui mês a mês**? Existe sazonalidade?
3. Qual o **ticket médio por canal** (balcão, app, delivery)?
4. Qual **forma de pagamento** domina?
5. Há diferença de vendas por **turno** e **dia da semana**?

> Todos os dados são **sintéticos** e gerados offline (`gerar_dados.py`). Nada depende
> de downloads externos ou chaves de API.
""")

# ===========================================================================
# 2. CARREGAMENTO E VISÃO GERAL
# ===========================================================================
md(r"""
## 2. Carregamento e visão geral

Importamos as bibliotecas, configuramos o estilo dos gráficos e carregamos o CSV bruto.
""")

code(r"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# Estilo visual consistente para todos os gráficos
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.figsize"] = (9, 5)
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.titleweight"] = "bold"

# Formatação de valores em Real (R$) no padrão brasileiro: 1.234,56
def reais(valor):
    return ("R$ " + f"{valor:,.2f}").replace(",", "X").replace(".", ",").replace("X", ".")

pd.set_option("display.max_columns", None)
""")

code(r"""
df = pd.read_csv("dados/vendas_cafebr.csv")
print(f"Formato: {df.shape[0]} linhas x {df.shape[1]} colunas")
df.head()
""")

md("Estrutura, tipos de dados e uso de memória:")
code("df.info()")

md("Estatísticas descritivas das colunas numéricas:")
code("df.describe()")

md("Checagem de valores nulos e de duplicatas — o que precisará de limpeza:")
code(r"""
print("Nulos por coluna:")
print(df.isna().sum())
print(f"\nLinhas duplicadas: {df.duplicated().sum()}")
""")

# ===========================================================================
# 3. LIMPEZA E PREPARAÇÃO
# ===========================================================================
md(r"""
## 3. Limpeza e preparação

Encontramos duas questões típicas de dados reais:

- **Valores nulos** em `forma_pagamento`.
- **Linhas duplicadas** (registros repetidos por erro de sistema).

Estratégia:
- Remover duplicatas exatas.
- Preencher `forma_pagamento` nula com a moda (categoria mais frequente) — decisão
  conservadora, já que representa poucos registros.
- Converter `data` para `datetime` e criar colunas derivadas para a análise:
  `receita`, `mes`, `dia_semana` e `turno`.
""")

code(r"""
antes = len(df)
df = df.drop_duplicates().reset_index(drop=True)
print(f"Duplicatas removidas: {antes - len(df)}")

# Preencher nulos de forma_pagamento com a moda
moda_pag = df["forma_pagamento"].mode()[0]
n_nulos = df["forma_pagamento"].isna().sum()
df["forma_pagamento"] = df["forma_pagamento"].fillna(moda_pag)
print(f"Nulos preenchidos em forma_pagamento: {n_nulos} (moda = '{moda_pag}')")

print("\nNulos restantes:", int(df.isna().sum().sum()))
""")

code(r"""
# Conversão de tipos e colunas derivadas
df["data"] = pd.to_datetime(df["data"])

df["receita"] = df["quantidade"] * df["preco_unitario"]
df["mes"] = df["data"].dt.to_period("M").astype(str)          # ex.: 2024-07
df["hora"] = df["data"].dt.hour

dias_pt = {0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui", 4: "Sex", 5: "Sáb", 6: "Dom"}
df["dia_semana"] = df["data"].dt.dayofweek.map(dias_pt)

def classificar_turno(h):
    if 6 <= h < 12:
        return "Manhã"
    if 12 <= h < 18:
        return "Tarde"
    return "Noite"

df["turno"] = df["hora"].apply(classificar_turno)

df[["data", "loja", "produto", "quantidade", "preco_unitario",
    "receita", "mes", "dia_semana", "turno"]].head()
""")

code(r"""
print("Receita total no período:", reais(df["receita"].sum()))
print("Ticket médio por venda:", reais(df["receita"].mean()))
print("Período:", df["data"].min().date(), "a", df["data"].max().date())
""")

# ===========================================================================
# 4. ANÁLISE
# ===========================================================================
md(r"""
## 4. Análise

Cada pergunta abaixo tem um **gráfico** e um **parágrafo de leitura** do resultado.
""")

# --- 4.1 Lojas ---
md("### 4.1 Quais lojas faturam mais?")
code(r"""
receita_loja = df.groupby("loja")["receita"].sum().sort_values(ascending=False)

ax = sns.barplot(x=receita_loja.values, y=receita_loja.index, color="#4C72B0")
ax.set_title("Receita total por loja (2024–2025)")
ax.set_xlabel("Receita (R$)")
ax.set_ylabel("Loja")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1000:.0f}k"))
for i, v in enumerate(receita_loja.values):
    ax.text(v, i, "  " + reais(v), va="center", fontsize=9)
plt.tight_layout()
plt.show()

for loja, v in receita_loja.items():
    print(f"{loja:32s} {reais(v)}")
""")
md(r"""
**Leitura:** a unidade **São Paulo - Paulista** lidera a receita com folga, seguida por
Rio de Janeiro - Ipanema. As três primeiras lojas concentram a maior parte do
faturamento. As unidades do Sul (Curitiba e Porto Alegre) fecham o ranking — candidatas
naturais a ações de marketing local para reduzir a distância para as líderes.
""")

# --- 4.2 Produtos ---
md("### 4.2 Quais produtos vendem mais?")
code(r"""
receita_prod = df.groupby("produto")["receita"].sum().sort_values(ascending=False)

ax = sns.barplot(x=receita_prod.values, y=receita_prod.index, color="#55A868")
ax.set_title("Receita total por produto")
ax.set_xlabel("Receita (R$)")
ax.set_ylabel("Produto")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1000:.0f}k"))
plt.tight_layout()
plt.show()

print("Top 5 produtos por receita:")
for p, v in receita_prod.head().items():
    print(f"  {p:20s} {reais(v)}")

# Receita por categoria
print("\nReceita por categoria:")
for c, v in df.groupby("categoria")["receita"].sum().sort_values(ascending=False).items():
    print(f"  {c:16s} {reais(v)}")
""")
md(r"""
**Leitura:** as **bebidas quentes** (cappuccino, latte, chocolate quente) e os itens de
maior ticket como o **sanduíche natural** puxam a receita. Produtos de ticket baixo e
alto giro (café expresso, pão de queijo) aparecem em volume, mas pesam menos no
faturamento. A categoria **Bebida Quente** é o coração do negócio.
""")

# --- 4.3 Receita por mês ---
md("### 4.3 Como a receita evolui mês a mês?")
code(r"""
receita_mes = df.groupby("mes")["receita"].sum()

ax = receita_mes.plot(marker="o", color="#C44E52")
ax.set_title("Evolução da receita mensal")
ax.set_xlabel("Mês")
ax.set_ylabel("Receita (R$)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1000:.0f}k"))
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

# Receita média por mês do ano (agregando 2024+2025) para ver sazonalidade
df["mes_num"] = df["data"].dt.month
saz = df.groupby("mes_num")["receita"].sum()
print("Receita por mês-calendário (soma 2024+2025):")
for m, v in saz.items():
    print(f"  mês {m:02d}: {reais(v)}")
""")
md(r"""
**Leitura:** a receita mostra **sazonalidade de inverno** — os meses de **junho, julho e
agosto** concentram os maiores valores, coerente com o consumo de bebidas quentes no
frio. O verão (dezembro a fevereiro) é o vale. Isso sugere reforçar estoque e equipe no
inverno e criar campanhas de bebidas geladas para sustentar a receita no verão.
""")

# --- 4.4 Ticket médio por canal ---
md("### 4.4 Qual o ticket médio por canal?")
code(r"""
ticket_canal = df.groupby("canal")["receita"].mean().sort_values(ascending=False)

ax = sns.barplot(x=ticket_canal.index, y=ticket_canal.values,
                 hue=ticket_canal.index, palette="crest", legend=False)
ax.set_title("Ticket médio por canal de venda")
ax.set_xlabel("Canal")
ax.set_ylabel("Ticket médio (R$)")
for i, v in enumerate(ticket_canal.values):
    ax.text(i, v, reais(v), ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.show()

print("Participação de cada canal na receita total:")
part = df.groupby("canal")["receita"].sum()
for c, v in (part / part.sum() * 100).sort_values(ascending=False).items():
    print(f"  {c:10s} {v:5.1f}%")
""")
md(r"""
**Leitura:** o **delivery** e o **app** tendem a apresentar ticket médio maior que o
balcão — pedidos digitais costumam agregar mais itens por compra. Ainda assim, o
**balcão** responde pela maior fatia da receita total por volume. Conclusão prática:
os canais digitais são alavancas de ticket; vale incentivar combos e itens adicionais no
app para elevar ainda mais o valor por pedido.
""")

# --- 4.5 Forma de pagamento ---
md("### 4.5 Qual forma de pagamento domina?")
code(r"""
pag = df["forma_pagamento"].value_counts()

ax = pag.plot(kind="pie", autopct="%1.1f%%", startangle=90,
              colors=sns.color_palette("pastel"), ylabel="")
ax.set_title("Distribuição das formas de pagamento")
plt.tight_layout()
plt.show()

print("Transações por forma de pagamento:")
for f, n in pag.items():
    print(f"  {f:10s} {n:4d}  ({n/len(df)*100:.1f}%)")
""")
md(r"""
**Leitura:** **cartão** e **Pix** dominam os pagamentos, com o dinheiro em queda —
padrão típico do varejo brasileiro pós-popularização do Pix. Como Pix tem custo de
transação baixíssimo, incentivá-lo (ex.: pequeno desconto) pode reduzir taxas de cartão
sem afastar o cliente.
""")

# --- 4.6 Turno e dia da semana ---
md("### 4.6 Há diferença por turno e dia da semana?")
code(r"""
ordem_dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
ordem_turnos = ["Manhã", "Tarde", "Noite"]

tabela = (df.pivot_table(index="turno", columns="dia_semana",
                         values="receita", aggfunc="sum")
            .reindex(index=ordem_turnos, columns=ordem_dias))

ax = sns.heatmap(tabela, annot=True, fmt=".0f", cmap="YlOrRd",
                 cbar_kws={"label": "Receita (R$)"})
ax.set_title("Receita por turno x dia da semana")
ax.set_xlabel("Dia da semana")
ax.set_ylabel("Turno")
plt.tight_layout()
plt.show()

print("Receita por turno:")
for t, v in df.groupby("turno")["receita"].sum().reindex(ordem_turnos).items():
    print(f"  {t:8s} {reais(v)}")
""")
md(r"""
**Leitura:** a **manhã** é disparado o turno mais forte — o pico clássico do café antes
do trabalho. Os dias de semana concentram o movimento, com leve queda no fim de semana.
O turno da noite é o mais fraco. Recomendação: garantir equipe e estoque completos no
pico da manhã e testar promoções à tarde/noite para suavizar a ociosidade.
""")

# ===========================================================================
# 5. SQL
# ===========================================================================
md(r"""
## 5. Consulta em SQL (sqlite3)

Para demonstrar domínio de SQL, carregamos o DataFrame em um banco **SQLite em memória**
e respondemos a uma pergunta com uma consulta: **o produto campeão de receita em cada
loja**, usando `GROUP BY`, agregação e uma *window function* (`RANK`).
""")
code(r"""
import sqlite3

con = sqlite3.connect(":memory:")
df.to_sql("vendas", con, index=False, if_exists="replace")

consulta = '''
WITH receita_produto AS (
    SELECT
        loja,
        produto,
        ROUND(SUM(quantidade * preco_unitario), 2) AS receita,
        RANK() OVER (
            PARTITION BY loja
            ORDER BY SUM(quantidade * preco_unitario) DESC
        ) AS posicao
    FROM vendas
    GROUP BY loja, produto
)
SELECT loja, produto, receita
FROM receita_produto
WHERE posicao = 1
ORDER BY receita DESC;
'''

top_por_loja = pd.read_sql_query(consulta, con)
con.close()
top_por_loja
""")
md(r"""
**Leitura:** a consulta revela o produto **líder de receita em cada unidade**. Bebidas
quentes de maior ticket (cappuccino/latte) tendem a aparecer no topo, confirmando via SQL
o que os gráficos mostraram: o mix de bebidas quentes é o motor de faturamento em todas
as praças.
""")

# ===========================================================================
# 6. CONCLUSÕES
# ===========================================================================
md(r"""
## 6. Conclusões e recomendações

Síntese acionável para a diretoria da CaféBR:

1. **Concentração geográfica.** São Paulo - Paulista e Rio de Janeiro - Ipanema puxam a
   receita. *Ação:* replicar as boas práticas dessas lojas nas unidades do Sul e avaliar
   investimento de marketing local em Curitiba e Porto Alegre.

2. **Sazonalidade de inverno é forte e previsível.** Junho–agosto são o pico graças às
   bebidas quentes. *Ação:* planejar estoque/escala para o inverno e lançar linha gelada
   promocional no verão para suavizar o vale.

3. **A manhã é o coração do negócio.** O pico matinal em dias úteis domina. *Ação:*
   garantir equipe completa das 7h às 11h e testar "happy hour do café" à tarde/noite
   para ocupar a capacidade ociosa.

4. **Canais digitais têm ticket maior.** App e delivery elevam o valor por pedido.
   *Ação:* incentivar combos e itens adicionais no app para aumentar ainda mais o ticket.

5. **Pix já rivaliza com o cartão.** *Ação:* estimular o Pix (ex.: mimo/desconto pontual)
   para reduzir custos de adquirência sem perder conversão.

---
*Análise reprodutível: `python gerar_dados.py` recria o CSV; o notebook roda de cima a
baixo sem dependências externas.*
""")

nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}

with open("analise.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("analise.ipynb criado com", len(cells), "células.")
