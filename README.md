# Runbot 🤖
I used to be a competitive cross-country runner with accesss to resources such as coaches and physical trainers. Now, as someone who still loves to run every day, I often find myself longing for those resources when I am not sure on how to progress or when I get injured. So, the inspiration for this project was quite simple: I wanted a quick, easy, and reliable way to get advice regarding cross country training and injury recovery. To solve this, I decided to build ``Runbot`` - a personal, RAG powered running coach and general knowledge bot. 

> Important Note: The data processed by this project is copyrighted and I am not at liberty to distribute it. This repository is intended for personal use and demonstration under fair use. However, the pipelines are fully configurable - if you understand the configuration structures, you can create your own configs to process and embed content from publicly available sources.
<br>

##  Key Features & Approach ⚡️
- **Data Processing** - Prepares data for user interaction and retrieval augmented generation.
  - **Ingestion Pipeline** - Retrieves and stores raw HTML from the web.
    - *Site Map Processing*: Parses XML sitemaps to collect all desired download links.
    - *HTML Downloading*: Downloads raw HTML files and saves them to disk for futher processing.
  - **Vectorization Pipeline**
    - *Intermediate Processing*: Converts raw HTML into structured JSON representations.
    - *Chunking*: Splits text into semantically meaningful chunks for embedding.
    - *Embedding*: Generates vector embeddings from text chunks using the ``bge-base-en-v1.5`` model.
- **RAG CLI** - Simple interactive command-line interface for querying the dataset.
  - *Retriever*: Embeds the user query and fetches relevant context.
  - *Generator*: Creates a response based on retriever context.
- **Extensibility**
  - Intermediary storage of HTML and JSON allows for the exploration of different chunk schemes and embedding models.
  - Adjust or test different chunking schemes without re-downloading data.
  - Config-driven processing enables easy addition of new sources
- **Validation**
  - Retrieval performance evaluated using a labeled dataset and precision-at-k.
  - Tested 5 embedding models, each with 21 hyperparameter variations for chunking.
  - Optimal model + chunking combination selected based on retrieval performance.

