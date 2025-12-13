# Physical AI & Humanoid Robotics Textbook

A comprehensive, AI-native textbook for teaching Physical AI and Humanoid Robotics, featuring an integrated RAG (Retrieval-Augmented Generation) chatbot powered by OpenAI GPT-4.

## 🎯 Project Overview

This project fulfills the hackathon requirements by providing:

1. **✅ AI/Spec-Driven Book Creation**: Built with Docusaurus, written using Claude Code and Spec-Kit Plus
2. **✅ Integrated RAG Chatbot**: Full-featured chatbot using OpenAI, FastAPI, Neon Postgres, and Qdrant Cloud
3. **✅ Text Selection Q&A**: Ask questions about any selected text in the book
4. **✅ Persistent Chat History**: Conversation storage across sessions
5. **✅ Semantic Search**: Vector-based search across all chapters

## 📚 Book Content

The textbook covers four comprehensive modules:

### Module 1: The Robotic Nervous System (ROS 2)
- ROS 2 architecture and concepts
- Nodes, topics, services, and actions
- URDF for humanoid robots
- Bridging Python AI agents to ROS controllers

### Module 2: The Digital Twin (Gazebo & Unity)
- Physics simulation with Gazebo
- Photorealistic rendering with Unity
- Sensor simulation (LiDAR, cameras, IMU)
- Bipedal walking simulation

### Module 3: The AI-Robot Brain (NVIDIA Isaac™)
- Isaac Sim for photorealistic simulation
- Isaac ROS for GPU-accelerated perception
- Visual SLAM and navigation
- Reinforcement learning for locomotion

### Module 4: Vision-Language-Action (VLA)
- Voice-to-Action with OpenAI Whisper
- Cognitive planning using LLMs
- Vision-Language models (CLIP)
- Multimodal interaction

## 🚀 Quick Start

### Prerequisites

- **Node.js** 20.0 or higher
- **Python** 3.10+
- **Git**

### Required API Keys

- **OpenAI API Key** (for GPT-4 and embeddings)
- **Qdrant Cloud** account (free tier available)
- **Neon Serverless Postgres** database

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd book

# Install frontend dependencies
cd reusable-book
npm install

# Install backend dependencies
cd ../backend
pip install -r requirements.txt
```

### Configuration

1. **Backend Configuration**:

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your API keys:

```env
OPENAI_API_KEY=sk-...
QDRANT_URL=https://xxxxx.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
DATABASE_URL=postgresql://user:password@host:5432/database
SECRET_KEY=your_secret_key_here
```

2. **Frontend Configuration** (optional):

Create `.env` in `reusable-book/`:

```env
REACT_APP_BACKEND_URL=http://localhost:8000
```

### Running the Application

#### 1. Start the Backend Server

```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

#### 2. Ingest Book Content

```bash
cd backend
python ingest_documents.py
```

This will:
- Read all markdown files from the docs
- Create embeddings using OpenAI
- Store vectors in Qdrant
- Save metadata in Postgres

#### 3. Start the Frontend

```bash
cd reusable-book
npm start
```

The book will be available at `http://localhost:3000`

## 🎨 Features

### RAG Chatbot

The integrated chatbot provides:

- **Contextual Answers**: Retrieves relevant content from the book
- **Source Citations**: Shows which chapters informed the answer
- **Confidence Scores**: Displays relevance confidence
- **Session Persistence**: Maintains conversation history
- **Text Selection Support**: Ask questions about highlighted text

#### Using the Chatbot

1. **General Questions**: Type any question about robotics or AI
2. **Text Selection**: Highlight any text on the page, then ask a question
3. **Chapter-Specific**: Questions automatically filtered by current chapter
4. **Clear Chat**: Reset conversation with the trash icon

### Search Functionality

Semantic search powered by Qdrant:

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how to simulate humanoid robots",
    "top_k": 5
  }'
```

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────┐
│                Docusaurus Frontend                 │
│  ┌──────────────────────────────────────────────┐ │
│  │  • React Components                          │ │
│  │  • MDX Documentation                         │ │
│  │  • Chatbot Widget                            │ │
│  │  • Text Selection Handler                    │ │
│  └──────────────────────────────────────────────┘ │
└─────────────────────┬──────────────────────────────┘
                      │ HTTP/REST API
                      ▼
┌────────────────────────────────────────────────────┐
│              FastAPI Backend                       │
│  ┌──────────────────────────────────────────────┐ │
│  │  RAG Service (GPT-4 + Embeddings)            │ │
│  │  • Query Processing                          │ │
│  │  • Context Building                          │ │
│  │  • Response Generation                       │ │
│  └──────────┬─────────────────┬─────────────────┘ │
│             │                 │                    │
│  ┌──────────▼────────┐  ┌────▼──────────────────┐ │
│  │  Qdrant Service   │  │  PostgreSQL Models    │ │
│  │  • Vector Search  │  │  • Chat Sessions      │ │
│  │  • Embeddings     │  │  • Messages           │ │
│  └───────────────────┘  │  • Documents          │ │
│                         └───────────────────────┘ │
└────────────────────────────────────────────────────┘
         │                        │
         ▼                        ▼
┌──────────────────┐    ┌──────────────────┐
│  Qdrant Cloud    │    │  Neon Postgres   │
│  (Vector DB)     │    │  (Relational DB) │
└──────────────────┘    └──────────────────┘
         │
         ▼
┌──────────────────┐
│   OpenAI API     │
│  • GPT-4         │
│  • Embeddings    │
└──────────────────┘
```

## 📁 Project Structure

```
book/
├── reusable-book/               # Docusaurus frontend
│   ├── docs/                    # Book chapters (markdown)
│   │   ├── 01-introduction.md
│   │   ├── 02-module1-ros2.md
│   │   ├── 03-module2-digital-twin.md
│   │   ├── 04-module3-nvidia-isaac.md
│   │   └── 05-module4-vla.md
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── Chatbot.js       # Main chatbot component
│   │   │   └── ChatWidget.js    # Floating chat widget
│   │   ├── pages/               # Custom pages
│   │   └── css/                 # Styles
│   ├── docusaurus.config.js     # Docusaurus configuration
│   └── package.json
│
└── backend/                     # FastAPI backend
    ├── app/
    │   ├── main.py              # FastAPI application
    │   ├── config.py            # Configuration
    │   ├── database.py          # Database setup
    │   ├── models.py            # SQLAlchemy models
    │   ├── schemas.py           # Pydantic schemas
    │   ├── qdrant_service.py    # Qdrant integration
    │   └── rag_service.py       # RAG logic
    ├── ingest_documents.py      # Document ingestion script
    ├── requirements.txt         # Python dependencies
    ├── .env.example             # Environment template
    └── README.md                # Backend documentation
```

## 🔧 API Endpoints

### Chat Endpoints

- `POST /api/chat` - Send a message to the chatbot
- `GET /api/chat/history/{session_id}` - Get chat history

### Search Endpoints

- `POST /api/search` - Semantic search across the book

### Document Management

- `POST /api/documents/ingest` - Ingest new documents
- `GET /api/documents` - List all documents
- `DELETE /api/documents/chapter/{chapter_id}` - Delete chapter documents

### Utility Endpoints

- `GET /api/chapters/{chapter_id}/summary` - Generate chapter summary
- `GET /health` - Health check

## 🧪 Testing the Chatbot

### Example Questions

Try asking the chatbot:

1. "What is ROS 2?"
2. "How do I simulate a humanoid robot in Gazebo?"
3. "Explain NVIDIA Isaac Sim"
4. "What are Vision-Language-Action models?"
5. Select any code snippet and ask "Explain this code"

### API Testing

```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Physical AI?",
    "session_id": "test-session"
  }'

# Test search
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ROS 2 nodes",
    "top_k": 3
  }'
```

## 🚢 Building for Production

### Build the Frontend

```bash
cd reusable-book
npm run build
```

This creates optimized static files in `build/`.

### Deploy to GitHub Pages

```bash
# Configure in docusaurus.config.js:
# - organizationName: 'your-github-username'
# - projectName: 'your-repo-name'
# - url: 'https://your-username.github.io'
# - baseUrl: '/your-repo-name/'

npm run deploy
```

### Deploy Backend

The backend can be deployed to:
- **Vercel** (with FastAPI adapter)
- **Railway**
- **Render**
- **AWS Lambda** (with Mangum)
- **Any VPS** (with Docker)

## 📊 Database Schema

### Tables

- **users**: User accounts with background info
- **chat_sessions**: Chat conversation sessions
- **chat_messages**: Individual messages
- **documents**: Ingested book content
- **bookmarks**: User bookmarks

## 🎓 Learning Resources

- [Docusaurus Documentation](https://docusaurus.io)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Qdrant Documentation](https://qdrant.tech/documentation)
- [Neon Postgres](https://neon.tech/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built for the Panaversity Hackathon
- Powered by OpenAI GPT-4
- Deployed on Qdrant Cloud and Neon Serverless Postgres
- Created with Claude Code and Spec-Kit Plus

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check the backend README for API documentation
- Review Docusaurus logs for frontend issues

---

**Built with ❤️ for Physical AI & Humanoid Robotics Education**
