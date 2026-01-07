# Crawler Dashboard

A modern web application for managing and monitoring web crawlers. Built with a Python FastAPI backend and React frontend, this dashboard allows you to create, configure, and control multiple web crawlers with real-time monitoring and keyword filtering capabilities.

## Features

- **Multi-Source Crawling**: Support for HTML, RSS, PDF, XML, and plain text sources
- **Real-time Monitoring**: Live stats including crawl rate, pages processed, and runtime
- **Keyword Filtering**: Built-in filters for finance, education, technology, economy, politics, ESG, health, business, and custom exclusion filters
- **Thread Management**: Safe concurrent crawling with proper thread cleanup
- **MongoDB Storage**: Persistent storage for crawled data and crawl runs
- **Modern UI**: Clean, responsive interface built with React and Vite
- **REST API**: Well-documented API endpoints for all operations

## Tech Stack

### Backend
- **Python 3.8+**
- **FastAPI**: High-performance web framework
- **MongoDB**: NoSQL database for data storage
- **BeautifulSoup4**: HTML/XML parsing
- **PyPDF2**: PDF text extraction
- **feedparser**: RSS feed parsing
- **requests**: HTTP client with retry logic

### Frontend
- **React 19**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **Lucide React**: Beautiful icons
- **CSS**: Custom styling with glassmorphism effects

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- MongoDB (local installation or cloud service like MongoDB Atlas)
- Git

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Yassine1nonly/crawler-dashboard.git
   cd crawler-dashboard
   ```

2. **Backend Setup**
   ```bash
   # Navigate to backend directory
   cd backend

   # Create virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install fastapi uvicorn pymongo python-dotenv beautifulsoup4 PyPDF2 feedparser requests

   # Create .env file with your MongoDB configuration
   echo "MONGODB_URI=mongodb://localhost:27017/" > .env
   echo "DATABASE_NAME=webcrawler_lab" >> .env
   ```

3. **Frontend Setup**
   ```bash
   # Navigate to frontend directory
   cd ../frontend

   # Install dependencies
   npm install
   ```

## Running the Application

1. **Start MongoDB**
   Make sure MongoDB is running on your system or update the `MONGODB_URI` in the backend `.env` file.

2. **Start Backend**
   ```bash
   cd backend
   # Activate virtual environment if created
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Start the FastAPI server
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Start Frontend** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```

4. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## API Endpoints

### Sources
- `GET /api/sources` - List all sources with stats
- `POST /api/sources` - Create a new source
- `POST /api/sources/{id}/start` - Start crawling a source
- `POST /api/sources/{id}/stop` - Stop crawling a source
- `GET /api/sources/{id}/stats` - Get detailed stats for a source

### Runs
- `GET /api/runs` - List recent crawl runs

### Health
- `GET /api/health` - Health check endpoint

## Configuration

### Backend Configuration
Edit `backend/app/core/config.py` or set environment variables:

- `MONGODB_URI`: MongoDB connection string
- `DATABASE_NAME`: Database name
- `USER_AGENT`: User agent for HTTP requests
- `TIMEOUT`: Request timeout in seconds
- `MAX_RETRIES`: Maximum retry attempts
- `RETRY_DELAY`: Delay between retries
- `DEFAULT_MAX_HITS`: Default maximum pages to crawl

### Crawler Options
When creating a source, you can configure:

- **URL**: Starting URL for crawling
- **Name**: Display name
- **Source Type**: html, rss, pdf, xml, txt (auto-detected if not specified)
- **Keyword Filter**: Content filtering by category
- **Max Hits**: Maximum number of pages to crawl
- **Request Delay**: Delay between requests in seconds

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt  # If you create one
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Building for Production
```bash
# Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
npm run preview
```

## Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test your changes**
   - Run the backend and frontend
   - Test API endpoints
   - Ensure UI works correctly
5. **Commit your changes**
   ```bash
   git commit -m "Add your descriptive commit message"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**

### Code Style
- **Backend**: Follow PEP 8 for Python code
- **Frontend**: Use ESLint rules (run `npm run lint`)
- **Commits**: Use descriptive commit messages

### Testing
Currently, the project doesn't have automated tests. Contributions adding tests are highly encouraged!

## Project Structure

```
crawler-dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── api/
│   │   │   └── routes.py        # API endpoints
│   │   ├── core/
│   │   │   └── config.py        # Configuration
│   │   ├── db/
│   │   │   └── mongo.py         # MongoDB connection
│   │   └── services/
│   │       ├── content_parser.py    # Content parsing logic
│   │       ├── crawler_engine.py    # Main crawling logic
│   │       ├── keyword_filter.py    # Keyword filtering
│   │       └── runner.py            # Thread management
│   └── requirements.txt         # Python dependencies (create if needed)
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx              # Main React app
│   │   ├── index.css            # Styles
│   │   ├── main.jsx             # React entry point
│   │   └── components/          # React components
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## License

This project is open source. Please check the license file for details.

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/Yassine1nonly/crawler-dashboard/issues) page
2. Create a new issue with detailed information
3. Include error messages, steps to reproduce, and your environment details

## Roadmap

- [ ] Add automated testing
- [ ] Implement user authentication
- [ ] Add more content parsers (JSON, CSV)
- [ ] Implement scheduling for automated crawls
- [ ] Add data export functionality
- [ ] Create Docker configuration
- [ ] Add monitoring and alerting
- [ ] Implement rate limiting
- [ ] Add support for proxy rotation