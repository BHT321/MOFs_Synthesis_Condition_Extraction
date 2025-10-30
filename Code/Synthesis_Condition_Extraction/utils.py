import json
from typing import Dict, List, Tuple

def should_be_used_for_example(paragraph:str, example_mof:dict):
    """Input the extraction paragraph and a dict containing all information of a mof.
    Return whether the mof should be used as example"""
    if example_mof["paragraph"] == paragraph:
        return False
    return True


def __json_to_example(synthesis_json:dict, paragraph:str):
    if not should_be_used_for_example(paragraph, synthesis_json):
        return None
    example = {}
    example['paragraph'] = synthesis_json["paragraph"]
    example['result'] = json.dumps([{
        "Compound_Name": [mof for mof in synthesis_json["Compound_Name"]],
        "Metal_Source": [
            {
                "precursor_name": metal["precursor_name"],
                "amount": metal["amount"]
            } for metal in synthesis_json["Metal_Source"]],
        "Organic_Linker": [
            {
                "precursor_name": organic["precursor_name"],
                "amount": organic["amount"]
            } for organic in synthesis_json["Organic_Linker"]],
        "Solvent": [
            {
                "precursor_name": solvent["precursor_name"],
                "amount": solvent["amount"]
            } for solvent in synthesis_json["Solvent"]],
        "Modulator": [
            {
                "precursor_name": modulator["precursor_name"],
                "amount": modulator["amount"]
            } for modulator in synthesis_json["Modulator"]],
        "Reaction_Time": [t for t in synthesis_json["Reaction_Time"]],
        "Reaction_Temperature": [t for t in synthesis_json["Reaction_Temperature"]],
    }], indent=2)
    return example

def json_to_example(synthesis_json:dict, paragraph:str):
    return __json_to_example(synthesis_json, paragraph)
    