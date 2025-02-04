document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchType = document.getElementById('search-type');
    const downloadBtn = document.getElementById('download-btn');
    const showBtn = document.getElementById('show-btn');
    const loading = document.getElementById('loading');
    const pdfContainer = document.getElementById('pdf-container');
    const pdfPages = document.getElementById('pdf-pages');
    const closeButton = document.getElementById('close-pdf');

    // Update placeholder based on search type
    function updatePlaceholder() {
        const type = searchType.value;
        switch (type) {
            case 'doi':
                searchInput.placeholder = 'Enter DOI (e.g., 10.1234/example)';
                break;
            case 'pmid':
                searchInput.placeholder = 'Enter PMID (e.g., 19346325)';
                break;
            case 'title':
                searchInput.placeholder = 'Enter paper title';
                break;
        }
    }

    // Set initial placeholder
    updatePlaceholder();

    let pdfDoc = null;
    const scale = 1.5;

    function normalizeDoi(input) {
        // Remove any whitespace
        let doi = input.trim();
        
        // Remove various DOI prefixes
        doi = doi.replace(/^(?:doi:|DOI:)/i, '');
        
        // Remove URL prefixes
        doi = doi.replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, '');
        
        return doi;
    }

    async function fetchPaper() {
        const query = searchInput.value.trim();
        const type = searchType.value;
        
        if (!query) {
            throw new Error(`Please enter a ${type.toUpperCase()}`);
        }

        // Normalize DOI if it's a DOI search
        const normalizedQuery = type === 'doi' && query.match(/\b(10\.\d{4,}\/.+)\b/) 
            ? normalizeDoi(query)
            : query;

        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                query: normalizedQuery,
                type: searchType.value
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to download paper');
        }

        return response;
    }

    async function downloadPaper() {
        loading.classList.remove('hidden');

        try {
            const response = await fetchPaper();
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `${searchInput.value.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`;
            document.body.appendChild(a);
            a.click();
            
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch (error) {
            alert(error.message);
        } finally {
            loading.classList.add('hidden');
        }
    }

    async function showPaper() {
        loading.classList.remove('hidden');

        try {
            const response = await fetchPaper();
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            // Load PDF using PDF.js
            pdfDoc = await pdfjsLib.getDocument(url).promise;
            
            // Clear previous pages
            pdfPages.innerHTML = '';
            
            // Show PDF container
            pdfContainer.classList.remove('hidden');
            
            // Render all pages
            for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
                await renderPage(pageNum);
            }

            window.URL.revokeObjectURL(url);

        } catch (error) {
            alert(error.message);
        } finally {
            loading.classList.add('hidden');
        }
    }

    async function renderPage(pageNum) {
        try {
            const page = await pdfDoc.getPage(pageNum);
            const viewport = page.getViewport({ scale });

            // Create page container
            const pageContainer = document.createElement('div');
            pageContainer.className = 'pdf-page';
            
            // Create canvas
            const canvas = document.createElement('canvas');
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            // Add page number
            const pageLabel = document.createElement('div');
            pageLabel.className = 'page-number';
            pageLabel.textContent = `Page ${pageNum} of ${pdfDoc.numPages}`;

            // Add to container
            pageContainer.appendChild(canvas);
            pageContainer.appendChild(pageLabel);
            pdfPages.appendChild(pageContainer);

            const renderContext = {
                canvasContext: canvas.getContext('2d'),
                viewport: viewport
            };

            await page.render(renderContext).promise;

        } catch (error) {
            console.error(`Error rendering page ${pageNum}:`, error);
            const errorDiv = document.createElement('div');
            errorDiv.className = 'pdf-page error';
            errorDiv.textContent = `Error loading page ${pageNum}`;
            pdfPages.appendChild(errorDiv);
        }
    }

    function closePdfViewer() {
        pdfContainer.classList.add('hidden');
        pdfPages.innerHTML = '';
        pdfDoc = null;
    }

    // Event Listeners
    downloadBtn.addEventListener('click', downloadPaper);
    showBtn.addEventListener('click', showPaper);
    closeButton.addEventListener('click', closePdfViewer);
    searchType.addEventListener('change', updatePlaceholder);
    
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            downloadPaper();
        }
    });
});
