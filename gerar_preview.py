"""
Gera a imagem de preview (hero) usada no topo do README a partir do CSV.
Cria um painel com os dois achados de maior impacto: sazonalidade de inverno
e ranking de lojas. Rodar: python gerar_preview.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

sns.set_theme(style="whitegrid", palette="deep")

df = pd.read_csv("dados/vendas_cafebr.csv").drop_duplicates()
df["forma_pagamento"] = df["forma_pagamento"].fillna(df["forma_pagamento"].mode()[0])
df["data"] = pd.to_datetime(df["data"])
df["receita"] = df["quantidade"] * df["preco_unitario"]
df["mes"] = df["data"].dt.to_period("M").astype(str)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# --- Evolução mensal (sazonalidade de inverno) ---
receita_mes = df.groupby("mes")["receita"].sum()
receita_mes.plot(marker="o", color="#C44E52", ax=ax1)
ax1.set_title("Receita mensal — pico no inverno (jun–ago)", fontweight="bold")
ax1.set_xlabel("Mês")
ax1.set_ylabel("Receita (R$)")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1000:.1f}k"))
ax1.tick_params(axis="x", rotation=45)

# --- Receita por loja ---
receita_loja = df.groupby("loja")["receita"].sum().sort_values()
ax2.barh(receita_loja.index, receita_loja.values, color="#4C72B0")
ax2.set_title("Receita por loja", fontweight="bold")
ax2.set_xlabel("Receita (R$)")
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1000:.0f}k"))

fig.suptitle("CaféBR — Análise de Vendas (2024–2025)",
             fontsize=15, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.96))

os.makedirs("imagens", exist_ok=True)
caminho = os.path.join("imagens", "preview.png")
fig.savefig(caminho, dpi=120, bbox_inches="tight")
print("Salvo:", caminho)
