import requests
import re
from bs4 import BeautifulSoup
import tempfile
import os

SCIHUB_URLS = [
    'https://sci-hub.se',
    'https://sci-hub.st',
    'https://sci-hub.ru',
]

class SciHubWrapper:
    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def _get_working_url(self):
        """Try different Sci-Hub URLs to find a working one."""
        for url in SCIHUB_URLS:
            try:
                response = self.sess.get(url, timeout=5)
                if response.status_code == 200:
                    return url
            except:
                continue
        raise Exception("No working Sci-Hub URL found")

    def _clean_doi(self, doi):
        """Clean DOI string."""
        match = re.search(r'10\.\d{4,}/[-._;()/:A-Za-z0-9]+', doi)
        if match:
            return match.group(0)
        return doi

    def download(self, identifier, output_path):
        """Download paper by DOI or title."""
        base_url = self._get_working_url()
        
        # Clean DOI if it looks like one
        if re.match(r'^(?:(?:DOI:?\s*)?10\.\d{4,})', identifier):
            identifier = self._clean_doi(identifier)
        
        # First try direct DOI download
        paper_url = f"{base_url}/{identifier}"
        response = self.sess.get(paper_url)
        
        if response.status_code != 200:
            raise Exception("Failed to access paper page")

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find PDF link
        pdf_link = None
        for iframe in soup.find_all('iframe'):
            if iframe.get('src'):
                pdf_link = iframe['src']
                if not pdf_link.startswith('http'):
                    pdf_link = f"https:{pdf_link}" if pdf_link.startswith('//') else f"{base_url}{pdf_link}"
                break
        
        if not pdf_link:
            raise Exception("No PDF link found")

        # Download PDF
        pdf_response = self.sess.get(pdf_link)
        if pdf_response.status_code != 200:
            raise Exception("Failed to download PDF")

        # Save PDF
        with open(output_path, 'wb') as f:
            f.write(pdf_response.content)
            
        return True
