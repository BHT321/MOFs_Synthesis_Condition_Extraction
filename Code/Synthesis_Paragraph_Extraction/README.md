# Synthesis Paragraph Extraction
This code is used to extract synthesis paragraphs from MOFs literature.

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
- bs4==4.12.2
- openai==1.25.0

## Usage
### Synthesis Paragraph Extraction        
Run the code in `synthesis_paragraph_extracter.py` with a fine-tuned BERT model to extract synthesis paragraphs from MOFs literature. The model should be trained to determine whether a paragraph contains a full set of MOFs synthesis conditions. 

The extraction results will be saved to `synthesis_paragraphs.json`.

### Training Data
The file `parsed_synthesis_paragraphs.txt` contains synthesis paragraphs annotated by professionals, which can be used as reference training data for fine-tuning classification models.

