# Veteran Claims Agent

A comprehensive AI-powered application designed to assist veterans with their claims process. This application provides a chat interface for veterans to interact with an AI assistant and includes an analytics dashboard to track usage and performance metrics.

## Features

### AI-Powered Chat Interface
- Real-time chat with AI assistant
- Markdown support for formatted responses
- Typing indicators
- Message timestamps
- Conversation history

### Analytics Dashboard
- Real-time cost tracking
- Token usage monitoring
- Request history
- Model performance metrics
- CSV report generation
- Data reset capabilities

## Tech Stack

### Frontend
- React.js (v19)
- CSS3 with CSS Variables
- Modern UI/UX design
- Responsive layout
- Axios for API requests
- React Router for navigation
- React Markdown for formatted text

### Backend
- Python 3.8+
- Flask web framework
- OpenAI API integration
- PostgreSQL for data persistence
- SQLAlchemy ORM
- Gunicorn for production deployment

## Prerequisites

- Node.js (v14 or higher)
- Python 3.8 or higher
- OpenAI API key
- PostgreSQL database
- Docker (optional, for local development)

## Getting Started

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Veteran_Claims_Agent
   ```

2. Copy and configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Then update `.env` with your settings:
   ```properties
   OPENAI_API_KEY=your_api_key
   POSTGRES_USER=admin
   POSTGRES_PASSWORD=your_password
   POSTGRES_HOST=your_db
   POSTGRES_PORT=5432
   POSTGRES_DB=your_db
   CORS_ORIGINS=http://localhost:8080
   REACT_APP_API_URL=http://localhost:5000/api
   ```

3. (Optional) Install local dependencies:
   ```bash
   cd client && npm install
   cd ../server && pip install -r requirements.txt
   ```

### Running with Docker

Build and start all services:
```bash
docker-compose up --build
```

- Frontend: http://localhost:8080
- Backend API: http://localhost:5000/api

### Running Locally Without Docker

1. Ensure PostgreSQL is running locally and the `agents` database exists.
2. Create tables from your models:
   ```bash
   cd server
   python -c "from create_app import create_app; from database import db; app = create_app(); with app.app_context(): db.create_all()"
   ```
3. Start backend:
   ```bash
   flask run
   ```
4. Start frontend:
   ```bash
   cd client && npm start
   ```

## Project Structure

```
├── client/                  # Frontend React application
│   ├── public/              # Static files
│   └── src/                 # Source files
│       ├── components/      # React components
│       │   ├── Analytics/   # Analytics dashboard components
│       │   ├── Chat/        # Chat interface components
│       │   └── Inventory/   # Inventory display components
│       ├── context/         # React context providers
│       ├── utils/           # Utility functions
│       └── App.js           # Main application component
└── server/                  # Backend Flask application
    ├── database/            # Database configuration
    ├── helpers/             # Helper functions
    ├── models/              # SQLAlchemy models
    ├── routes/              # API routes
    ├── services/            # Business logic
    ├── app.py               # Main application file
    ├── config.py            # Configuration settings
    └── requirements.txt     # Python dependencies
```

## Configuration

### Database Setup

The application uses PostgreSQL for data persistence. You can set up a local database using Docker:

```bash
docker run --name postgres-db -e POSTGRES_PASSWORD=your_password -e POSTGRES_USER=your_user -e POSTGRES_DB=your_db -p 5432:5432 -d postgres
```

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Secret key for session management
- `CORS_ORIGINS`: Allowed CORS origins

## 🔍 Troubleshooting

### Database Connection Issues

If you're experiencing database connection issues:

1. Check that your PostgreSQL server is running
2. Verify your database credentials in the `.env` file
3. Ensure the database exists and is accessible

### API Connection Issues

If the frontend can't connect to the backend:

1. Check that both servers are running
2. Verify the CORS settings in the backend
3. Check the network tab in your browser's developer tools

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for their API
- React.js community
- Python Flask community
- PostgreSQL community
