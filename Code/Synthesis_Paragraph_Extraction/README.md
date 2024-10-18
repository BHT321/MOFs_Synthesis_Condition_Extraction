# Synthesis Paragraph Extraction
This code is used to extract synthesis paragraphs from MOFs literature .
## Requirement
**Operation system**: Ubuntu 20.04  
**GPU**: NVIDIA GeForce RTX 3090  
**CUDA version**: 11.4  
**Python version**: 3.8.18   
**Packages**:  

- python-dotenv==1.0.1
- nltk==3.7
- transformers==4.33.3
- sentence-transformers==2.2.2
- torch==2.1.2
- numpy==1.24.4
- scipy==1.10.1
- pandas==1.5.3
- scikit-learn==1.3.0
- bs4==4.12.2
- paddlenlp==2.0.0
- openai==1.25.0

## Usage
### Training Classification Model
1.  To train a binary classification model to determine whether a paragraph contains a full set of MOFs synthesis conditions, go to https://huggingface.co/google-bert/bert-base-uncased to access pre-trained model. 
2. Run the code in `training.py` to fine-tune the pre-trained model with synthesis paragraphs annotated by professionals in `parsed_synthesis_paragraphs.txt`. 
3. If you want to insert new synthesis paragraphs in `PDF` format to supplement your training dataset ,  you can refer to https://github.com/pdf2htmlEX/pdf2htmlEX to convert `PDF` to `HTML` format, then run `convert.js` to convert `HTML` to `txt` format.
4. If the training dataset is heavily imbalanced with more negative samples, run `augmentation.py` to generate more diverse  positive samples by adopting data augmentation.

### Synthesis Paragraph Extraction        
Run the code in `synthesis_paragraph_extracter.py` with your fine-tuned model to extract synthesis paragraphs. It will save the extracted paragraphs to `synthesis_paragraphs.json`.

### Metrics of Results
Run the code in `training.py`, and you can observe the performance metrics of your fine-tuned model presented in the following format: 

```
metric_functions = {
    'f1': f1_score,
    'precision': precision_score,
    'recall': recall_score,
    'accuracy': accuracy_score
}
```

