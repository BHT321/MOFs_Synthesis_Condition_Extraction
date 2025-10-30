import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import sys
import os
from dotenv import load_dotenv
load_dotenv()
mysql_path = os.getenv("SQL_URL")

version = sys.argv[1]
merge_version = "merge1"
table_suffix = f"_{merge_version}" if merge_version != "" else ""
subset_and_fingerprint_dir = "subset_and_fingerprint"

DATABASE_URI = f'{mysql_path}/synthethis_condition_{version}'
engine = create_engine(DATABASE_URI)
ssa_data = pd.read_csv(f'txt_SSA.csv', encoding='utf-8')
metal_source = pd.read_sql_table(f'MOF_MetalSource{table_suffix}', engine)
organic_linker = pd.read_sql_table(f'MOF_OrganicLinker{table_suffix}', engine)
solvent = pd.read_sql_table(f'MOF_Solvent{table_suffix}', engine)
modulator = pd.read_sql_table(f'MOF_Modulator{table_suffix}', engine)
fingerprint = pd.read_csv(f"{subset_and_fingerprint_dir}/fingerprint.csv", encoding='utf-8')
synthesis_conditions = pd.read_sql_table('MOF', engine)
synthesis_conditions = synthesis_conditions[["identifier", "reaction_time_value", "reaction_temperature_value"]]
synthesis_conditions.columns = ["mof_identifier", "reaction_time_value", "reaction_temperature_value"]
mof_list = pd.read_csv(f'{subset_and_fingerprint_dir}/subset.txt', header=None, names=['mof_identifier'], encoding='utf-8')
# mof_list = synthesis_conditions[["mof_identifier"]]

def filtered_only_one_precursor_mof(df:pd.DataFrame):
    unique_names = set()
    def select_unique_mof_id(group: pd.DataFrame):
        if len(set(group["precursor_name"])) == 1:
            unique_names.add(group["mof_identifier"].iloc[0])
    df.groupby("mof_identifier").apply(select_unique_mof_id)
    return unique_names

def drop_rare_precursors(df:pd.DataFrame, precursor_dict:dict):
    df = df[df["precursor_name"].isin(precursor_dict.keys())]
    df["precursor_name"] = df["precursor_name"].replace(precursor_dict)
    return df

def get_max_n_amount_data(df:pd.DataFrame, precursor_type, top_n=2):
    # Ensure the amount column is numeric before merging
    df["amount_value"] = pd.to_numeric(df["amount_value"], errors='coerce')
    
    def get_top_n(group:pd.DataFrame):
        sorted_group = group.sort_values(by="amount_value", ascending=False)
        top_result = sorted_group.head(top_n)
        
        while len(top_result) < top_n:
            top_result = pd.concat(
                [top_result, 
                 pd.DataFrame([[None, None, None]], columns=["mof_identifier", "precursor_name", "amount_value"])
                ])
    
        result = []
        for i in range(top_n):
            result.append(top_result.iloc[i]["precursor_name"])
            result.append(top_result.iloc[i]["amount_value"])
        return pd.Series(result)
    
    max_n_amount_data:pd.DataFrame = df.groupby('mof_identifier', as_index=False).apply(get_top_n).reset_index()
    max_n_amount_data = max_n_amount_data.drop(columns=["index"])

    columns = ["mof_identifier"]
    for i in range(top_n):
        columns.append(f"{precursor_type}_name{i}")
        columns.append(f"{precursor_type}_amount{i}")
    max_n_amount_data.columns = columns
    
    return max_n_amount_data

def get_amount_data_of_selected_precursors(df: pd.DataFrame, precursor_type, precursor_names):
    def get_amount_data(group: pd.DataFrame):
        amounts = []
        for precursor in precursor_names:
            df_subset = group[group["precursor_name"]==precursor]
            if len(df_subset) == 0:
                amounts.append(0)
            else:
                amount = df_subset["amount_value"].sum()
                if amount == 0:
                    amounts.append(-1)
                else:
                    amounts.append(amount)
        return pd.Series(amounts)

    amount_data:pd.DataFrame = df.groupby('mof_identifier', as_index=False).apply(get_amount_data).reset_index()
    amount_data = amount_data.drop(columns=["index"])
    amount_data.columns = ["mof_identifier"] + [f"{precursor_type}_{precursor_names[i]}_amount" for i in range(len(precursor_names))]
    return amount_data

# the valid mof should only have one precursor name of MetalSource, OrganicLinker and Solvent
valid_metal_mofs = set(filtered_only_one_precursor_mof(metal_source))
valid_organic_mofs = set(filtered_only_one_precursor_mof(organic_linker))
valid_solvent_mofs = set(filtered_only_one_precursor_mof(solvent))

# get the data from each group
metal_agg = get_amount_data_of_selected_precursors(
    metal_source, "MetalSource", list(fingerprint[fingerprint["type"]=="MetalSource"]["precursor_name"])
)
organic_agg = get_amount_data_of_selected_precursors(
    organic_linker, "OrganicLinker", list(fingerprint[fingerprint["type"]=="OrganicLinker"]["precursor_name"])
)
solvent_agg = get_amount_data_of_selected_precursors(
    solvent, "Solvent", list(fingerprint[fingerprint["type"]=="Solvent"]["precursor_name"])
)
modulator_agg = get_amount_data_of_selected_precursors(
    modulator, "Modulator", list(fingerprint[fingerprint["type"]=="Modulator"]["precursor_name"])
)

# select the ssa and mofs
ssa_data["mof_identifier"] = ssa_data.apply(lambda row:row["txt"][:-4], axis=1)
ssa_data = ssa_data.drop(columns=["txt"])
valid_identifiers = valid_metal_mofs & valid_organic_mofs & valid_solvent_mofs
mof_list = mof_list[mof_list["mof_identifier"].isin(valid_identifiers)]

# combine the generated data
features = mof_list.merge(metal_agg, on='mof_identifier', how='left')\
    .merge(organic_agg, on='mof_identifier', how='left')\
    .merge(solvent_agg, on='mof_identifier', how='left')\
    .merge(modulator_agg, on='mof_identifier', how='left')\
    .merge(synthesis_conditions, on='mof_identifier', how='left')\
    .merge(ssa_data, on="mof_identifier", how="left")

# name_columns = [column for column in features.columns if "_name" in column]
# features[name_columns] = features[name_columns].fillna(-1)
# features[name_columns] = features[name_columns].astype(int)
amount_columns = [column for column in features.columns if "_amount" in column]
features[amount_columns] = features[amount_columns].fillna(0)

# precursor_df = pd.concat([metal_top_df, organic_top_df, solvent_top_df, modulator_top_df])
features.to_csv(f"{version}/merged_features.csv", index=False)
