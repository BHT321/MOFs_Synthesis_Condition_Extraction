
import nltk
from nltk.tokenize import TextTilingTokenizer
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import json


#####################################
# 1. Synthesis Paragraph Extraction #
#####################################
NLTK_text_tokenizer = TextTilingTokenizer()

print("Start loading the model.")
classifier_model_path = '../BertModels/synthesis_paragraph_classifier_bert/'
original_model_path = '../BertModels/uncased_L-12_H-768_A-12/'
Bert_tokenizer = BertTokenizer.from_pretrained(original_model_path)
model = BertForSequenceClassification.from_pretrained(classifier_model_path, num_labels=2)
model.eval()


def segment_text(text):
    print("Start segmenting text.")
    segmented_text = NLTK_text_tokenizer.tokenize(text.replace("\n", "\n\n"))
    print("Finish segmenting text.")
    return [para.replace('\n', '') for para in segmented_text if para.strip()]


def classify_paragraphs(paragraphs):
    print("Start classifying paragraphs.")
    classified_paragraphs = []
    for paragraph in paragraphs:
        inputs = Bert_tokenizer(paragraph, padding=True, truncation=True, max_length=512, return_tensors="pt")
        outputs = model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=1).item()
        if prediction == 1:
            classified_paragraphs.append(paragraph)
    print("Finish classifying paragraphs.")
    return classified_paragraphs


def read_paper_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().splitlines()


def process_paper(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return classify_paragraphs(segment_text(text))


# Read the list of paper names
paper_list = read_paper_list('paper_list.txt')

# Initialize an empty list to store all synthesis paragraphs from each paper
synthesis_paragraphs = []

# Process each paper
for paper_name in paper_list:
    paper_path = f"txt/{paper_name}"
    synthesis_paragraphs.extend(process_paper(paper_path))

# Print all classified paragraphs
for para in synthesis_paragraphs:
    print(para)
    print("----")

# Save the extracted paragraphs to a JSON file
with open('synthesis_paragraphs.json', 'w', encoding='utf-8') as json_file:
    json.dump(synthesis_paragraphs, json_file, ensure_ascii=False, indent=4)



