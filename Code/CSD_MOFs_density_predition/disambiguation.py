import pandas as pd
from sqlalchemy import create_engine
from fuzzywuzzy import fuzz
from itertools import combinations
from multiprocessing import Pool, cpu_count
import json
import os
from dotenv import load_dotenv
load_dotenv()
mysql_path = os.getenv("SQL_URL")
import sys

version = sys.argv[1]
DATABASE_URI = f'{mysql_path}/synthethis_condition_{version}?charset=utf8mb4'
engine = create_engine(DATABASE_URI)

tables = ['MOF_MetalSource', 'MOF_Modulator', 'MOF_OrganicLinker', 'MOF_Solvent']

unique_precursors = {}

for table in tables:
    df = pd.read_sql_table(table, engine)
    unique_precursors[table] = df['precursor_name'].unique()

metal_atoms = [
    "Li", "Be", "Na", "Mg", "Al", "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", 
    "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Cs", "Ba", "La", "Ce", "Pr",
    "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt",
    "Au", "Hg", "Tl", "Pb", "Bi", "Po", "Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es",
    "Fm", "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og"
]

def extract_metal_atom(name):
    for atom in metal_atoms:
        if name.find(atom) != -1:
            return atom
    return ''

def calculate_similarity(pair):
    name1, name2 = pair
    return (name1, name2, fuzz.ratio(name1, name2))

def find_similar_names(precursor_list, threshold=90):
    pairs = list(combinations(precursor_list, 2))
    similar_names = []

    with Pool(cpu_count()) as pool:
        results = pool.map(calculate_similarity, pairs)
        
    similarity_map = {}
    name_groups = []
    
    for name1, name2, similarity in results:
        key = f"{name1}; {name2}"
        similarity_map[key] = similarity
        
        if similarity >= threshold:
            atom1 = extract_metal_atom(name1)
            atom2 = extract_metal_atom(name2)
            if atom1 and atom1 == atom2:
                added = False
                for group in name_groups:
                    if name1 in group['words'] or name2 in group['words']:
                        group['words'].update([name1, name2])
                        group['similarity'].append(similarity)
                        group['count'] += 1
                        group['name'] = min(group['words'], key=len)
                        group['similarity'] = [similarity_map.get(f"{group['name']}; {word}", fuzz.ratio(group['name'], word)) for word in group['words']]
                        added = True
                        break
                if not added:
                    name_groups.append({
                        'name': min([name1, name2], key=len),
                        'count': 2,
                        'similarity': [similarity],
                        'words': set([name1, name2]),
                        'atom': atom1
                    })

    for group in name_groups:
        group['words'] = list(group['words'])
        group['name'] = min(group['words'], key=len)
        group['similarity'] = [similarity_map.get(f"{group['name']}; {word}", fuzz.ratio(group['name'], word)) for word in group['words']]
        group['atom'] = extract_metal_atom(group['name'])

    return similarity_map, name_groups

all_similarity_maps = {}
all_name_groups = {}
all_matched_words = {}

for table, precursors in unique_precursors.items():
    print(f"Processing table: {table}")
    similarity_map, name_groups = find_similar_names(precursors, threshold=90)
    all_similarity_maps[table] = similarity_map
    all_name_groups[table] = name_groups
    matched_words = [sorted(group['words']) for group in name_groups]
    all_matched_words[table] = sorted(matched_words)

for table, sim_map in all_similarity_maps.items():
    all_similarity_maps[table] = dict(sorted(sim_map.items(), key=lambda item: item[1], reverse=True))

# with open(f'{version}/similarity_map.json', 'w') as f:
#     json.dump(all_similarity_maps, f, indent=4)

# with open(f'{version}/name_groups.json', 'w') as f:
#     json.dump(all_name_groups, f, indent=4)

with open(f'{version}/disambiguation.json', 'w') as f:
    json.dump(all_matched_words, f, indent=4)

print("Processing completed and results saved to JSON files.")
