
import json
from transformers import BertTokenizer, BertForSequenceClassification
from torch.optim import AdamW
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score, confusion_matrix, roc_auc_score
from torch.utils.data import DataLoader, TensorDataset
import torch
import numpy as np
import statistics
import copy
import argparse

#######################
# 1.Generate data set #
#######################

# Data format: a list of dictionary. Dictionary format:
# paragraphs.append({
#                     'paragraph': paragraph,
#                     'startPosition': paragraph_start,
#                     'endPosition': paragraph_end,
#                     'doi': start_row['doi'],
#                     'mof-id': start_row['mof-id'],
#                     'fileName': start_row['txt-name'],
#                     'is_synthesis_paragraph': True,
#                     'marker': creator_id,
#                     'twice_marked': False,
# })

# Extract the dataset.
with open('parsed_synthesis_paragraphs_totalDataPara.csv.txt', 'r', encoding='utf-8') as file:
    extracted_paragraphs = [json.loads(line) for line in file]

synthesis_paragraphs = [p for p in extracted_paragraphs if p['is_synthesis_paragraph'] and p['twice_marked']]
non_synthesis_paragraphs = [p for p in extracted_paragraphs if not p['is_synthesis_paragraph']]

# numpy is good for pytorch. If user needs clearness, original list is more suitable.
data = np.array([entry['paragraph'] for entry in synthesis_paragraphs + non_synthesis_paragraphs])
labels = np.array([1] * len(synthesis_paragraphs) + [0] * len(non_synthesis_paragraphs))
print(f"load {len(data)} data and {len(labels)} labels!")


##################################
# 2.Model and Dataset Initiating #
##################################
# For linux server.


parser = argparse.ArgumentParser(description="Train a BERT model for MOFs classification")
parser.add_argument('model_name', nargs='?', default='uncased_L-12_H-768_A-12', help='BERT model name') # bert-base-uncased model names uncased_L-12_H-768_A-12
args = parser.parse_args()

base_model_path = '/home/BertModels/'
model_name = args.model_name
model_path = base_model_path + model_name + '/'

tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path, num_labels=2)

model.to('cpu')  # If not so, the gpu memory will exceed and break. Our gpu is weak.
initial_model_state = copy.deepcopy(model.state_dict())
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)
model.to(device)  # move to gpu


# Data Tokenizer
def tokenize_data(original_text):
    # Batch_encode_plus is better for batch processing.
    return tokenizer.batch_encode_plus(original_text, padding=True, truncation=True, max_length=512, return_tensors="pt")


def bert_DataLoader(sentences, sentence_labels, shuffle):
    return DataLoader(TensorDataset(tokenize_data(sentences)['input_ids'], tokenize_data(sentences)['attention_mask'],
                                    torch.tensor(sentence_labels)), batch_size=32, shuffle=shuffle)


##############################
# 4. Training and Validation #
##############################


def evaluate_metrics(predictions, labels, scores):
    """
    Calculate f1, precision, recall, accuracy, tp, fp, fn and auc with lists of predictions, labels and scores.
    """
    predictions, labels = np.array(predictions), np.array(labels)

    tn, fp, fn, tp = confusion_matrix(labels, predictions).ravel()
    roc_auc = roc_auc_score(labels, scores)
    metric_functions = {
        'f1': f1_score,
        'precision': precision_score,
        'recall': recall_score,
        'accuracy': accuracy_score
    }

    metric_results = {name: func(labels, predictions) for name, func in metric_functions.items()}
    metric_results.update({'tp': tp, 'fn': fn, 'fp': fp, 'roc_auc': roc_auc})

    return metric_results


# Initialize StratifiedKFold and optimizer
k = 5
stratified_kfold = StratifiedKFold(n_splits=k, shuffle=True, random_state=42)
optimizer = AdamW(model.parameters(), lr=2e-5)

count = 0
timer = statistics.Timer()
metrics = {'f1': [], 'precision': [], 'recall': [], 'accuracy': [], 'tp': [], 'fn': [], 'fp': [], 'roc_auc': []}

# K-Fold training and evaluation
for train_idx, validate_idx in stratified_kfold.split(data, labels):
    count += 1
    print(f"Start {count} round!")
    timer.start()

    if max(train_idx) >= len(labels) or max(validate_idx) >= len(labels):
        print("Index out of bounds. Skipping this iteration.")
        print(f"Debug: labels[train_idx].shape = {labels[train_idx].shape}, type = {type(labels[train_idx])}")
        continue

    # Split the data, tokenize sentences and create DataLoader
    train_loader = bert_DataLoader(data[train_idx], labels[train_idx], shuffle=True)
    validate_loader = bert_DataLoader(data[validate_idx], labels[validate_idx], shuffle=False)

    model.load_state_dict(initial_model_state)  # initiate the model state for k-fold
    model.train()
    for epoch in range(3):  # Number of epochs
        # print(f"Round {count}, epoch {epoch} training start!")
        for batch in train_loader:
            optimizer.zero_grad()
            input_ids, attention_mask, batch_labels = batch
            input_ids, attention_mask, batch_labels = input_ids.to(device), attention_mask.to(device), batch_labels.to(device)

            batch_labels = batch_labels.unsqueeze(1)  # Expanding dimensions to align with logits shape
            outputs = model(input_ids, attention_mask=attention_mask, labels=batch_labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()

    model.eval()
    all_predictions, all_labels, all_scores = [], [], []
    with torch.no_grad():
        for batch in validate_loader:
            input_ids, attention_mask, batch_labels = batch
            input_ids, attention_mask, batch_labels = input_ids.to(device), attention_mask.to(device), batch_labels.to(device)

            outputs = model(input_ids, attention_mask=attention_mask)
            predictions = torch.argmax(outputs.logits, dim=1)

            predictions = predictions.cpu().numpy()
            batch_labels = batch_labels.cpu().numpy()

            all_predictions.extend(predictions)
            all_labels.extend(batch_labels)

            # calculate ROC
            scores = torch.softmax(outputs.logits, dim=1)[:, 1]  # Assuming the positive class is at index 1
            scores = scores.cpu().numpy()
            all_scores.extend(scores)

    metrics_results = evaluate_metrics(all_predictions, all_labels, all_scores)
    for name, result in metrics_results.items():
        metrics[name].append(result)
        print(f"{name.upper()}: {result}")

    elapsed_time = timer.record()
    print(f"Elapsed time: {elapsed_time} seconds")

    torch.cuda.empty_cache()

# Calculate the final cross-validation F1 score
final_metrics = {name: np.mean(scores) for name, scores in metrics.items()}
print(f"Final Cross-Validation Metrics: {final_metrics}")

# Save the fine-tuned model
save_model_name = f"../BertModels/synthesis_paragraph_classifier_bert_{model_name}"
model.save_pretrained(save_model_name)

