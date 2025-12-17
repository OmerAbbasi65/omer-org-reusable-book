# Technology Research: RAG Chatbot Implementation

**Feature**: Integrated RAG Chatbot
**Date**: 2025-12-17
**Purpose**: Document technology decisions and research findings for implementation

## 1. OpenAI Agents SDK (ChatKit) vs LangChain

### Decision: Use OpenAI Agents SDK (ChatKit)

**Rationale**:
- User specifically requested OpenAI Agents/ChatKit SDK
- Simpler conversation management with built-in state handling
- Direct integration with OpenAI models
- Lighter weight than full LangChain for our use case

**Implementation Notes**:
- Use ChatKit's Agent class for conversation orchestration
- Inject RAG context via system prompts or context messages
- Handle streaming responses for real-time user experience

**Alternatives Considered**:
- **LangChain**: More comprehensive but heavier; would work but adds complexity
- **Custom implementation**: Too much reinvention; ChatKit handles conversation state well

**References**:
- OpenAI Agents SDK: https://github.com/openai/openai-agents-sdk
- ChatKit documentation: https://platform.openai.com/docs/guides/agents

---

## 2. Qdrant Cloud Configuration

### Decision: Qdrant Cloud Free Tier with 1GB cluster

**Rationale**:
- Free tier sufficient for ~100-200 pages of book content
- Hosted solution eliminates infrastructure management
- Native vector similarity search optimized for RAG
- Simple Python client library

**Configuration**:
- **Collection name**: `book-content`
- **Vector dimensions**: 1536 (OpenAI text-embedding-3-small)
- **Distance metric**: Cosine similarity
- **Payload fields**:
  - `text`: Original chunk text
  - `chapter`: Chapter reference
  - `section`: Section reference
  - `page`: Page/location identifier
  - `chunk_id`: Unique chunk identifier

**Free Tier Limitations**:
- 1GB total storage (sufficient for our content)
- No SLA guarantees (acceptable for educational project)
- Rate limits: adequate for expected traffic

**Alternatives Considered**:
- **Pinecone**: Similar capabilities but Qdrant has better Python support
- **Chroma**: Local-first, would require self-hosting
- **FAISS**: Lower-level, requires more manual management

**References**:
- Qdrant Cloud: https://qdrant.tech/cloud/
- Free tier details: https://qdrant.tech/pricing/

---

## 3. Neon Serverless Postgres Setup

### Decision: Neon Free Tier for chat persistence

**Rationale**:
- Serverless architecture scales to zero (cost-effective)
- PostgreSQL compatibility with SQLAlchemy
- Free tier includes 0.5GB storage (sufficient for chat sessions)
- Automatic backups and branch capabilities

**Schema**:
```sql
-- See data-model.md for complete schema
- chat_sessions table (session_id, created_at, metadata)
- messages table (message_id, session_id, role, content, timestamp)
```

**Connection**:
- Use psycopg2/asyncpg with SQLAlchemy ORM
- Connection pooling via SQLAlchemy
- Async support for FastAPI

**Free Tier Limitations**:
- 0.5GB storage (adequate for thousands of sessions)
- 1 concurrent connection (may need pooling for high traffic)
- Auto-pause after inactivity (acceptable latency tradeoff)

**Alternatives Considered**:
- **Supabase**: Similar offering but Neon has better Python integration
- **PlanetScale**: MySQL-based, prefer PostgreSQL for JSON support
- **SQLite**: Would require file storage management

**References**:
- Neon: https://neon.tech/
- Free tier: https://neon.tech/pricing

---

## 4. Book Content Chunking Strategy

### Decision: Semantic chunking with ~500-token chunks

**Rationale**:
- 500 tokens balances context richness with retrieval precision
- Semantic chunking preserves coherent paragraphs/sections
- Overlap prevents information loss at boundaries

**Chunking Approach**:
1. Parse Docusaurus markdown files
2. Split on natural boundaries (headers, paragraphs)
3. Target 500 tokens per chunk (±100 token variance allowed)
4. 50-token overlap between chunks
5. Preserve metadata (chapter, section, page references)

**Implementation**:
```python
# Use LangChain's RecursiveCharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,  # ~500 tokens * 4 chars/token
    chunk_overlap=200,
    separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    length_function=len
)
```

**Alternatives Considered**:
- **Fixed-size chunks**: Simpler but may split mid-sentence
- **Larger chunks (1000+ tokens)**: More context but less precise retrieval
- **Smaller chunks (200 tokens)**: More precise but loses context

**References**:
- LangChain text splitting: https://python.langchain.com/docs/modules/data_connection/document_transformers/

---

## 5. Embedding Model Selection

### Decision: OpenAI text-embedding-3-small

**Rationale**:
- Cost-effective ($0.02 per 1M tokens)
- 1536 dimensions (good balance)
- High quality semantic understanding
- Consistent with OpenAI LLM usage

**Embedding Strategy**:
- Embed all book chunks during initial setup (one-time cost)
- Embed user questions at query time (minimal cost)
- Store embeddings in Qdrant
- Top-k=5 retrieval (retrieve 5 most relevant chunks per query)

**Cost Estimate**:
- ~200 pages × 500 words/page = 100k words
- ~130k tokens total
- Embedding cost: ~$0.003 (one-time)
- Query embeddings: ~$0.02 per 1000 queries (negligible)

**Alternatives Considered**:
- **text-embedding-3-large**: Higher quality but 3x cost (overkill for our content)
- **Open-source models** (e.g., sentence-transformers): Free but lower quality
- **text-embedding-ada-002**: Older model, prefer newer version

**References**:
- OpenAI embeddings: https://platform.openai.com/docs/guides/embeddings

---

## 6. Docusaurus Component Integration

### Decision: Custom React component with Docusaurus swizzling

**Rationale**:
- Docusaurus supports custom React components
- Use swizzling to modify Root component wrapper
- Maintains Docusaurus hot-reload and build process
- No ejecting required

**Integration Approach**:
1. Create custom React components in `src/components/ChatBot/`
2. Swizzle Docusaurus Root component
3. Wrap app with ChatBot provider/container
4. ChatBot renders globally across all pages

**Implementation**:
```bash
# Swizzle Root component
npm run swizzle @docusaurus/theme-classic Root -- --eject

# Add ChatBot to Root wrapper
import ChatBot from '@site/src/components/ChatBot';

export default function Root({children}) {
  return (
    <>
      {children}
      <ChatBot />
    </>
  );
}
```

**Styling**:
- Use CSS modules for component styles
- Respect Docusaurus theme colors (light/dark mode)
- Ensure z-index above content but below modals

**Alternatives Considered**:
- **Separate SPA**: Would duplicate book content and navigation
- **iframe embedding**: CORS complications and poor UX
- **Browser extension**: Too much friction for users

**References**:
- Docusaurus swizzling: https://docusaurus.io/docs/swizzling
- Custom components: https://docusaurus.io/docs/creating-pages#add-react-components

---

## 7. RAG Retrieval Parameters

### Decision: Top-k=5 with re-ranking

**Rationale**:
- Retrieve 5 most similar chunks from Qdrant
- Balance between context richness and token limits
- Optional re-ranking for precision (if needed)

**Retrieval Flow**:
1. User submits question
2. Embed question with text-embedding-3-small
3. Query Qdrant for top-5 similar chunks (cosine similarity)
4. Concatenate chunks as context
5. Inject into LLM prompt with user question

**Prompt Template**:
```python
system_prompt = """
You are a helpful assistant for the Physical AI & Humanoid Robotics book.
Answer questions using the book content provided below. If the answer isn't
in the book content, you can use your general knowledge about Physical AI
and Humanoid Robotics.

Book Content:
{retrieved_chunks}

If answering from general knowledge, clarify that it's not from the book.
"""

user_prompt = "{user_question}"
```

**Re-ranking** (optional future enhancement):
- Use cross-encoder model to re-rank retrieved chunks
- Only if initial results show poor relevance

**Alternatives Considered**:
- **Top-k=3**: May miss relevant context
- **Top-k=10**: Token limit concerns, slower responses
- **Hybrid search** (keyword + vector): Adds complexity, vector search sufficient

**References**:
- RAG best practices: https://www.anthropic.com/index/building-effective-agents
- Qdrant search: https://qdrant.tech/documentation/concepts/search/

---

## 8. Session Management

### Decision: In-memory session state with database persistence

**Rationale**:
- Fresh sessions on chatbot open (no cross-session history)
- Store messages in database for potential future analytics
- In-memory state during active session for performance
- Session expires on close (client-side cleanup)

**Session Lifecycle**:
1. User opens chatbot → Frontend generates UUID → POST /api/chat/sessions
2. Backend creates session record in Neon Postgres
3. Messages exchanged and stored with session_id
4. User closes chatbot → Frontend discards session (no persistence needed)
5. Database retains history for analytics (optional)

**Session Storage**:
- **Session ID**: UUID v4
- **Created timestamp**: For cleanup/analytics
- **Metadata**: Empty for now (future: user preferences)

**Alternatives Considered**:
- **No database persistence**: Would lose analytics capability
- **JWT tokens**: Unnecessary complexity for stateless sessions
- **Redis cache**: Overkill for simple session management

---

## 9. Text Selection Detection

### Decision: Browser Selection API with React hook

**Rationale**:
- Native browser Selection API is reliable
- React hook encapsulates selection logic
- Debounced to avoid flickering on selection changes
- Works across all modern browsers

**Implementation**:
```typescript
// useTextSelection.ts
const useTextSelection = () => {
  const [selectedText, setSelectedText] = useState('');
  const [selectionPosition, setSelectionPosition] = useState(null);

  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim();

      if (text && text.length > 10) {
        setSelectedText(text);
        // Get selection bounding box for popup positioning
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        setSelectionPosition({x: rect.x, y: rect.bottom});
      } else {
        setSelectedText('');
        setSelectionPosition(null);
      }
    };

    document.addEventListener('selectionchange', handleSelection);
    return () => document.removeEventListener('selectionchange', handleSelection);
  }, []);

  return { selectedText, selectionPosition };
};
```

**UX Flow**:
1. User selects text (min 10 characters to avoid accidental selections)
2. "Ask about this" popup appears near selection
3. User clicks popup → Chatbot opens with selected text pre-filled
4. Selected text displayed as quoted message in chat

**Alternatives Considered**:
- **Keyboard shortcuts**: Less discoverable
- **Context menu**: Browser restrictions make this difficult
- **Tooltip on hover**: Conflicts with natural reading flow

**References**:
- Selection API: https://developer.mozilla.org/en-US/docs/Web/API/Selection

---

## 10. Error Handling & Fallbacks

### Decision: Graceful degradation with user-friendly messages

**Rationale**:
- Network errors, API failures, and rate limits should not break UX
- Provide helpful error messages guiding users
- Log errors for debugging but don't expose internals

**Error Scenarios**:
1. **API endpoint down**: "Chatbot is temporarily unavailable. Please try again later."
2. **Rate limit exceeded**: "Too many requests. Please wait a moment and try again."
3. **No relevant content found**: "I couldn't find information about this in the book, but I can provide general knowledge..."
4. **Embedding service down**: Fallback to keyword search or direct LLM (without RAG)
5. **Database connection lost**: Session creation fails gracefully, show error to user

**Implementation**:
```python
# Backend error handling
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An error occurred. Please try again."}
    )

# Frontend error handling
const handleError = (error) => {
  if (error.response?.status === 429) {
    setErrorMessage("Too many requests. Please wait a moment.");
  } else if (error.response?.status === 503) {
    setErrorMessage("Chatbot is temporarily unavailable.");
  } else {
    setErrorMessage("An error occurred. Please refresh and try again.");
  }
};
```

**Alternatives Considered**:
- **Retry logic**: Could implement automatic retries for transient errors
- **Offline mode**: Complex for RAG system, not feasible
- **Queue system**: Overkill for expected traffic

---

## Summary of Decisions

| Component | Decision | Key Rationale |
|-----------|----------|---------------|
| Conversation SDK | OpenAI Agents SDK (ChatKit) | User requirement, simple state management |
| Vector Store | Qdrant Cloud (free tier) | Managed service, sufficient free tier |
| Database | Neon Serverless Postgres | Serverless, PostgreSQL compatibility |
| Chunking | 500-token semantic chunks | Balances context and precision |
| Embeddings | text-embedding-3-small | Cost-effective, high quality |
| Frontend Integration | Docusaurus swizzling | Native React, no ejecting |
| Retrieval | Top-k=5 | Sufficient context, manageable tokens |
| Session Management | In-memory + DB persistence | Performance + analytics |
| Text Selection | Browser Selection API | Native, reliable |
| Error Handling | Graceful degradation | User-friendly, maintainable |

All technology decisions align with free tier requirements and educational book context.
