import requests
import logging
from typing import Optional, Dict, Any
from urllib.parse import quote

class PaperSearch:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ResearchPaperArchive/1.0 (mailto:walpartei@pm.me)'
        })
        self.crossref_api = "https://api.crossref.org/works"
        
    def search_by_title(self, title: str) -> Optional[str]:
        """
        Search for a paper by title and return the best matching DOI.
        Returns None if no good match is found.
        """
        try:
            # Encode the title for URL
            encoded_title = quote(title)
            
            # Query Crossref API with the title
            params = {
                'query.title': title,
                'rows': 1,  # We only need the best match
                'select': 'DOI,title,score',  # Only get necessary fields
                'sort': 'score'  # Sort by relevance
            }
            
            response = self.session.get(self.crossref_api, params=params)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('message', {}).get('items', [])
            
            if not items:
                logging.info(f"No results found for title: {title}")
                return None
                
            # Get the best match
            best_match = items[0]
            match_score = best_match.get('score', 0)
            
            # Only return if we have a reasonably good match
            if match_score > 50:  # Threshold can be adjusted
                return best_match.get('DOI')
            else:
                logging.info(f"No good matches found for title: {title} (best score: {match_score})")
                return None
                
        except Exception as e:
            logging.error(f"Error searching for paper title: {str(e)}")
            return None
