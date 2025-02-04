document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const downloadBtn = document.getElementById('download-btn');
    const showBtn = document.getElementById('show-btn');
    const loading = document.getElementById('loading');
    const pdfContainer = document.getElementById('pdf-container');
    const pdfPages = document.getElementById('pdf-pages');
    const closeButton = document.getElementById('close-pdf');

    let pdfDoc = null;
    const scale = 1.5;

    async function fetchPaper() {
        const query = searchInput.value.trim();
        if (!query) {
            throw new Error('Please enter a DOI or paper title');
        }

        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query })
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
    
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            downloadPaper();
        }
    });
});
