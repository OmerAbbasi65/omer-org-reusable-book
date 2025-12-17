# Implementation Plan: Integrated RAG Chatbot

**Branch**: `001-rag-chatbot` | **Date**: 2025-12-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `spec/001-rag-chatbot/spec.md`

## Summary

Build a Retrieval-Augmented Generation (RAG) chatbot embedded in the Docusaurus-based Physical AI & Humanoid Robotics book. The system combines semantic search over book content with general AI knowledge to answer reader questions. Key features include a floating chat interface, text selection Q&A, and contextual learning support.

**Technical Approach**:
- Backend: FastAPI with OpenAI Agents SDK (ChatKit) for conversation management
- Vector Store: Qdrant Cloud (free tier) for semantic search of book content
- Database: Neon Serverless Postgres for session/message persistence
- Frontend: React components integrated into existing Docusaurus site
- RAG Pipeline: Embed book content → Store in Qdrant → Retrieve relevant chunks → Augment LLM prompts

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/JavaScript (frontend)
**Primary Dependencies**:
- Backend: FastAPI, OpenAI Agents SDK, Qdrant Client, Neon Postgres client, LangChain/LlamaIndex (for RAG orchestration)
- Frontend: React 18+, Docusaurus 3.x, TailwindCSS or styled-components
**Storage**:
- Neon Serverless Postgres (chat sessions, messages, user context)
- Qdrant Cloud Free Tier (vector embeddings of book content)
**Testing**: pytest (backend), Jest + React Testing Library (frontend)
**Target Platform**: Web (hosted backend API + integrated frontend in Docusaurus)
**Project Type**: Web application (backend API + frontend integration)
**Performance Goals**:
- <5 second response time for 90% of queries
- Support 50+ concurrent users
- Vector search < 500ms
**Constraints**:
- Must use free tiers (Qdrant Cloud free, Neon free tier)
- Integrate seamlessly with existing Docusaurus book
- No persistent chat history across sessions
**Scale/Scope**:
- ~100-200 pages of book content to embed
- Expected 10-100 concurrent readers
- ~1000 vector chunks from book

## Constitution Check

*Note: Constitution template is not yet filled in for this project. Proceeding with industry best practices.*

**Assumed Principles**:
- ✅ Simple, maintainable architecture
- ✅ Clear separation of concerns (backend API / frontend UI)
- ✅ Use managed services where possible (Neon, Qdrant Cloud)
- ✅ Test core functionality
- ✅ Document setup and deployment

## Project Structure

### Documentation (this feature)

```text
spec/001-rag-chatbot/
├── plan.md              # This file
├── research.md          # Technology decisions and research
├── data-model.md        # Database schema and entities
├── quickstart.md        # Setup and development guide
├── contracts/           # API specifications
│   └── api-spec.yaml   # OpenAPI specification
└── tasks.md             # Task breakdown (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py                 # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py            # Chat endpoints
│   │   └── health.py          # Health check endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chatbot_service.py # Chatbot logic (OpenAI Agents SDK)
│   │   ├── rag_service.py     # RAG retrieval logic
│   │   └── vector_service.py  # Qdrant vector operations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat.py            # Pydantic models for chat
│   │   └── database.py        # SQLAlchemy models
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py         # Database connection
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py        # Environment config
│   └── utils/
│       ├── __init__.py
│       └── embeddings.py      # Text embedding utilities
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── scripts/
│   └── ingest_book_content.py # One-time script to embed book
├── requirements.txt
├── .env.example
└── README.md

src/components/
├── ChatBot/
│   ├── ChatBot.tsx            # Main chatbot component
│   ├── ChatButton.tsx         # Floating chat button
│   ├── ChatPanel.tsx          # Chat interface panel
│   ├── MessageList.tsx        # Message display
│   ├── MessageInput.tsx       # User input field
│   ├── TextSelector.tsx       # Text selection handler
│   └── styles.module.css      # Component styles
└── hooks/
    ├── useChatBot.ts          # Chat state management
    └── useTextSelection.ts    # Text selection detection

docs/
├── [existing docusaurus content]
└── [chatbot will be added to layout]
```

**Structure Decision**: Web application with separate backend (FastAPI API) and frontend (React components in Docusaurus). Backend handles all AI/RAG logic, frontend provides UI integration. This separation allows independent development and testing of each layer.

## Complexity Tracking

*No constitutional violations to justify - using straightforward web app architecture*

## Phase 0: Research & Technology Decisions

**See**: [research.md](./research.md) for detailed technology research and decisions.

Key research areas:
1. OpenAI Agents SDK vs custom LangChain implementation
2. Qdrant Cloud setup and free tier limitations
3. Neon Serverless Postgres configuration
4. Book content chunking strategies for RAG
5. Embedding model selection (OpenAI vs open-source)
6. Docusaurus custom component integration patterns

## Phase 1: Design & Contracts

### Data Model

**See**: [data-model.md](./data-model.md) for complete database schema.

**Key Entities**:
- ChatSession: Represents a single conversation
- Message: Individual messages within a session
- BookChunk: Metadata for embedded book content (stored alongside vectors in Qdrant)

### API Contracts

**See**: [contracts/api-spec.yaml](./contracts/api-spec.yaml) for OpenAPI specification.

**Key Endpoints**:
- `POST /api/chat/sessions` - Create new chat session
- `POST /api/chat/sessions/{session_id}/messages` - Send message
- `GET /api/chat/sessions/{session_id}/messages` - Get message history
- `GET /api/health` - Health check

### Quick Start

**See**: [quickstart.md](./quickstart.md) for setup instructions.

## Implementation Approach

### Backend Implementation (Priority: P1)

1. **Setup FastAPI project structure**
   - Initialize FastAPI app with CORS for Docusaurus integration
   - Configure environment variables for API keys (OpenAI, Qdrant, Neon)
   - Set up database connection to Neon Postgres

2. **Implement RAG pipeline**
   - Create script to chunk and embed book content
   - Upload embeddings to Qdrant Cloud
   - Implement retrieval service to query relevant chunks

3. **Integrate OpenAI Agents SDK**
   - Configure ChatKit agent with system prompts
   - Implement RAG context injection into prompts
   - Handle streaming responses for real-time feel

4. **Build API endpoints**
   - Session creation endpoint
   - Message sending/receiving with RAG
   - Session history retrieval

### Frontend Implementation (Priority: P1)

1. **Create React chatbot components**
   - Floating chat button (fixed position)
   - Chat panel with message list
   - Message input with loading states
   - Text selection popup ("Ask about this")

2. **Implement state management**
   - Chat session state (fresh on open)
   - Message history for current session
   - Selected text context

3. **Integrate with Docusaurus**
   - Add chatbot to Docusaurus layout wrapper
   - Configure API endpoint connections
   - Style for consistency with book theme

### Text Selection Feature (Priority: P2)

1. **Implement text selection detection**
   - Browser selection API integration
   - Show "Ask about this" prompt on selection
   - Capture selected text and metadata

2. **Context injection**
   - Include selected text in API requests
   - Display selected text in chat UI
   - Maintain context for follow-ups

### Testing & Validation (Priority: P3)

1. **Backend tests**
   - Unit tests for RAG retrieval accuracy
   - Integration tests for chat flow
   - API endpoint tests

2. **Frontend tests**
   - Component rendering tests
   - User interaction tests
   - Text selection handling tests

3. **End-to-end validation**
   - Test complete chat flows
   - Verify answer accuracy against book content
   - Performance testing (response times)

## Deployment Considerations

- **Backend**: Deploy FastAPI to cloud platform (e.g., Render, Railway, Fly.io free tiers)
- **Frontend**: Already deployed with Docusaurus site (no separate deployment needed)
- **Environment Variables**: Secure storage for API keys (OpenAI, Qdrant, Neon)
- **CORS**: Configure for Docusaurus domain
- **Rate Limiting**: Implement to stay within free tier limits

## Success Criteria Mapping

| Success Criterion | Implementation Strategy |
|------------------|------------------------|
| SC-001: <5s response time | - Use streaming responses<br>- Optimize vector search<br>- Cache common queries |
| SC-002: 85% accuracy | - Careful book chunking<br>- Relevant chunk retrieval (top-k=5)<br>- Quality LLM prompts |
| SC-003: 80% task completion | - Clear UI/UX<br>- Helpful error messages<br>- Loading indicators |
| SC-004: 60% engagement | - Visible, accessible chat button<br>- Quick response times<br>- Useful answers |
| SC-005: 30% text selection use | - Obvious "Ask about this" prompt<br>- Smooth UX for selection<br>- Contextual answers |
| SC-006: 4+ satisfaction | - Accurate answers<br>- Fast responses<br>- Intuitive interface |
| SC-007: 40% reduced confusion | - Accurate book content retrieval<br>- Clear explanations<br>- Related topic suggestions |
| SC-008: Responsive design | - Mobile-first CSS<br>- Test on 320px-1920px<br>- Touch-friendly UI |

## Open Questions

*All technical questions will be addressed in research.md*

## Next Steps

1. Complete research.md with technology decisions
2. Create data-model.md with database schema
3. Generate API contracts in contracts/
4. Write quickstart.md for developer onboarding
5. Run `/sp.tasks` to generate implementation task breakdown
