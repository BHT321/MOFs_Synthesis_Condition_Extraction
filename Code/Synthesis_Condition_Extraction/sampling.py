"""
This script contains all sampling methods, including BM25, Bert, SBert, random ...
"""
from utils import json_to_example
import BM25
import bert
import json
import random


EXAMPLE_FILE = "CSD_annotated_data.json"
"""
Point to the path of human-model annotation file.
"""

with open(EXAMPLE_FILE) as f:
    EXAMPLES = json.loads(f.read())
BM25.init_new(EXAMPLE_FILE)
bert.init_bert(EXAMPLE_FILE)
bert.init_sbert(EXAMPLE_FILE)

# load the valid_data_second_label file, extract 11 params
def load_examples_by_random(paragraph, example_size):
    candidate_examples = random.sample(EXAMPLES, example_size + 5)
    examples = _load_examples_from_candidate_array(paragraph, example_size, candidate_examples)
    return examples

def load_examples_by_BM25_similarity(paragraph, example_size):
    candidate_examples = BM25.retrive_examples(paragraph)
    examples = _load_examples_from_candidate_array(paragraph, example_size, candidate_examples)
    return examples[::-1]

def load_examples_by_bert_similarity(paragraph, example_size):
    candidate_examples = bert.retrieve_bert_examples(paragraph)
    examples = _load_examples_from_candidate_array(paragraph, example_size, candidate_examples)
    return examples[::-1]


def load_examples_by_sbert_similarity(paragraph, example_size):
    candidate_examples = bert.retrieve_sbert_examples(paragraph)
    examples = _load_examples_from_candidate_array(paragraph, example_size, candidate_examples)
    return examples[::-1]

def _load_examples_from_candidate_array(paragraph, example_size, candidate_array):
    array = []
    i = 0
    while len(array) < example_size and i < len(candidate_array):
        example = json_to_example(candidate_array[i], paragraph)
        if not example:
            i += 1
            continue
        array.append(example)
        i += 1
    return array
