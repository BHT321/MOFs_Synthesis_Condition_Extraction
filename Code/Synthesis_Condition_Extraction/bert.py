from sentence_transformers import SentenceTransformer
from typing import Callable
import json
from scipy import spatial
import numpy as np
from transformers import BertTokenizer, BertModel, logging
import torch

logging.set_verbosity_error()

bert_model_path = "bert-base-uncased"
sbert_model_path = "sentence-transformers/all-MiniLM-L6-v2"

sbert_model = SentenceTransformer(sbert_model_path)
bert_tokenizer = BertTokenizer.from_pretrained(bert_model_path)
bert_model = BertModel.from_pretrained(bert_model_path).cuda()

bert_embedding_to_examples = {}
sbert_embedding_to_examples = {}

def get_sbert_embedding(text):
    return sbert_model.encode(text)

def get_bert_embedding(text):
    encoded_input = bert_tokenizer.encode(text, truncation=True, max_length=512)
    with torch.no_grad():
        output = bert_model(torch.tensor([encoded_input]).cuda())
    return torch.mean(output[0], dim=1).squeeze().cpu().numpy()

def init_bert(MOF_FILE):
    with open(MOF_FILE) as f:
        mofs = json.loads(f.read())
    for mof in mofs:
        bert_embedding_to_examples[tuple(get_bert_embedding(mof['paragraph']).tolist())] = mof


def init_sbert(MOF_FILE):
    with open(MOF_FILE) as f:
        mofs = json.loads(f.read())
    for mof in mofs:
        sbert_embedding_to_examples[tuple(get_sbert_embedding(mof['paragraph']).tolist())] = mof

def retrieve_bert_examples(paragraph):
    return __retreive_examples(paragraph, get_bert_embedding, bert_embedding_to_examples)

def retrieve_sbert_examples(paragraph):
    return __retreive_examples(paragraph, get_sbert_embedding, sbert_embedding_to_examples)

def __retreive_examples(paragraph:str, get_embedding:Callable, embeddings):
    p_embedding = get_embedding(paragraph)
    similarities = []

    for embedding in embeddings:
        similarities.append((1 - spatial.distance.cosine(embedding, p_embedding), embedding))
    similarities.sort(reverse=True)
    examples = []
    for _, embedding in similarities:
        examples.append(embeddings[embedding])
    return examples
