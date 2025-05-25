from mcp.server.fastmcp import FastMCP, Image
import sys
import requests
import json
import faiss
import numpy as np
import logger
from markitdown import MarkItDown
from pathlib import Path
import hashlib
from models import UrlInput,MarkdownOutput
import trafilatura
from tqdm import tqdm
import os

# instantiate an MCP server client
mcp = FastMCP("Calculator")

EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 256
CHUNK_OVERLAP = 40
PATH = Path("D:/EAG/EAG_SESSION_7/chrome_extension")

#ROOT = Path(__file__).parent.resolve()

def get_embedding(text: str) -> np.ndarray:
    response = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
    response.raise_for_status()
    return np.array(response.json()["embedding"], dtype=np.float32)

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    for i in range(0, len(words), size - overlap):
        yield " ".join(words[i:i+size])

def mcp_log(level: str, message: str) -> None:
    """Log a message to stderr to avoid interfering with JSON communication"""
    sys.stderr.write(f"{level}: {message}\n")
    sys.stderr.flush()

@mcp.tool()
def strings_to_chars_to_int(input: str) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(StringsToIntsInput) -> StringsToIntsOutput")
    ascii_values = [ord(char) for char in input.string]
    return list[int](ascii_values=ascii_values)

@mcp.tool()
def search_documents(query: str) -> list[str]:
    """Search for relevant content from uploaded documents."""
   # ensure_faiss_ready()
    logger.loggingInfo(f"SEARCH query {query}")
    try:
        index = faiss.read_index(str(PATH / "faiss_index" / "index.bin"))
        metadata = json.loads((PATH / "faiss_index" / "metadata.json").read_text())
        query_vec = get_embedding(query).reshape(1, -1)
        D, I = index.search(query_vec, k=3)
        results = []
        for idx in I[0]:
            data = metadata[idx]
            results.append(f"{data['chunk']},[Source: {data['url']}, ID: {data['chunk_id']}]")
        return results
    except Exception as e:
        return [f"ERROR: Failed to search: {str(e)}"]
    
@mcp.tool()
def extract_webpage(input: str) -> MarkdownOutput:
    """Extract and convert webpage content to markdown. Usage: extract_webpage|input={"url": "https://example.com"}"""

    downloaded = trafilatura.fetch_url(input)
    if not downloaded:
        return MarkdownOutput(markdown="Failed to download the webpage.")

    markdown = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=False,
        include_images=False,
        output_format='markdown'
    ) or ""
    return MarkdownOutput(markdown=markdown)

def ensure_faiss_ready():
    from pathlib import Path
    index_path = PATH / "faiss_index" / "index.bin"
    meta_path = PATH / "faiss_index" / "metadata.json"
    if not (index_path.exists() and meta_path.exists()):
        logger.loggingInfo("Index not found — running process_documents()...")
       # process_documents()
    else:
        logger.loggingInfo("Index already exists. Skipping regeneration.")

def process_url(url: str)-> str:
    """step1: extract the web page"""

    mark_down_resp = extract_webpage(url).markdown
    """Process documents and create FAISS index"""
    logger.loggingInfo("Indexing documents with trafilatura...")
    #ROOT = Path(__file__).parent.resolve()
    DOC_PATH = PATH / "S7_documents"
    INDEX_CACHE = PATH / "faiss_index"
    os.makedirs(DOC_PATH,exist_ok=True)
    os.makedirs(INDEX_CACHE,exist_ok=True)
    #DOC_PATH.mkdir(exist_ok=True)
    #INDEX_CACHE.mkdir(exist_ok=True)
    INDEX_FILE = INDEX_CACHE / "index.bin"
    METADATA_FILE = INDEX_CACHE / "metadata.json"
    
    metadata = json.loads(METADATA_FILE.read_text()) if METADATA_FILE.exists() else []
    index = faiss.read_index(str(INDEX_FILE)) if INDEX_FILE.exists() else None
    all_embeddings = []
    try:
            logger.loggingInfo("chunk preparation")
            chunks = list(chunk_text(mark_down_resp))
            file_name = mark_down_resp.split('\n')[0]
            file_url = url
            embeddings_for_file = []
            new_metadata = []
            for i, chunk in enumerate(tqdm(chunks, desc=f"Embedding {file_name}")):
                embedding = get_embedding(chunk)
                embeddings_for_file.append(embedding)
                new_metadata.append({"doc": file_name, "chunk": chunk, "chunk_id": f"{file_name}_{i}", "url":f"{file_url}"})
            if embeddings_for_file:
                if index is None:
                    dim = len(embeddings_for_file[0])
                    index = faiss.IndexFlatL2(dim)
                index.add(np.stack(embeddings_for_file))
                metadata.extend(new_metadata)
    except Exception as e:
            logger.loggingError(f"Failed to process {file_name}: {e}")

    #CACHE_FILE.write_text(json.dumps(CACHE_META, indent=2))
    METADATA_FILE.write_text(json.dumps(metadata, indent=2))
    if index and index.ntotal > 0:
        faiss.write_index(index, str(INDEX_FILE))
        logger.loggingInfo("Saved FAISS index and metadata")
    else:
        logger.loggingInfo("No new documents or updates to process.")



if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING THE SERVER AT AMAZING LOCATION")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
