# AI Chatbot with Inventory Management

A modern, full-stack AI chatbot application with inventory management capabilities, built with React and Python.

## Features

- 🤖 **AI-Powered Chat Interface**
  - Real-time chat with AI assistant
  - Markdown support for formatted responses
  - Typing indicators
  - Message timestamps
  - Conversation history

- 📊 **Analytics Dashboard**
  - Conversation summaries
  - Sentiment analysis
  - Keyword tracking
  - Department categorization
  - Action tracking

- 📦 **Inventory Management**
  - Real-time inventory viewing
  - Car search functionality
  - Detailed vehicle information
  - Filter and sort capabilities

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
- Analytics processing

## Getting Started

### Prerequisites
- Node.js (v14 or higher)
- Python 3.8 or higher
- OpenAI API key

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
│   │   └── App.js
│   └── package.json
└── server/
    ├── app.py
    ├── routes/
    │   └── chat_routes.py
    ├── services/
    │   ├── chat_service.py
    │   └── analytics_service.py
    └── requirements.txt
```

## Features in Detail

### Chat Interface
- Modern, responsive design
- Real-time message updates
- Markdown support for formatted text
- Typing indicators
- Message timestamps
- Conversation history

### Analytics
- Conversation summaries
- Sentiment analysis (positive, neutral, negative)
- Keyword extraction
- Department categorization
- Action item tracking

### Inventory Management
- Real-time inventory updates
- Advanced search capabilities
- Detailed vehicle information
- Filter and sort options

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for their API
- React.js community
- Python Flask community