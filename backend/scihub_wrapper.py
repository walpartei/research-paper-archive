import requests
import re
from bs4 import BeautifulSoup
import tempfile
import os
import logging
from urllib.parse import urljoin, urlparse

SCIHUB_URLS = [
    'https://sci-hub.se',
    'https://sci-hub.st',
    'https://sci-hub.ru',
    'https://sci-hub.ee',
    'https://sci-hub.wf',
    'https://sci-hub.ren',
]

logging.basicConfig(level=logging.INFO)

class SciHubWrapper:
    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def _get_working_url(self):
        """Try different Sci-Hub URLs to find a working one."""
        errors = []
        for url in SCIHUB_URLS:
            try:
                response = self.sess.get(url, timeout=5)
                if response.status_code == 200:
                    logging.info(f"Using Sci-Hub mirror: {url}")
                    return url
            except Exception as e:
                errors.append(f"{url}: {str(e)}")
                continue
        raise Exception(f"No working Sci-Hub URL found. Tried: {', '.join(errors)}")

    def _clean_doi(self, doi):
        """Clean DOI string."""
        match = re.search(r'10\.\d{4,}/[-._;()/:A-Za-z0-9]+', doi)
        if match:
            return match.group(0)
        return doi

    def _find_pdf_link(self, soup, base_url):
        """Find PDF link in the page using multiple methods."""
        # Method 1: Look for iframe with PDF
        for iframe in soup.find_all('iframe'):
            if iframe.get('src'):
                return iframe['src']

        # Method 2: Look for embed tags
        for embed in soup.find_all('embed'):
            if embed.get('src'):
                return embed['src']

        # Method 3: Look for links containing PDF
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if '.pdf' in href.lower():
                return href

        # Method 4: Look for meta tags with PDF URL
        for meta in soup.find_all('meta'):
            content = meta.get('content', '')
            if '.pdf' in content.lower():
                return content

        return None

    def _normalize_url(self, url, base_url):
        """Normalize URL to absolute form."""
        if not url:
            return None
        
        if not url.startswith('http'):
            if url.startswith('//'):
                return f'https:{url}'
            return urljoin(base_url, url)
        return url

    def download(self, identifier, output_path):
        """Download paper by DOI or title."""
        base_url = self._get_working_url()
        
        # Clean DOI if it looks like one
        if re.match(r'^(?:(?:DOI:?\s*)?10\.\d{4,})', identifier):
            identifier = self._clean_doi(identifier)
            logging.info(f"Cleaned DOI: {identifier}")
        
        # Try direct DOI download
        paper_url = f"{base_url}/{identifier}"
        logging.info(f"Fetching paper page: {paper_url}")
        
        try:
            response = self.sess.get(paper_url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"Failed to access paper page: {str(e)}")

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find PDF link
        pdf_link = self._find_pdf_link(soup, base_url)
        if not pdf_link:
            # Try to extract error message if present
            error_msg = soup.find('p', class_='error') or soup.find('div', class_='error')
            if error_msg:
                raise Exception(f"Sci-Hub error: {error_msg.text.strip()}")
            raise Exception("No PDF link found in the page")

        # Normalize PDF URL
        pdf_link = self._normalize_url(pdf_link, base_url)
        logging.info(f"Found PDF link: {pdf_link}")

        # Download PDF
        try:
            pdf_response = self.sess.get(pdf_link, timeout=30)
            pdf_response.raise_for_status()
            
            # Verify it's actually a PDF
            content_type = pdf_response.headers.get('content-type', '')
            if 'application/pdf' not in content_type.lower():
                raise Exception(f"Invalid content type: {content_type}")
                
        except Exception as e:
            raise Exception(f"Failed to download PDF: {str(e)}")

        # Save PDF
        with open(output_path, 'wb') as f:
            f.write(pdf_response.content)
            
        logging.info(f"Successfully downloaded PDF to {output_path}")
        return True
