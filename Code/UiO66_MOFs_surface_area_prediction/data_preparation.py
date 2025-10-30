import pandas as pd
import numpy as np
import pandas as pd
import numpy as np
import itertools

def remove_error_data(df:pd.DataFrame, threshold=1e-5):
    df_origin = df
    df = df_origin.copy()
    def similar(data1, data2):
        if data1 == 0:
            return abs(data2) <= threshold
        return abs(data1 - data2) / abs(data1) <= threshold
    error_rows = set()
    valid_columns = list(df.columns)
    valid_columns.remove("SSA")
    valid_columns.remove("synthesis_method")
    valid_columns.remove("mof_identifier")
    for (i, j) in itertools.combinations(range(len(df)), 2):
        row1, row2 = df.iloc[i], df.iloc[j]
        is_similar_row = True
        for column in valid_columns:
            if not similar(row1[column], row2[column]):
                is_similar_row = False
                break
        if is_similar_row and not similar(row1["SSA"], row2["SSA"]):
            error_rows.add(i)
            error_rows.add(j)
    df = df_origin.drop(index=list(error_rows))
    return df

            

def get_input_data3(df:pd.DataFrame, y_min=None, y_max=None, log=True, save_path=None):
    # Define properties dictionary
    # if "SSA" in df.columns:
    #     df = remove_error_data(df)
    acid_properties = {
        'HAc': {
            'pKa': 4.76,
            'molecular_weight': 60.05,
            'density': 1.05,  # g/cm³
        },
        'HCl': {
            'pKa': -6.3,
            'molecular_weight': 36.46,
            'density': 1.19,  # g/cm³ for 37% HCl solution
        },
        'BA': {
            'pKa': 4.20,
            'molecular_weight': 122.12,
            'density': 1.25,  # g/cm³
        },
        'formic acid': {
            'pKa': 3.75,
            'molecular_weight': 46.03,
            'density': 1.22,  # g/cm³
        },
        'H2O': {
            'pKa': 15.7,  # neutral water, used as a reference
            'molecular_weight': 18.02,
            'density': 1.00,  # g/cm³
        },
        'PVP': {
            'pKa': 9999,
            'molecular_weight': 40000,  # Typical molecular weight for PVP K30 grade
            'density': 1.2,  # g/cm³ (approximate for polymer)
        }
    }

    # Initialize new columns with NaN for numeric features and None for categorical
    numeric_features = ['pKa', 'molecular_weight', 'density']
    categorical_features = []

    for feature in numeric_features:
        df[feature] = np.nan

    for feature in categorical_features:
        df[feature] = None

    # Insert feature data
    for feature in numeric_features + categorical_features:
        remaining_mask = pd.Series(True, index=df.index)
        if log:
            print("Insert feature:", feature)
        mask_hac = (df['Modulator_HAc_amount'] != 0) & remaining_mask
        df.loc[mask_hac, feature] = acid_properties['HAc'][feature]
        remaining_mask = remaining_mask & ~mask_hac

        mask_hcl = (df['Modulator_HCl_amount'] != 0) & remaining_mask
        df.loc[mask_hcl, feature] = acid_properties['HCl'][feature]
        remaining_mask = remaining_mask & ~mask_hcl

        mask_ba = (df['Modulator_BA_amount'] != 0) & remaining_mask
        df.loc[mask_ba, feature] = acid_properties['BA'][feature]
        remaining_mask = remaining_mask & ~mask_ba

        mask_h2o = (df['Modulator_H2O_amount'] != 0) & remaining_mask
        df.loc[mask_h2o, feature] = acid_properties['H2O'][feature]
        remaining_mask = remaining_mask & ~mask_h2o

        mask_formic_acid = (df['Modulator_formic acid_amount'] != 0) & remaining_mask
        df.loc[mask_formic_acid, feature] = acid_properties['formic acid'][feature]
        remaining_mask = remaining_mask & ~mask_formic_acid

        mask_pvp = (df['Modulator_PVP_amount'] != 0) & remaining_mask
        df.loc[mask_pvp, feature] = acid_properties['PVP'][feature]
        remaining_mask = remaining_mask & ~mask_pvp
    if log:
        print("Insert Modulator feature data")

    # Define metal properties dictionary with numerical parameters
    metal_properties = {
        'ZrCl4': {
            'molar_mass': 233.04,  # in g/mol
            'density': 2.8,  # in g/cm³, solid at room temperature
        },
        'ZrOCl2·8H2O': {
            'molar_mass': 322.24,  # in g/mol
            'density': 1.91,  # in g/cm³, typically as a hydrate solid
        },
        'zirconium propoxide': {
            'molar_mass': 383.36,  # in g/mol
            'density': 1.05,  # in g/cm³, usually a liquid
        },
        'zirconyl nitrate hydrate': {
            'molar_mass': 339.24,  # in g/mol
            'density': 2.23,  # in g/cm³, solid
        }
    }

    # Initialize new columns for metal properties
    df['metal_molecular_weight'] = np.nan
    df['metal_density'] = None

    # Insert metal property data into the DataFrame
    remaining_mask = pd.Series(True, index=df.index)
    
    mask_zrcl4 = (df['MetalSource_ZrCl4_amount'] != 0) & remaining_mask
    df.loc[mask_zrcl4, 'metal_molecular_weight'] = metal_properties['ZrCl4']['molar_mass']
    df.loc[mask_zrcl4, 'metal_density'] = metal_properties['ZrCl4']['density']
    remaining_mask = remaining_mask & ~mask_zrcl4

    mask_zrocl2 = (df['MetalSource_ZrOCl2·8H2O_amount'] != 0) & remaining_mask
    df.loc[mask_zrocl2, 'metal_molecular_weight'] = metal_properties['ZrOCl2·8H2O']['molar_mass']
    df.loc[mask_zrocl2, 'metal_density'] = metal_properties['ZrOCl2·8H2O']['density']
    remaining_mask = remaining_mask & ~mask_zrocl2

    # mask_zirconium_propoxide = (df['MetalSource_zirconium propoxide_amount'] != 0) & remaining_mask
    # df.loc[mask_zirconium_propoxide, 'metal_molecular_weight'] = metal_properties['zirconium propoxide']['molar_mass']
    # df.loc[mask_zirconium_propoxide, 'metal_density'] = metal_properties['zirconium propoxide']['density']
    # remaining_mask = remaining_mask & ~mask_zirconium_propoxide

    # mask_zirconyl_nitrate = (df['MetalSource_zirconyl nitrate hydrate_amount'] != 0) & remaining_mask
    # df.loc[mask_zirconyl_nitrate, 'metal_molecular_weight'] = metal_properties['zirconyl nitrate hydrate']['molar_mass']
    # df.loc[mask_zirconyl_nitrate, 'metal_density'] = metal_properties['zirconyl nitrate hydrate']['density']
    # remaining_mask = remaining_mask & ~mask_zirconyl_nitrate
    if log:
        print("Insert MetalSource feature data")



    df['metal_amount0'] = df['MetalSource_ZrOCl2·8H2O_amount'] + df['MetalSource_ZrCl4_amount']\
        # +df['MetalSource_zirconium propoxide_amount'] + df['MetalSource_zirconyl nitrate hydrate_amount']

    df = df[(df['metal_amount0'] > 0) & (df['OrganicLinker_H2BDC_amount'] > 0) & (df['Solvent_DMF_amount'] > 0)]

    # 计算 metal_ratio 并处理负数
    # 计算 metal_ratio 并处理负数
    def deal_div(df, column1, column2, result_column):
        all_mask = pd.Series(True, index=df.index)
        valid_mask = ((df[column1]>=0) & (df[column2]>0))
        invalid_mask = all_mask & (~valid_mask)
        df.loc[valid_mask, result_column] = df.loc[valid_mask, column1] / df.loc[valid_mask, column2]
        df.loc[invalid_mask, result_column] = np.nan
        
    deal_div(df, 'metal_amount0', 'Solvent_DMF_amount', 'metal_ratio')
    deal_div(df, 'OrganicLinker_H2BDC_amount', 'Solvent_DMF_amount', 'organic_ratio')
    deal_div(df, 'metal_amount0', 'OrganicLinker_H2BDC_amount', 'metal_organic_ratio')
    modulator_sum = df[['Modulator_BA_amount', 'Modulator_HCl_amount', 'Modulator_HAc_amount',
                    'Modulator_H2O_amount', 'Modulator_formic acid_amount', 'Modulator_PVP_amount']].sum(axis=1)

    df['metal_mud_ratio'] = np.where(df['metal_amount0'] != 0, modulator_sum / df['metal_amount0'], 0)
    df['metal_mud_ratio'] = df['metal_mud_ratio'].apply(lambda x: x if x >= 0 else np.nan)

    df['sol_mud_ratio'] = np.where(df['Solvent_DMF_amount'] != 0, modulator_sum / df['Solvent_DMF_amount'], 0)
    df['sol_mud_ratio'] = df['sol_mud_ratio'].apply(lambda x: x if x >= 0 else np.nan)
    if log:
        print("Insert ratio data")
    
    if y_min and y_max:
        df = df[(df['SSA'] >= y_min) & (df['SSA'] <= y_max)]
    df = df[(df['metal_density'].isin([None, 2.8, 1.91])) & (df['pKa'] != 9999) & (df['pKa'] != 15.7)]
    # df = df[(df['classification'].isin([0,1]))]

    df = df.drop(
        columns=['MetalSource_ZrOCl2·8H2O_amount', 'MetalSource_ZrCl4_amount', 
                #  'MetalSource_zirconium propoxide_amount', 'MetalSource_zirconyl nitrate hydrate_amount', 
                 'Modulator_BA_amount', 'Modulator_HCl_amount',
                'Modulator_HAc_amount', 'Modulator_H2O_amount', 'Modulator_formic acid_amount', 'Modulator_PVP_amount'])
    df = df.drop(columns=['synthesis_method'])
    data = df
    data['classification'].fillna('missing', inplace=True)
    data = pd.get_dummies(data, columns=['classification'], drop_first=False)
    wrong_column_names = ["classification_0", "classification_1", "classification_2"]
    for wrong_column_name in wrong_column_names:
        if wrong_column_name in data.columns:
            data = data.rename(columns={wrong_column_name:wrong_column_name+".0"})
    necessary_column_names = ["classification_0.0", "classification_1.0", "classification_2.0", "classification_missing"]
    for column_name in necessary_column_names:
        if column_name not in data.columns:
            data[column_name] = 0

    if save_path:
        data.to_csv(save_path, index=None)
    if log:
        print(data.shape)
    processed_data = data.copy()
    del data
    return processed_data

if __name__ == "__main__":
    import sys
    version = sys.argv[1]
    df = pd.read_csv(f"{version}/merged_data.csv")
    df = get_input_data3(df, 700, 1700)
    df.to_csv(f"{version}/model_input.csv", index=None)