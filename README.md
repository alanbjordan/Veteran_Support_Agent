# AI Chatbot Optimization Template with Analytics Dashboard

This repository provides a template designed to help developers build and optimize AI-powered chatbots. The integrated analytics dashboard offers insights into user interactions and chatbot performance, enabling continuous improvement and fine-tuning of chatbot operations. Use this template as a starting point to accelerate development, deploy robust solutions, and leverage data-driven optimizations for your chatbot projects.

## ⚠️ Important Note
You must create an external PostgreSQL database for the analytics information. The application uses SQLAlchemy with PostgreSQL for data persistence.

## Features

### 🤖 AI-Powered Chat Interface
- Real-time chat with AI assistant
- Markdown support for formatted responses
- Typing indicators
- Message timestamps
- Conversation history

### 📊 Analytics Dashboard
- Real-time cost tracking
- Token usage monitoring
- Request history
- Model performance metrics
- CSV report generation
- Data reset capabilities

## Tech Stack

### Frontend
- React.js
- CSS3 with CSS Variables
- Modern UI/UX design
- Responsive layout

### Backend
- Python
- Flask
- OpenAI API integration
- PostgreSQL for Analytics processing
- SQLAlchemy ORM

## Getting Started

### Prerequisites
- Node.js (v14 or higher)
- Python 3.8 or higher
- OpenAI API key
- PostgreSQL database

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [project-directory]
```

2. Install frontend dependencies:
```bash
cd client
npm install
```

3. Install backend dependencies:
```bash
cd server
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the server directory with:
```
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
SECRET_KEY=your_secret_key_here
CORS_ORIGINS=http://localhost:3000
```

### Running the Application

1. Start the backend server:
```bash
cd server
python app.py
```

2. Start the frontend development server:
```bash
cd client
npm start
```

The application will be available at `http://localhost:3000`

## Project Structure

```
├── client/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   │   ├── Chat.jsx
│   │   │   │   ├── Chat.css
│   │   │   │   ├── Message.jsx
│   │   │   │   ├── ChatInput.jsx
│   │   │   │   └── InventoryDisplay.jsx
│   │   │   └── Analytics/
│   │   │       ├── index.jsx
│   │   │       ├── Analytics.css
│   │   │       ├── AnalyticsCard.jsx
│   │   │       ├── AnalyticsSummary.jsx
│   │   │       └── AnalyticsTable.jsx
│   │   └── App.js
│   └── package.json
└── server/
    ├── app.py
    ├── config.py
    ├── database/
    │   └── session.py
    ├── models/
    │   └── sql_models.py
    ├── routes/
    │   ├── chat_routes.py
    │   ├── analytics_routes.py
    │   └── all_routes.py
    ├── services/
    │   ├── chat_service.py
    │   └── analytics_service.py
    └── requirements.txt
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for their API
- React.js community
- Python Flask community
- PostgreSQL community
