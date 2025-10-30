import json
import openai
import os
from dotenv import load_dotenv
from sampling import load_examples_by_random, load_examples_by_BM25_similarity, load_examples_by_bert_similarity, load_examples_by_sbert_similarity


with open("CSD_few_shot_prompt.txt", 'r', encoding='utf-8') as file:     
    few_shot_prompt = file.read()

with open("CSD_zero_shot_prompt.txt", 'r', encoding='utf-8') as file:    
    zero_shot_prompt = file.read()

def check_json_format(result:str):
    result = result.strip()
    if result.startswith("```json") and result.endswith("```"):
        result = result[7:-3].strip()
    return result

def combine_example_and_input(examples, paragraph, system_prompt):
    prompt = []
    prompt.append({"role": "system", "content": system_prompt})
    for example in examples:
        prompt.append({"role": "user", "content": example['paragraph']})
        prompt.append({"role": "assistant", "content": example['result']})
    prompt.append({"role": "user", "content": paragraph})
    return prompt
  

def extract_synthesis_parameters(paragraph, example_size, model='gpt-3.5-turbo', rag_method="BM25", temperature=0, output_n=1):
    if example_size == 0:
        examples = []
    elif rag_method == 'random':
        examples = load_examples_by_random(paragraph, example_size)
    elif rag_method == 'bert':
        examples = load_examples_by_bert_similarity(paragraph, example_size)
    elif rag_method == 'sbert':
        examples = load_examples_by_sbert_similarity(paragraph, example_size)
    elif rag_method == "BM25":
        examples = load_examples_by_BM25_similarity(paragraph, example_size)
    else:
        raise ValueError()
    if example_size == 0:
        system_prompt = zero_shot_prompt
    else:
        system_prompt = few_shot_prompt
    prompt = combine_example_and_input(examples, paragraph, system_prompt)
    results = extract_synthesis_parameters_by_openai(prompt, model, temperature, output_n)
    results = check_json_format(results)
    json_result = json.loads(results)
    
    if isinstance(json_result, dict):
        json_result = [json_result]
    elif not isinstance(json_result, list):
        raise json.decoder.JSONDecodeError("can not parse the response to right JSON format")
    return json_result

# Parameter Extraction Setup
load_dotenv()

def extract_synthesis_parameters_by_openai(prompt, model, temperature=0, output_n=1):
    """
    Extract synthesis parameters using openai-api
    :param prompt: list of messages
    :param model: valid model: "gpt-3.5-turbo", "gpt-4"
    :param temperature: 0-2
    """
    OPENAI_CLIENT = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
    )
    # openai_tokens_count(prompt, model)
    response = OPENAI_CLIENT.chat.completions.create(
        model=model,
        messages=prompt,
        temperature=temperature,
        n = output_n,
    )
    if output_n == 1:
        return response.choices[0].message.content
    else:
        return [choice.message.content for choice in response.choices]

