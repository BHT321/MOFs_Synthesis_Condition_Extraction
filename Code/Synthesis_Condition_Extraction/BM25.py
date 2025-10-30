from langchain_community.retrievers import BM25Retriever
from langchain.schema import Document
import json

documents = []


# loads data
def init_new(MOF_FILE, document_size=None):
    global retriever, documents
    retriever, documents = None, []
    with open(MOF_FILE) as f:
        mofs = json.loads(f.read())
    if document_size:
        mofs = mofs[:document_size]
    for mof in mofs:
        documents.append(Document(page_content=mof["paragraph"], metadata={"mof": mof}))

    retriever = BM25Retriever.from_documents(documents)
    # set select top k document
    if document_size:
        retriever.k = min(30, document_size)
    else:
        retriever.k = 30

def load_examples_by_BM25_similarity(paragraph:str, example_size:int=1):
    results = retriever.get_relevant_documents(paragraph)
    candidate_mofs = [result.metadata["mof"] for result in results]
    return candidate_mofs

def retrive_examples(paragraph:str):
    return [result.metadata["mof"] for result in retriever.get_relevant_documents(paragraph)]


if __name__ == '__main__':
    p = "[La( d Hdtpc)(OH)(H 2 O)] n (6): A mixture of La 2 O 3 (0.0325 g, 0.1 mmol), H 3 dtpc (0.035 g, 0.2 mmol) and water (15 mL) was placed in a 25 mL stainless reactor fitted with a Teflon liner and heated to 160 °C for 72 hours. It was then cooled to room temperature, and colorless needle-like crystals were obtained. Yield: 80%."
    result = retriever.get_relevant_documents(p)
    print(result[0])
    print(json.dumps(load_examples_by_BM25_similarity(p, 2), indent=2))