from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import tempfile
import os
from scidownl import scihub_download
import re

app = FastAPI()

# Enable CORS for the frontend
# Configure CORS for both local development and production
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

# Add Vercel URL if available
vercel_url = os.getenv('VERCEL_URL')
if vercel_url:
    origins.append(f"https://{vercel_url}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str

def is_doi(query: str) -> bool:
    """Check if the query looks like a DOI."""
    doi_pattern = r'^(?:(?:10\.\d{4,})|(?:DOI:?\s*)?\s*(10\.\d{4,}))/[-._;()/:A-Za-z0-9]+$'
    return bool(re.match(doi_pattern, query, re.IGNORECASE))

@app.post("/api/download")
async def download_paper(request: SearchRequest):
    query = request.query.strip()
    
    # Create a temporary file to store the PDF
    temp_dir = tempfile.mkdtemp()
    output_file = os.path.join(temp_dir, "paper.pdf")
    
    try:
        # Determine if the query is a DOI or title
        paper_type = "doi" if is_doi(query) else "title"
        
        try:
            # Clean DOI if present
            if paper_type == 'doi':
                query = re.sub(r'^(?:DOI:?\s*)?(.+)$', r'\1', query)

            # Download the paper
            scihub_download(query, paper_type=paper_type, out=output_file)
        except Exception as e:
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
