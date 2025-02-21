from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime
import tempfile
import os
import re
from .scihub_wrapper import SciHubWrapper
from .paper_search import PaperSearch
import logging

app = FastAPI()
wrapper = SciHubWrapper()
paper_search = PaperSearch()

# Enable CORS for the frontend
# Get the Vercel URL from environment or default to localhost
FRONTEND_URL = os.getenv('VERCEL_URL', 'http://localhost:3000')
if FRONTEND_URL.startswith('http://') is False and FRONTEND_URL.startswith('https://') is False:
    FRONTEND_URL = f'https://{FRONTEND_URL}'

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str

def is_doi(query: str) -> bool:
    """Check if the query looks like a DOI."""
    logging.info(f"Checking DOI format for: {query}")
    doi_pattern = r'^(?:(?:10\.\d{4,})|(?:DOI:?\s*)?\s*(10\.\d{4,}))/[-._;()/:A-Za-z0-9]+$'
    result = bool(re.match(doi_pattern, query, re.IGNORECASE))
    logging.info(f"DOI format valid for '{query}': {result}")
    return result

async def get_doi_from_title(title: str) -> str:
    """Search for a paper by title and return its DOI."""
    doi = paper_search.search_by_title(title)
    if not doi:
        raise HTTPException(status_code=404, detail=f"No paper found matching title: {title}")
    return doi

@app.get("/api/mirrors")
async def check_mirrors():
    """Check status of all Sci-Hub mirrors."""
    try:
        results = await wrapper.check_mirrors_async()
        return {
            "mirrors": results,
            "cached": not wrapper._should_refresh_cache(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check mirrors: {str(e)}"
        )

@app.post("/api/download")
async def download_paper(request: SearchRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Please provide a DOI or paper title")
    
    # Create a temporary file to store the PDF
    temp_dir = tempfile.mkdtemp()
    output_file = os.path.join(temp_dir, "paper.pdf")
    
    try:
        # If not a DOI, search by title first
        if not is_doi(query):
            logging.info(f"Searching for paper by title: {query}")
            query = await get_doi_from_title(query)
            logging.info(f"Found DOI for title: {query}")
        
        try:
            # Download the paper using the DOI
            wrapper.download(query, output_file)
            
        except Exception as e:
            if os.path.exists(output_file):
                os.remove(output_file)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to download paper: {str(e)}"
            )
        
        # Check if file was downloaded successfully
        if not os.path.exists(output_file):
            raise HTTPException(status_code=404, detail="Paper not found")
            
        # Stream the file to the client
        def iterfile():
            with open(output_file, "rb") as file:
                yield from file
            # Cleanup after streaming
            os.remove(output_file)
            os.rmdir(temp_dir)
            
        return StreamingResponse(
            iterfile(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=paper.pdf"
            }
        )
        
    except Exception as e:
        # Cleanup on error
        if os.path.exists(output_file):
            os.remove(output_file)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))


import tempfile

def generate_pdf_chunks(file_path, chunk_size=1024*1024):
    """Generator function to yield PDF chunks."""
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

@app.get("/{doi:path}")
def download_with_doi(doi: str):
    """Download paper directly using DOI from URL."""
    if is_doi(doi):
        try:
            # Use a temporary file to store the downloaded PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                wrapper.download(doi, tmp_file.name)

            # Stream the PDF in chunks
            return StreamingResponse(
                generate_pdf_chunks(tmp_file.name),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"inline; filename={doi.replace('/', '_')}.pdf"
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Invalid DOI format.")
