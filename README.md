# RunIQ 🤖

I used to be a competitive cross-country runner with accesss to resources such as coaches and physical trainers. Now, as someone who still loves to run every day, I often find myself wishing for that guidance when I am unsure to progress or when I get injured. <br><br> The inspiration for this project was quite simple: I wanted a quick, reliable way to get advice regarding cross-country training and injury recovery. To solve this, I built `RunIQ` - a personal, RAG-powered running coach and general knowledge bot.<br>

> **Important Note**: The data processed by this project is copyrighted and I am not at liberty to distribute it. This repository is intended for personal use and demonstration under fair use. However, the pipelines are fully configurable - if you understand the configuration structures, you can create your own configs to process and embed content from publicly available sources.
> <br>

## Key Features & Approach ⚡️

- **Data Processing** - Prepares data for user interaction and retrieval augmented generation.
  - **Ingestion Pipeline** - Retrieves and stores raw HTML from the web.
    - _Site Map Processing_: Parses XML sitemaps to collect all desired download links.
    - _HTML Downloading_: Downloads raw HTML files and saves them to disk for futher processing.
  - **Vectorization Pipeline**
    - _Intermediate Processing_: Converts raw HTML into structured JSON representations.
    - _Chunking_: Splits text into semantically meaningful chunks for embedding.
    - _Embedding_: Generates vector embeddings from text chunks using the `bge-base-en-v1.5` model.
- **RAG CLI** - Simple interactive command-line interface for querying the dataset.
  - _Retriever_: Embeds the user query and fetches relevant context.
  - _Generator_: Creates a response based on retriever context.
- **Extensibility**
  - Intermediary storage of HTML and JSON allows for the exploration of different chunk schemes and embedding models.
  - Adjust or test different chunking schemes without re-downloading data.
  - Config-driven processing enables easy addition of new sources
- **Validation**
  - Retrieval performance evaluated using a labeled dataset and precision-at-k.
  - Tested 5 embedding models, each with 21 hyperparameter variations for chunking.
  - Optimal model + chunking combination selected based on retrieval performance.

<br>

## Validation Results 📝

| Model            | Chunk Size |  Chunk Overlap  |   Chunk Strategy    | P@1 | P@5 | P@10 | MAP@1 | MAP@5 | MAP@10 |
| :--------------- | :--------- | :-------------: | :-----------------: | :-: | :-: | :--: | ----- | ----- | ------ |
| bge-base-en-v1.5 | 256        | 50 (20 percent) | Naive (token-based) | .86 | .79 | .71  | .86   | .84   | .84    |

> _Note:_ This is the optimal model + scheme based on my experiments.

<br>

## Example Query (RAG CLI) 🧠

#### Query: What stretches can I do to prevent injury?

#### Response:

1. Hip Flexor Stretch: Start by standing with feet hip-width apart. Draw one leg up to hip level and let the knee fall outward as you grab the ankle to support the leg. Hold for a brief stretch before performing the same move on the opposite side. Continue to alternate. This stretch promotes hip flexion, abduction, and external rotation to allow for improved hip mobility during your workout.

2. Hamstring Stretch: From standing, bend one knee as you step the other heel forward with the straight leg. Send hips back to bend forward, scooping both hands along the floor from hip to toe before returning to stand. Repeat on the other leg. This is a great stretch to promote hamstring lengthening for reduced risk of a hamstring injury while running.

> _Note_: The system can produce longer, detailed multi-step responses with full instructions.

<br>

## Future Considerations 🔮

- **Optimizing Generation**: Explore different generation models and optimization techniques to reduce query to response latency.
- **Optimizing Ingestion**: Make preprocessing more efficient by introducing parralel workers (and once Python3.14 comes out - threads!).
- **Automating Ingestion**: Schedule regular updates or new data sources with minimal manual intervention.
- **Short Term Memory**: Enable the generator to maintain context across queries for more cohesive multi-turn conversations.
