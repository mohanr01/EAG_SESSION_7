# chromeExtention

## Overview

chrome_extension is a web-based semantic search application that enables both automatic and manual indexing of web pages. The indexed content is embedded using Ollama's Nomic embedding and stored locally with FAISS for efficient vector search. When a user submits a query, the system utilizes a Retrieval-Augmented Generation (RAG) agent to perform semantic search and retrieve relevant information.

## Features

- **Automatic and Manual Web Page Indexing**: Index web pages either on demand (manually) or automatically.
- **Efficient Local Storage**: Uses FAISS for storing and retrieving high-dimensional embeddings.
- **Semantic Search with RAG**: Employs a Retrieval-Augmented Generation agent to answer user queries based on indexed data.
- **Web Page Embedding**: Uses Ollama Nomic embedding to convert web page content into high-quality vector representations.
- **Local Storage**: All data is stored locally, ensuring data privacy and fast access.

## Technologies Used

- `flask==2.0.1`
- `flask-cors==3.0.10`
- `faiss-cpu==1.7.2`
- `numpy==1.21.2`
- `sentence-transformers==2.2.2`
- `torch==1.9.0`
- `trailatura` (for web page extraction)
- Ollama Nomic embedding

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/mohanr01/EAG_SESSION_7.git
   cd EAG_SESSION_7
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   *If `requirements.txt` is not available, install manually:*
   ```bash
   pip install flask==2.0.1 flask-cors==3.0.10 faiss-cpu==1.7.2 numpy==1.21.2 sentence-transformers==2.2.2 torch==1.9.0 trailatura
   ```

4. **Download and Set Up Ollama Nomic Embedding**

   - Follow the official [Ollama documentation](https://docs.ollama.com/) to set up the Nomic embedding locally.

## Usage

1. **Start the Flask Application**

   ```bash
   python app.py
   ```

2. **Indexing Web Pages**

   - **Automatic Indexing**: The system can be configured to periodically index specified web pages.
   - **Manual Indexing**: Use the provided API endpoints or UI to add web pages for indexing.

3. **Semantic Search**

   - Submit a natural language query through the UI or API.
   - The RAG agent will semantically search the indexed content and return relevant answers.

## Example

1. **Index a Web Page Manually**

   ```http
   POST /index
   Content-Type: application/json

   {
     "url": "https://example.com/article"
   }
   ```

2. **Search a Query**

   ```http
   POST /search
   Content-Type: application/json

   {
     "query": "Explain the main topic of the article."
   }
   ```

## How it Works

- Web pages are fetched and processed using Trailatura.
- The content is embedded using Ollama's Nomic embedding model.
- Embeddings are stored in a local FAISS index for fast vector similarity search.
- When a user asks a question, the system retrieves relevant documents with FAISS and uses the RAG agent to generate accurate answers.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.

## License

This project is licensed under the MIT License.

## Acknowledgments

- [FAISS](https://github.com/facebookresearch/faiss)
- [Ollama](https://ollama.com/)
- [Trailatura](https://github.com/johnomotani/trailatura)
- [Sentence Transformers](https://github.com/UKPLab/sentence-transformers)
