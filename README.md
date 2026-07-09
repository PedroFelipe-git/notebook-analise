# ☕ CaféBR — Análise Exploratória de Vendas (2024–2025)

Análise exploratória de dados (EDA) das vendas de uma rede fictícia de cafeterias, a
**CaféBR**, com 5 unidades em capitais brasileiras. O projeto vai do **dado bruto às
conclusões de negócio** usando o núcleo do dia a dia de um analista: **pandas**,
**SQL (sqlite3)**, **estatística descritiva** e **visualização** com matplotlib/seaborn.

> Projeto de portfólio. Todos os dados são **sintéticos** e gerados offline — não há
> downloads externos nem chaves de API. O notebook roda de cima a baixo sem erros.

---

## 🎯 Contexto e pergunta de negócio

A diretoria da CaféBR quer entender **onde, quando e como a rede vende mais** para
orientar decisões de estoque, escala de equipe, promoções e expansão. A análise responde:

1. Quais **lojas** e **produtos** mais faturam?
2. Como a **receita evolui mês a mês**? Há sazonalidade?
3. Qual o **ticket médio por canal** (balcão, app, delivery)?
4. Qual **forma de pagamento** domina?
5. Há diferença de vendas por **turno** e **dia da semana**?

## 📊 Principais achados

- **São Paulo - Paulista lidera o faturamento** (R$ 9.498,77), seguida por Rio de
  Janeiro - Ipanema (R$ 7.346,72). As unidades do Sul (Curitiba e Porto Alegre) fecham o
  ranking — candidatas a marketing local.
- **Sazonalidade de inverno é forte e previsível:** junho, julho e agosto são o pico de
  receita (topo do ano), impulsionados pelas bebidas quentes. O verão é o vale.
- **A manhã é o coração do negócio:** o turno matinal responde por ~55% da receita, com
  concentração em dias úteis. A noite é o turno mais fraco (~16%).
- **Canais digitais têm ticket médio maior:** delivery (R$ 20,29) e app (R$ 18,91)
  superam o balcão (R$ 14,67) — pedidos digitais agregam mais itens por compra.
- **Pix já rivaliza com o cartão:** cartão 49% e Pix 43% das transações, com dinheiro em
  queda (~7%) — oportunidade de incentivar o Pix e reduzir taxas de adquirência.

## 🗂️ Estrutura do projeto

```
notebook-analise/
├── analise.ipynb            # notebook de EDA (narrativa + código, já executado)
├── dados/
│   └── vendas_cafebr.csv     # ~2.000 linhas sintéticas de vendas (2024–2025)
├── gerar_dados.py            # script que gera o CSV (semente fixa, reprodutível)
├── construir_notebook.py     # script que monta o analise.ipynb
├── requirements.txt          # dependências
└── README.md
```

## 🧱 O que o notebook cobre

1. **Introdução** — pergunta de negócio e perguntas de análise.
2. **Carregamento e visão geral** — `head()`, `info()`, `describe()`, checagem de nulos e
   tipos.
3. **Limpeza e preparação** — tratamento de nulos e duplicatas; colunas derivadas
   (`receita = quantidade × preço`, `mês`, `dia da semana`, `turno`).
4. **Análise** — cada pergunta com **gráfico + parágrafo de leitura** (barras, linha de
   evolução, pizza e heatmap).
5. **SQL** — consulta em `sqlite3` a partir do DataFrame (CTE + *window function* `RANK`)
   para achar o produto campeão de cada loja.
6. **Conclusões e recomendações** — achados acionáveis para o negócio.

## 🚀 Como executar

Pré-requisito: Python 3.9+.

```bash
# 1. (opcional) crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. instale as dependências
pip install -r requirements.txt

# 3. (opcional) regenere o CSV sintético
python gerar_dados.py

# 4. abra o notebook
jupyter notebook analise.ipynb
```

O `dados/vendas_cafebr.csv` já vem incluído, então o notebook roda sem precisar gerar
nada. Para reexecutar tudo sem abrir a interface:

```bash
jupyter nbconvert --to notebook --execute --inplace analise.ipynb
```

## 🛠️ Tecnologias

`Python` · `pandas` · `NumPy` · `matplotlib` · `seaborn` · `SQL (sqlite3)` · `Jupyter`
