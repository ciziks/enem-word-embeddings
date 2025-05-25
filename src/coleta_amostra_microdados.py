import pandas as pd
import random

chunksize = 200_000  
reservoir = []
k = 100
n = 0
ano = 2009

codigos_prova = {
    "2009": 49,
    "2010": 89,
    "2011": 121,
    "2012": 141,
    "2013": 171,
    "2014": 199,
    "2015": 275,
    "2016": 291,
    "2017": 407,
    "2018": 463,
    "2019": 519,
    "2020": 604,
    "2021": 916,
    "2022": 1092,
    "2023": 1228,
}

# Coleta "parcelada" de dados, a fim de não estourar a memória devido ao tamanho do csv
for chunk in pd.read_csv(f'MICRODADOS_ENEM_{ano}.csv',
                         usecols=['CO_PROVA_CN', "TX_RESPOSTAS_CN"],
                         chunksize=chunksize,
                         encoding="ISO-8859-1", 
                         sep=";"):
    
    # Queremos amostras relativas a Ciências da Natureza em que as pessoas tenham respondido ao menos uma questão
    sub = chunk[
        (chunk.CO_PROVA_CN == codigos_prova[str(ano)]) &
        (chunk.TX_RESPOSTAS_CN.notna())
    ]

    # Primeiras 100 linhas são incluídas na amostra
    # Para garantir iguais chances, após as 100 primeiras, sorteamos um número entre 100 e o número da variável
    # O número sorteado é a posição dela - queremos apenas as 100 primeiras
    for _, row in sub.iterrows():
        n += 1
        if len(reservoir) < k:
            reservoir.append(row)
        else:
            s = random.randrange(n)
            if s < k:
                reservoir[s] = row

df_amostra = pd.DataFrame(reservoir)

# Para cada pessoa, há um vetor de 45 caracteres. Cada caractere é a resposta da questão de CN ordenada
resp_expanded = df_amostra['TX_RESPOSTAS_CN']\
    .apply(lambda s: pd.Series(list(s)))

# Converter a string de 45 caracteres para 45 colunas
resp_expanded.columns = [f'questao_{i+1}' for i in range(resp_expanded.shape[1])]
df_final = pd.concat([df_amostra.drop(columns=['TX_RESPOSTAS_CN']), resp_expanded], axis=1)

# Salvar
df_final.to_csv(f'amostra_microdados_respostas_{ano}.csv', sep=';', index=False, encoding='ISO-8859-1')