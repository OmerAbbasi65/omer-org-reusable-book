# Tasks: Integrated RAG Chatbot

**Input**: Design documents from `spec/001-rag-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-spec.yaml

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are minimal (basic validation only).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `src/components/` (React in Docusaurus)
- Paths assume web application structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure: backend/src/{api,services,models,db,config,utils}
- [ ] T002 Create Python virtual environment and install dependencies from spec/001-rag-chatbot/quickstart.md
- [ ] T003 [P] Create backend/.env file with API keys (OpenAI, Qdrant, Neon Postgres connection string)
- [ ] T004 [P] Create backend/requirements.txt with all dependencies listed in research.md
- [ ] T005 [P] Create React component directory structure: src/components/ChatBot/
- [ ] T006 [P] Create backend/scripts/ directory for one-time setup scripts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & Vector Store Setup

- [ ] T007 Initialize Neon Postgres database schema using SQL from spec/001-rag-chatbot/data-model.md (chat_sessions, messages tables)
- [ ] T008 Create Qdrant collection 'book-content' with 1536-dimensional vectors per research.md
- [ ] T009 Create book content ingestion script backend/scripts/ingest_book_content.py (chunk docs/, embed with text-embedding-3-small, upload to Qdrant)
- [ ] T010 Run ingestion script to populate Qdrant with embedded book content (one-time setup)

### Backend Core Infrastructure

- [ ] T011 Implement database connection in backend/src/db/session.py using SQLAlchemy and Neon connection string
- [ ] T012 [P] Create Pydantic models in backend/src/models/chat.py (ChatSessionCreate, ChatSessionResponse, MessageCreate, MessageResponse, ChatRequest, ChatResponse) per data-model.md
- [ ] T013 [P] Create SQLAlchemy models in backend/src/models/database.py (ChatSession, Message) per data-model.md
- [ ] T014 [P] Create configuration management in backend/src/config/settings.py using pydantic-settings for environment variables
- [ ] T015 [P] Implement embedding utility in backend/src/utils/embeddings.py for text-embedding-3-small
- [ ] T016 Create FastAPI app skeleton in backend/src/main.py with CORS configuration per quickstart.md
- [ ] T017 [P] Implement health check endpoint GET /api/health in backend/src/api/health.py per contracts/api-spec.yaml
- [ ] T018 Test backend server startup: python backend/src/main.py and verify http://localhost:8000/api/health returns 200

### Frontend Core Infrastructure

- [ ] T019 Swizzle Docusaurus Root component to enable global ChatBot integration (npm run swizzle @docusaurus/theme-classic Root -- --eject)
- [ ] T020 Create ChatBot component skeleton in src/components/ChatBot/index.tsx
- [ ] T021 [P] Create CSS module in src/components/ChatBot/styles.module.css for chatbot UI styling
- [ ] T022 Integrate ChatBot component into src/theme/Root.tsx to render on all pages
- [ ] T023 Test frontend: npm start and verify chat button appears in bottom-right corner

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Chatbot Interaction (Priority: P1) 🎯 MVP

**Goal**: Enable readers to ask questions and receive accurate answers from book content and general AI knowledge

**Independent Test**: Open chatbot, ask "What is inverse kinematics?", receive accurate answer based on book content; close and reopen chatbot, verify fresh session starts

### Backend Implementation for US1

- [ ] T024 [P] [US1] Implement vector search service in backend/src/services/vector_service.py (query Qdrant with top-k=5 retrieval per research.md)
- [ ] T025 [P] [US1] Implement RAG service in backend/src/services/rag_service.py (retrieve chunks, format context for LLM)
- [ ] T026 [US1] Implement chatbot service in backend/src/services/chatbot_service.py using OpenAI Agents SDK (ChatKit) with RAG context injection
- [ ] T027 [US1] Implement POST /api/chat/sessions endpoint in backend/src/api/chat.py to create new chat sessions per contracts/api-spec.yaml
- [ ] T028 [US1] Implement POST /api/chat/sessions/{session_id}/messages endpoint in backend/src/api/chat.py for sending messages and receiving RAG-augmented responses per contracts/api-spec.yaml
- [ ] T029 [US1] Implement GET /api/chat/sessions/{session_id}/messages endpoint in backend/src/api/chat.py to retrieve message history per contracts/api-spec.yaml
- [ ] T030 [US1] Add error handling for API endpoints (404 for session not found, 429 for rate limits, 500 for errors) per research.md error handling strategy
- [ ] T031 [US1] Test backend flow end-to-end: Create session → Send message → Verify RAG retrieval → Receive answer → Check database persistence

### Frontend Implementation for US1

- [ ] T032 [P] [US1] Create ChatButton component in src/components/ChatBot/ChatButton.tsx (floating button, fixed position bottom-right)
- [ ] T033 [P] [US1] Create ChatPanel component in src/components/ChatBot/ChatPanel.tsx (chat interface with header, message list, input)
- [ ] T034 [P] [US1] Create MessageList component in src/components/ChatBot/MessageList.tsx to display conversation history
- [ ] T035 [P] [US1] Create MessageInput component in src/components/ChatBot/MessageInput.tsx for user input with send button
- [ ] T036 [US1] Implement chat state management hook in src/components/ChatBot/hooks/useChatBot.ts (session creation, message sending, fresh sessions on open)
- [ ] T037 [US1] Connect frontend to backend API in useChatBot.ts hook (fetch calls to http://localhost:8000/api/chat/*)
- [ ] T038 [US1] Implement UI states in ChatPanel component: loading indicator during API calls, error messages for failures
- [ ] T039 [US1] Update ChatBot main component (src/components/ChatBot/index.tsx) to integrate all subcomponents and manage open/close state
- [ ] T040 [US1] Add responsive CSS styles in styles.module.css for desktop, tablet, and mobile (320px-1920px) per spec success criteria SC-008

### US1 Integration & Validation

- [ ] T041 [US1] Test complete US1 flow: Click chat button → Opens panel → Type question → Receive answer → Answer references book content → Close and reopen → New fresh session
- [ ] T042 [US1] Verify response time <5 seconds for typical questions (SC-001)
- [ ] T043 [US1] Test edge cases: very long questions, questions outside book scope, rapid-fire questions
- [ ] T044 [US1] Verify chat button remains visible when scrolling through book pages
- [ ] T045 [US1] Test on mobile device (or browser dev tools) to verify responsive design

**Checkpoint**: At this point, User Story 1 (Basic Chatbot Interaction) should be fully functional and independently testable. This is the MVP!

---

## Phase 4: User Story 2 - Text Selection Q&A (Priority: P2)

**Goal**: Enable readers to select text from the book and ask context-specific questions about their selection

**Independent Test**: Highlight text in book → See "Ask about this" popup → Click popup → Chatbot opens with selected text shown → Ask question about selection → Receive contextual answer

### Frontend Implementation for US2

- [ ] T046 [P] [US2] Create useTextSelection hook in src/components/ChatBot/hooks/useTextSelection.ts using Browser Selection API per research.md
- [ ] T047 [P] [US2] Create TextSelector component in src/components/ChatBot/TextSelector.tsx to display "Ask about this" popup on text selection
- [ ] T048 [US2] Integrate useTextSelection hook in ChatBot main component to detect text selections across all book pages
- [ ] T049 [US2] Update ChatPanel component to display selected text as quoted message when chat opens from text selection
- [ ] T050 [US2] Update useChatBot hook to include selected_text in message metadata when sending to backend
- [ ] T051 [US2] Position "Ask about this" popup near text selection using selection bounding box coordinates
- [ ] T052 [US2] Handle edge cases: very long selections (>5000 chars), selections with special formatting, selections across page navigation

### Backend Implementation for US2

- [ ] T053 [US2] Update RAG service (backend/src/services/rag_service.py) to prioritize selected text in context when provided
- [ ] T054 [US2] Update chatbot service to inject selected text into LLM prompt with special formatting (quoted context)
- [ ] T055 [US2] Store selected_text in message metadata (JSONB column) in Postgres for US2 messages
- [ ] T056 [US2] Update POST /api/chat/sessions/{session_id}/messages to accept and process optional selected_text parameter

### US2 Integration & Validation

- [ ] T057 [US2] Test complete US2 flow: Select text → Click "Ask about this" → Chatbot opens → Selected text visible → Ask question → Receive contextual answer
- [ ] T058 [US2] Test follow-up questions: Ask second question without re-selecting → Verify context is maintained
- [ ] T059 [US2] Test new selection: Select different text → Verify new selection replaces previous context
- [ ] T060 [US2] Verify "Ask about this" popup appears <0.5 seconds after text selection (non-functional requirement)
- [ ] T061 [US2] Test minimum selection length (10 chars) to avoid accidental selections

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Text selection Q&A is fully functional.

---

## Phase 5: User Story 3 - Learning Support Functions (Priority: P3)

**Goal**: Extend chatbot to support active learning with simpler explanations, examples, and concept relationships

**Independent Test**: Ask chatbot to "explain inverse kinematics in simpler terms" → Receive accessible explanation; ask "how does this relate to Chapter 3?" → Receive connections to relevant sections

### Backend Implementation for US3

- [ ] T062 [US3] Enhance chatbot service system prompt in backend/src/services/chatbot_service.py to support learning modes (simpler explanations, examples, conceptual connections)
- [ ] T063 [US3] Update RAG service to retrieve related chapters/sections when user asks about topic relationships
- [ ] T064 [US3] Implement prompt templates for different learning support modes (explain-simpler, provide-examples, show-relationships) in chatbot service
- [ ] T065 [US3] Add detection logic in chatbot service to identify learning support requests (keywords: "simpler", "example", "relate", "how does")

### Frontend Implementation for US3

- [ ] T066 [US3] No specific frontend changes required for US3 (uses existing chat interface)
- [ ] T067 [US3] Optional: Add suggested prompts in ChatPanel (e.g., "Explain this simply", "Give me an example") to guide users

### US3 Integration & Validation

- [ ] T068 [US3] Test simpler explanations: Ask complex concept → Request simpler explanation → Verify accessible response
- [ ] T069 [US3] Test examples: Ask for examples → Verify relevant practical applications provided
- [ ] T070 [US3] Test topic relationships: Ask "How does X relate to Chapter Y?" → Verify connections and references
- [ ] T071 [US3] Test homework assistance: Ask conceptual question → Verify chatbot explains concepts without giving direct answers
- [ ] T072 [US3] Verify all three user stories (US1, US2, US3) work together without conflicts

**Checkpoint**: All user stories should now be independently functional. Complete feature is ready.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

### Performance & Optimization

- [ ] T073 [P] Implement response caching for common questions to improve response times
- [ ] T074 [P] Add request rate limiting to backend API to stay within free tier limits (Qdrant, OpenAI)
- [ ] T075 [P] Optimize Qdrant vector search parameters if response times exceed 500ms
- [ ] T076 [P] Add database connection pooling in backend/src/db/session.py for better concurrency

### Error Handling & User Experience

- [ ] T077 [P] Implement comprehensive error messages for all failure scenarios per research.md (API down, rate limits, no relevant content)
- [ ] T078 [P] Add retry logic for transient errors (network issues, temporary service unavailability)
- [ ] T079 [P] Implement graceful degradation: if Qdrant unavailable, fallback to direct LLM (without RAG)
- [ ] T080 [P] Add telemetry/logging for error tracking and debugging (backend)

### Accessibility & Responsive Design

- [ ] T081 [P] Ensure keyboard navigation works for chatbot (Tab to focus, Enter to send, Esc to close)
- [ ] T082 [P] Verify WCAG AA color contrast standards in styles.module.css
- [ ] T083 [P] Test screen reader compatibility for visually impaired users
- [ ] T084 [P] Final responsive design testing across all breakpoints (320px, 768px, 1024px, 1920px)

### Documentation & Deployment

- [ ] T085 [P] Update spec/001-rag-chatbot/quickstart.md with any lessons learned during implementation
- [ ] T086 [P] Create deployment guide for backend (Render/Railway/Fly.io recommendations)
- [ ] T087 [P] Document environment variable requirements in backend/README.md
- [ ] T088 [P] Create troubleshooting section in quickstart.md based on common development issues

### Final Validation

- [ ] T089 Run complete end-to-end testing: All three user stories work independently and together
- [ ] T090 Verify all success criteria from spec.md are met (SC-001 through SC-008)
- [ ] T091 Load testing: Verify system handles 50+ concurrent users per performance goals
- [ ] T092 Run quickstart.md validation: Fresh developer can set up environment following guide
- [ ] T093 Final code review and cleanup: Remove debug code, unused imports, TODO comments

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion - No dependencies on other stories
- **User Story 2 (Phase 4)**: Depends on Foundational completion - Extends US1 but independently testable
- **User Story 3 (Phase 5)**: Depends on Foundational completion - Extends chatbot service but independently testable
- **Polish (Phase 6)**: Depends on desired user stories being complete (minimum US1 for MVP)

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories ✅ MVP
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 chat interface but is independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Enhances chatbot service but is independently testable

### Within Each User Story

- Backend and Frontend tasks for same story can run in parallel (marked [P])
- Integration & Validation tasks depend on all implementation tasks for that story
- Models/services before API endpoints
- Components before integration
- Implementation before validation

### Parallel Opportunities

**Foundational Phase**:
- T012, T013, T014, T015, T017 can all run in parallel (different files)
- T021 can run in parallel with backend tasks

**User Story 1**:
- T024, T025 can run in parallel
- T032, T033, T034, T035 can all run in parallel (different components)

**User Story 2**:
- T046, T047 can run in parallel

**Polish Phase**:
- T073, T074, T075, T076 (performance tasks) can all run in parallel
- T077, T078, T079, T080 (error handling) can all run in parallel
- T081, T082, T083, T084 (accessibility) can all run in parallel
- T085, T086, T087, T088 (documentation) can all run in parallel

---

## Parallel Example: User Story 1 (Backend)

```bash
# Launch all service layer tasks together:
Task T024: "Implement vector search service in backend/src/services/vector_service.py"
Task T025: "Implement RAG service in backend/src/services/rag_service.py"

# After services complete, API endpoints:
Task T027: "Implement POST /api/chat/sessions endpoint"
Task T028: "Implement POST /api/chat/sessions/{session_id}/messages endpoint"
Task T029: "Implement GET /api/chat/sessions/{session_id}/messages endpoint"
```

## Parallel Example: User Story 1 (Frontend)

```bash
# Launch all React component tasks together:
Task T032: "Create ChatButton component in src/components/ChatBot/ChatButton.tsx"
Task T033: "Create ChatPanel component in src/components/ChatBot/ChatPanel.tsx"
Task T034: "Create MessageList component in src/components/ChatBot/MessageList.tsx"
Task T035: "Create MessageInput component in src/components/ChatBot/MessageInput.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T023) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T024-T045)
4. **STOP and VALIDATE**: Test User Story 1 independently (T041-T045)
5. Deploy/demo basic chatbot - readers can now ask questions and get answers!

**MVP Success**: Readers can click chat button, ask questions, get accurate answers from book content. Fresh sessions on reopen.

### Incremental Delivery

1. **Foundation** (Phases 1-2) → Backend + Frontend infrastructure ready
2. **MVP** (Phase 3 - US1) → Basic Q&A functional → Deploy/Demo ✅
3. **Enhanced** (Phase 4 - US2) → Text selection Q&A → Deploy/Demo ✅
4. **Complete** (Phase 5 - US3) → Learning support → Deploy/Demo ✅
5. **Production-Ready** (Phase 6) → Polish, performance, accessibility → Final Deploy ✅

Each phase adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (Phases 1-2)
2. Once Foundational is done:
   - **Developer A**: User Story 1 backend (T024-T031)
   - **Developer B**: User Story 1 frontend (T032-T040)
   - **Developer C**: Start User Story 2 prep work
3. User Story 1 integrates → Test → Deploy MVP
4. Proceed to User Stories 2 and 3 in parallel or sequentially

---

## Task Summary

**Total Tasks**: 93
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 17 tasks
- Phase 3 (US1 - MVP): 22 tasks
- Phase 4 (US2): 16 tasks
- Phase 5 (US3): 11 tasks
- Phase 6 (Polish): 21 tasks

**Parallel Opportunities**: 45+ tasks marked [P] can run in parallel
**Independent Stories**: All 3 user stories can be developed and tested independently after Foundational phase

**MVP Scope** (Minimum viable product): Phases 1, 2, and 3 (45 tasks) delivers basic chatbot Q&A

**Format Validation**: ✅ All tasks follow required format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label (US1, US2, US3) maps task to specific user story for traceability
- Each user story is independently completable and testable
- Tests are minimal (basic validation only) as not explicitly requested in spec
- Stop at any checkpoint to validate story independently
- Commit after completing each task or logical group
- Backend and frontend can be developed in parallel by different team members
- Focus on MVP (User Story 1) first, then incrementally add US2 and US3
