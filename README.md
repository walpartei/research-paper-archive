# Research Paper Archive

A modern web application for accessing and viewing research papers using DOI or title. Built with FastAPI backend and vanilla JavaScript frontend, featuring a built-in PDF viewer.

## Features

- 🔍 Search papers by DOI or title
- 📥 Direct PDF download
- 👀 Built-in PDF viewer with continuous scroll
- 📱 Responsive design for all devices
- ⚡ Fast and reliable with multiple mirror support
- 🚀 Easy deployment to Vercel

## Live Demo

Visit [your-app-name.vercel.app](https://your-app-name.vercel.app) to try it out!

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js and npm (for Vercel CLI)
- Git
- [Vercel account](https://vercel.com/signup) (for deployment)

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/research-paper-archive.git
   cd research-paper-archive
   ```

2. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r api/requirements.txt
   ```

4. Run the development server:
   ```bash
   uvicorn backend.main:app --reload
   ```

5. Open `index.html` in your browser or use a local server:
   ```bash
   python -m http.server 8000
   ```

   Visit `http://localhost:8000` in your browser.

### Project Structure

```
├── api/                  # Vercel serverless functions
│   ├── download.py       # PDF download endpoint
│   ├── mirrors.py        # Mirror status endpoint
│   └── requirements.txt  # Python dependencies
├── backend/              # FastAPI backend
│   ├── main.py          # Main FastAPI application
│   └── scihub_wrapper.py # SciHub integration
├── index.html           # Frontend entry point
├── styles.css           # Styles
├── script.js            # Frontend JavaScript
└── vercel.json          # Vercel configuration
```

## Deployment to Vercel

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy to Vercel:
   ```bash
   vercel
   ```

   Follow the prompts to configure your deployment.

4. For production deployment:
   ```bash
   vercel --prod
   ```

### Environment Variables

No environment variables are required for basic functionality.

## Usage

1. Enter a DOI (e.g., `10.1234/example.doi`) or paper title in the search box
2. Choose an action:
   - Click "Download PDF" to save the paper to your device
   - Click "Show PDF" to view the paper in the built-in viewer
3. For the viewer:
   - Scroll through pages naturally
   - Use the close button to exit the viewer

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [PDF.js](https://mozilla.github.io/pdf.js/) for PDF rendering
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Vercel](https://vercel.com/) for hosting and serverless functions

## Support

If you find this project helpful, please give it a ⭐️ on GitHub and [Paypal me](https://paypal.me/jeremias)!
