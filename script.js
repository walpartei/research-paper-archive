document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const downloadBtn = document.getElementById('download-btn');
    const loading = document.getElementById('loading');

    downloadBtn.addEventListener('click', async () => {
        const query = searchInput.value.trim();
        if (!query) {
            alert('Please enter a DOI or paper title');
            return;
        }

        loading.classList.remove('hidden');
        // Backend integration will be added in the next step
        loading.classList.add('hidden');
    });

    // Allow pressing Enter to trigger search
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            downloadBtn.click();
        }
    });
});
