document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const downloadBtn = document.getElementById('download-btn');
    const showBtn = document.getElementById('show-btn');
    const loading = document.getElementById('loading');
    const pdfContainer = document.getElementById('pdf-container');
    const pdfCanvas = document.getElementById('pdf-canvas');
    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');
    const closeButton = document.getElementById('close-pdf');
    const pageNum = document.getElementById('page-num');
    const pageCount = document.getElementById('page-count');

    let pdfDoc = null;
    let pageNum_ = 1;
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
            pageCount.textContent = pdfDoc.numPages;
            
            // Show PDF container and render first page
            pdfContainer.classList.remove('hidden');
            renderPage(1);

            window.URL.revokeObjectURL(url);

        } catch (error) {
            alert(error.message);
        } finally {
            loading.classList.add('hidden');
        }
    }

    async function renderPage(num) {
        if (!pdfDoc || num < 1 || num > pdfDoc.numPages) return;

        pageNum_ = num;
        pageNum.textContent = pageNum_;

        try {
            const page = await pdfDoc.getPage(pageNum_);
            const viewport = page.getViewport({ scale });

            // Set canvas dimensions
            pdfCanvas.height = viewport.height;
            pdfCanvas.width = viewport.width;

            const renderContext = {
                canvasContext: pdfCanvas.getContext('2d'),
                viewport: viewport
            };

            await page.render(renderContext).promise;

            // Update button states
            prevButton.disabled = pageNum_ <= 1;
            nextButton.disabled = pageNum_ >= pdfDoc.numPages;

        } catch (error) {
            console.error('Error rendering PDF page:', error);
            alert('Error rendering PDF page');
        }
    }

    function closePdfViewer() {
        pdfContainer.classList.add('hidden');
        pdfDoc = null;
        pageNum_ = 1;
    }

    // Event Listeners
    downloadBtn.addEventListener('click', downloadPaper);
    showBtn.addEventListener('click', showPaper);
    prevButton.addEventListener('click', () => renderPage(pageNum_ - 1));
    nextButton.addEventListener('click', () => renderPage(pageNum_ + 1));
    closeButton.addEventListener('click', closePdfViewer);
    
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            downloadPaper();
        }
    });
});
