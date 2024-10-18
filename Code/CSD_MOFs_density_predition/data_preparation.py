import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()
mysql_path = os.getenv("SQL_URL")
import sys
version = sys.argv[1]

DATABASE_URI = f'{mysql_path}/synthethis_condition_{version}'
engine = create_engine(DATABASE_URI)

mof_list = pd.read_csv(f'{version}/subset.txt', header=None, names=['mof_identifier'])
fingerprint = pd.read_csv(f'{version}/fingerprint.csv', encoding='utf-8')
metal_source = pd.read_sql_table('MOF_MetalSource_merge', engine)
organic_linker = pd.read_sql_table('MOF_OrganicLinker_merge', engine)
solvent = pd.read_sql_table('MOF_Solvent_merge', engine)
synthesis_conditions = pd.read_sql_table('MOF', engine)
performance = pd.read_csv('only_one_mof.csv', encoding='utf-8')
performance = performance[['identifier', 'pld', 'lcd', 'gcd', 'density', 'unitcell_volume']]
performance.columns = ['mof_identifier', 'pld', 'lcd', 'gcd', 'density', 'unitcell_volume']

synthesis_conditions = synthesis_conditions[['identifier', 'active_time_value', 'active_temperature_value', 'reaction_time_value', 'reaction_temperature_value']]
synthesis_conditions.columns = ['mof_identifier', 'active_time_value', 'active_temperature_value', 'reaction_time_value', 'reaction_temperature_value']

MetalSource_embedding = fingerprint[fingerprint['type'] == 'MetalSource']
OrganicLinker_embedding = fingerprint[fingerprint['type'] == 'OrganicLinker']
Solvent_embedding = fingerprint[fingerprint['type'] == 'Solvent']

MetalSource_embedding = MetalSource_embedding.drop(columns=['cnt', 'formula', 'smiles', 'type'])
OrganicLinker_embedding = OrganicLinker_embedding.drop(columns=['cnt', 'formula', 'smiles', 'type'])
Solvent_embedding = Solvent_embedding.drop(columns=['cnt', 'formula', 'smiles', 'type'])
fingerprint = fingerprint.drop(columns=['cnt', 'formula', 'smiles', 'type'])

MetalSource_features = pd.read_csv(f'{version}/MetalSource_features.csv')
MetalSource_features = MetalSource_features.drop(columns=['cnt', 'formula', 'smiles'])
MetalSource_features2 = pd.read_csv(f'{version}/metal.csv')
MetalSource_features2 = MetalSource_features2.drop(columns=['cnt', 'formula', 'smiles', 'metal'])
MetalSource_features = MetalSource_features.merge(MetalSource_features2, 
                                                    on='precursor_name', how='left')
# convert to float
cols = MetalSource_features.columns
cols = cols.drop('precursor_name')
MetalSource_features[cols] = MetalSource_features[cols].apply(pd.to_numeric, errors='coerce')
MetalSource_embedding = MetalSource_embedding.merge(MetalSource_features, 
                                                    on='precursor_name', how='left')

print('------------------MetalSource_embedding', MetalSource_embedding.shape)
print(MetalSource_embedding.describe())
print(MetalSource_embedding)
print('------------------OrganicLinker_embedding', OrganicLinker_embedding.shape)
print(OrganicLinker_embedding.describe())
print(OrganicLinker_embedding)
print('------------------Solvent_embedding', Solvent_embedding.shape)
print(Solvent_embedding.describe())
print(Solvent_embedding)

def calculate_ratios(metal_df, organic_df, solvent_df):
    metal_amounts = metal_df.groupby('mof_identifier')['amount_value'].sum().reset_index()
    organic_amounts = organic_df.groupby('mof_identifier')['amount_value'].sum().reset_index()
    solvent_amounts = solvent_df.groupby('mof_identifier')['amount_value'].sum().reset_index()
    
    metal_amounts = metal_amounts.replace(0, np.nan)
    organic_amounts = organic_amounts.replace(0, np.nan)
    solvent_amounts = solvent_amounts.replace(0, np.nan)
    
    metal_amounts = round(metal_amounts, 2)
    organic_amounts = round(organic_amounts, 2)
    solvent_amounts = round(solvent_amounts, 2)
    
    ratios = metal_amounts.merge(organic_amounts, on='mof_identifier', suffixes=('_metal', '_organic'))
    ratios = ratios.merge(solvent_amounts, on='mof_identifier')
    ratios.columns = ['mof_identifier', 'metal_amount', 'organic_amount', 'solvent_amount']
    
    ratios['metal_organic_ratio'] = np.where((ratios['metal_amount'].isnull()) | (ratios['organic_amount'].isnull()), np.nan, round(ratios['metal_amount'] / ratios['organic_amount'], 2))
    ratios['metal_solvent_ratio'] = np.where((ratios['metal_amount'].isnull()) | (ratios['solvent_amount'].isnull()), np.nan, round(ratios['metal_amount'] / ratios['solvent_amount'], 2))
    ratios['organic_solvent_ratio'] = np.where((ratios['organic_amount'].isnull()) | (ratios['solvent_amount'].isnull()), np.nan, round(ratios['organic_amount'] / ratios['solvent_amount'], 2))

    print(f"------------------Ratios shape: {ratios.shape}")
    print(ratios.describe())
    print(ratios)
    return ratios

def aggregate_features(df, embedding_df, weight_col):
    avg_amounts = df.groupby('precursor_name')[weight_col].mean().reset_index()
    avg_amounts.columns = ['precursor_name', 'avg_amount']
    df = df.merge(avg_amounts, on='precursor_name')
    df['standardized_amount'] = df[weight_col] / df['avg_amount']
    df_merged = df.merge(embedding_df, on='precursor_name')

    idx_max_amount = df_merged.groupby('mof_identifier')[weight_col].idxmax()
    idx_max_amount = idx_max_amount.dropna()
    max_amount_embedding = df_merged.loc[idx_max_amount, ['mof_identifier'] + list(embedding_df.columns)].set_index('mof_identifier')

    aggregated_features = max_amount_embedding
    
    # Make Index a column
    aggregated_features.reset_index(inplace=True)
    aggregated_features.drop(columns=['precursor_name'], inplace=True)
    return aggregated_features

metal_agg = aggregate_features(metal_source, MetalSource_embedding, 'amount_value')
organic_agg = aggregate_features(organic_linker, OrganicLinker_embedding, 'amount_value')
solvent_agg = aggregate_features(solvent, Solvent_embedding, 'amount_value')


ratios = calculate_ratios(metal_source, organic_linker, solvent)


merged_features = mof_list.merge(ratios, on='mof_identifier', how='left')\
                          .merge(metal_agg, on='mof_identifier', how='left')\
                          .merge(organic_agg, on='mof_identifier', how='left')\
                          .merge(solvent_agg, on='mof_identifier', how='left')\
                          .merge(synthesis_conditions, on='mof_identifier', how='left')\
                          .merge(performance, on='mof_identifier', how='left')                          


merged_features.to_csv(f'{version}/merged_features.csv', index=False, encoding='utf-8')

print(f"Final merged features shape: {merged_features.shape}")
print(merged_features.describe())
print(merged_features)
