document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const downloadBtn = document.getElementById('download-btn');
    const loading = document.getElementById('loading');

    async function downloadPaper(query) {
        loading.classList.remove('hidden');
        
        try {
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

            // Create a blob from the PDF stream
            const blob = await response.blob();
            
            // Create a link to download the PDF
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'paper.pdf';
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

    downloadBtn.addEventListener('click', async () => {
        const query = searchInput.value.trim();
        if (!query) {
            alert('Please enter a DOI or paper title');
            return;
        }

        await downloadPaper(query);
    });

    // Allow pressing Enter to trigger search
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            downloadBtn.click();
        }
    });
});
