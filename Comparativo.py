import pandas as pd
from io import StringIO
from fuzzywuzzy import fuzz
import difflib

# Função para carregar e limpar os dados
def load_data(file_path):
    # Carrega os dados como texto primeiro
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Corrigir linhas mal formatadas (algumas têm campos ausentes)
    cleaned_lines = []
    for line in lines:
        parts = line.strip().split(',')
        if len(parts) == 5:
            cleaned_lines.append(','.join(parts))

    # Cabeçalho manualmente definido
    headers = ['Latitude', 'Longitude', 'Base', 'Nome', 'Localidade']

    # Usar StringIO para criar um DataFrame
    data_str = '\n'.join(cleaned_lines)
    df = pd.read_csv(StringIO(data_str), names=headers)

    # Converter Latitude e Longitude para float
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

    return df.dropna(subset=['Latitude', 'Longitude'])

# Função de comparação fuzzy + proximidade
def match_auvo_to_received(auvo_df, received_df, lat_threshold=0.2, lon_threshold=0.2, similarity_threshold=75):
    results = []

    for idx, row in auvo_df.iterrows():
        best_match = None
        best_score = 0

        for r_idx, r_row in received_df.iterrows():
            # Verifica proximidade geográfica
            lat_diff = abs(row['Latitude'] - r_row['Latitude'])
            lon_diff = abs(row['Longitude'] - r_row['Longitude'])

            if lat_diff <= lat_threshold and lon_diff <= lon_threshold:
                # Calcula similaridade de nomes
                name_similarity = fuzz.token_sort_ratio(row['Nome'].lower(), r_row['Nome'].lower())

                if name_similarity >= similarity_threshold and name_similarity > best_score:
                    best_score = name_similarity
                    best_match = {
                        'Auvo Nome': row['Nome'],
                        'Recebida Nome': r_row['Nome'],
                        'Latitude Auvo': row['Latitude'],
                        'Longitude Auvo': row['Longitude'],
                        'Localidade': row['Localidade'],
                        'Latitude Recebida': r_row['Latitude'],
                        'Longitude Recebida': r_row['Longitude'],
                        'Similaridade (%)': name_similarity
                    }

        if best_match:
            results.append(best_match)
        else:
            results.append({
                'Auvo Nome': row['Nome'],
                'Recebida Nome': None,
                'Latitude Auvo': row['Latitude'],
                'Longitude Auvo': row['Longitude'],
                'Localidade': row['Localidade'],
                'Latitude Recebida': None,
                'Longitude Recebida': None,
                'Similaridade (%)': None
            })

    return pd.DataFrame(results)

# Caminho do seu arquivo CSV
file_path = 'Mapa.csv'  # Substitua pelo caminho real do seu arquivo

# Carregar dados
df = load_data(file_path)

# Separar bases
auvo_df = df[df['Base'] == 'Auvo'].copy()
received_df = df[df['Base'] == 'Base Recebida'].copy()

# Comparar
match_df = match_auvo_to_received(auvo_df, received_df)

# Mostrar resultado
print(match_df[['Auvo Nome', 'Recebida Nome', 'Similaridade (%)']])
match_df.to_csv('resultado.csv', index=False)
