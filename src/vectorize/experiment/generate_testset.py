import os
from ragas.testset import TestsetGenerator  # type: ignore
from langchain_chroma import Chroma  # type: ignore
from langchain_ollama import OllamaLLM  # type: ignore
from sentence_transformers import SentenceTransformer  # type: ignore
from langchain.schema import Document  # type:ignore
import random


print("loaded imports")
# load in all of the chunks
persistent_path = os.environ['RUNBOT_CHROMA_PATH']
collection_name = os.environ['RUNBOT_CHROMA_COLLECTION']
vectorstore = Chroma(persist_directory=persistent_path,
                     collection_name=collection_name)
collection = vectorstore._collection
documents = collection.get()
print("loaded documents")

docs = [
    Document(page_content=text, metadata=meta) for text, meta in zip(documents['documents'], documents['metadatas'])
]
docs_sample = random.sample(docs, 1)

# load the models
generator_llm = OllamaLLM(model='llama2-3b')
embedding_model = SentenceTransformer("BAAI/bge-base-en-v1.5")
print("loaded models")

# define testset generator
generator = TestsetGenerator.from_langchain(
    llm=generator_llm,
    embedding_model=embedding_model,
)

print("generating testset")
testset = generator.generate_with_langchain_docs(docs_sample, testset_size=10)
print("generated testset")
test_df = testset.to_pandas()
test_df.head()
