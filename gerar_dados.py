"""
Gerador de dados sintéticos de vendas da rede fictícia de cafeterias "CaféBR".

Produz ~2.000 linhas realistas cobrindo 2024-2025, com sazonalidade plausível
(mais vendas no inverno e pela manhã). Executar uma vez para (re)gerar o CSV:

    python gerar_dados.py

O resultado é salvo em dados/vendas_cafebr.csv. Semente fixa => reprodutível.
"""

import os
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
N_LINHAS = 2000

# ---------------------------------------------------------------------------
# Dimensões do negócio
# ---------------------------------------------------------------------------
LOJAS = {
    "São Paulo - Paulista": 0.30,
    "Rio de Janeiro - Ipanema": 0.22,
    "Belo Horizonte - Savassi": 0.18,
    "Curitiba - Batel": 0.16,
    "Porto Alegre - Moinhos": 0.14,
}

# produto -> (categoria, preço base em R$)
PRODUTOS = {
    "Café Expresso": ("Bebida Quente", 6.00),
    "Café Coado": ("Bebida Quente", 5.00),
    "Cappuccino": ("Bebida Quente", 11.00),
    "Latte": ("Bebida Quente", 12.00),
    "Chocolate Quente": ("Bebida Quente", 13.00),
    "Café Gelado": ("Bebida Gelada", 12.50),
    "Suco Natural": ("Bebida Gelada", 10.00),
    "Bolo de Cenoura": ("Comida", 9.50),
    "Bolo de Chocolate": ("Comida", 10.50),
    "Pão de Queijo": ("Comida", 7.00),
    "Sanduíche Natural": ("Comida", 16.00),
    "Croissant": ("Comida", 12.00),
}

PAGAMENTOS = {"Pix": 0.42, "Cartão": 0.45, "Dinheiro": 0.13}
CANAIS = {"Balcão": 0.55, "App": 0.28, "Delivery": 0.17}

# Bebidas quentes vendem MAIS no inverno (jun-ago no hemisfério sul).
# Fator multiplicativo de "peso" por mês para bebidas quentes.
FATOR_INVERNO = {
    1: 0.70, 2: 0.70, 3: 0.85, 4: 1.05, 5: 1.30, 6: 1.55,
    7: 1.65, 8: 1.50, 9: 1.15, 10: 0.95, 11: 0.85, 12: 0.75,
}

# Volume de MOVIMENTO por mês (nº de transações): também sobe no inverno, pois a
# rede vende mais no frio. Usado para ponderar o sorteio das datas.
FATOR_VOLUME = {
    1: 0.75, 2: 0.75, 3: 0.90, 4: 1.00, 5: 1.20, 6: 1.45,
    7: 1.55, 8: 1.40, 9: 1.05, 10: 0.95, 11: 0.85, 12: 0.80,
}

# Cesta média por canal: pedidos digitais (App/Delivery) costumam agregar mais
# itens que o balcão -> ticket médio maior. Probabilidades de quantidade 1..4.
CESTA_CANAL = {
    "Balcão":   [0.68, 0.24, 0.06, 0.02],
    "App":      [0.45, 0.34, 0.15, 0.06],
    "Delivery": [0.38, 0.34, 0.19, 0.09],
}


def escolher(mapa):
    """Sorteia uma chave de um dict {valor: probabilidade}."""
    chaves = list(mapa.keys())
    probs = np.array(list(mapa.values()), dtype=float)
    probs = probs / probs.sum()
    return RNG.choice(chaves, p=probs)


def gerar_turno_hora():
    """Retorna (hora) com forte concentração pela manhã."""
    # manhã 55%, tarde 30%, noite 15%
    faixa = RNG.choice(["manha", "tarde", "noite"], p=[0.55, 0.30, 0.15])
    if faixa == "manha":
        return int(RNG.integers(7, 12))      # 07h-11h
    if faixa == "tarde":
        return int(RNG.integers(12, 18))     # 12h-17h
    return int(RNG.integers(18, 22))         # 18h-21h


def gerar():
    datas_base = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    # Peso de cada dia proporcional ao volume do seu mês -> mais vendas no inverno
    peso_dia = np.array([FATOR_VOLUME[pd.Timestamp(d).month] for d in datas_base])
    peso_dia = peso_dia / peso_dia.sum()
    linhas = []

    for _ in range(N_LINHAS):
        data = pd.Timestamp(RNG.choice(datas_base.values, p=peso_dia))
        mes = data.month
        hora = gerar_turno_hora()

        # Escolha de produto ponderada pela sazonalidade (bebida quente x inverno)
        nomes = list(PRODUTOS.keys())
        pesos = []
        for nome in nomes:
            categoria = PRODUTOS[nome][0]
            peso = 1.0
            if categoria == "Bebida Quente":
                peso *= FATOR_INVERNO[mes]
                if hora < 12:            # bebida quente ainda mais forte de manhã
                    peso *= 1.4
            elif categoria == "Bebida Gelada":
                peso *= (2.0 - FATOR_INVERNO[mes])   # inverso do inverno
            pesos.append(peso)
        pesos = np.array(pesos)
        pesos = pesos / pesos.sum()
        produto = RNG.choice(nomes, p=pesos)
        categoria, preco_base = PRODUTOS[produto]

        # Preço com pequena variação (+/- 8%) e arredondado a centavos "de menu"
        preco = round(preco_base * RNG.uniform(0.95, 1.08), 2)

        loja = escolher(LOJAS)
        pagamento = escolher(PAGAMENTOS)
        canal = escolher(CANAIS)

        # Quantidade depende do canal: cesta digital maior que a de balcão
        quantidade = int(RNG.choice([1, 2, 3, 4], p=CESTA_CANAL[canal]))

        # Delivery e App tendem a Pix/Cartão (quase nunca dinheiro)
        if canal in ("App", "Delivery") and pagamento == "Dinheiro":
            pagamento = escolher({"Pix": 0.5, "Cartão": 0.5})

        linhas.append({
            "data": data.strftime("%Y-%m-%d") + f" {hora:02d}:{int(RNG.integers(0,60)):02d}",
            "loja": loja,
            "produto": produto,
            "categoria": categoria,
            "quantidade": quantidade,
            "preco_unitario": preco,
            "forma_pagamento": pagamento,
            "canal": canal,
        })

    df = pd.DataFrame(linhas)

    # ------------------------------------------------------------------
    # Injetar "sujeira" realista para o notebook exercitar a limpeza:
    #  - alguns nulos em forma_pagamento
    #  - algumas linhas duplicadas
    # ------------------------------------------------------------------
    idx_nulos = RNG.choice(df.index, size=25, replace=False)
    df.loc[idx_nulos, "forma_pagamento"] = np.nan

    dup = df.sample(15, random_state=7)
    df = pd.concat([df, dup], ignore_index=True)

    df = df.sample(frac=1, random_state=1).reset_index(drop=True)
    return df


if __name__ == "__main__":
    os.makedirs("dados", exist_ok=True)
    df = gerar()
    caminho = os.path.join("dados", "vendas_cafebr.csv")
    df.to_csv(caminho, index=False, encoding="utf-8")
    print(f"Gerado: {caminho}")
    print(f"Linhas: {len(df)}  |  Colunas: {list(df.columns)}")
    print(df.head())
