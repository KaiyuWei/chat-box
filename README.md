# Chat Box - AI-Powered Conversation Platform

A modern, full-stack chat application featuring local AI model integration, real-time conversations, and intuitive conversation management.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)

### Build & Run with Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/KaiyuWei/chat-box.git
cd chat-box

# Start the entire application
docker compose up --build

# View server logs, useful for monitoring AI model loading
docker compose logs server -f
```

**⏰ First Startup:** The backend server needs 5-10 minutes to load the AI model on first boot. Look for this message in the logs:

```
INFO - Chat model and processor loaded successfully
```

If you see it, then you're good to go! The frontend is running on http://localhost:3000/

### Alternative: Local Development (Optional)

> **Note**: This project is designed for Docker-first development. Local development setup is provided for reference but may require additional configuration and compatibility adjustments.

#### Backend Setup

```bash
cd server
uv sync  # Install dependencies from lockfile
# You'll need to configure MySQL connection manually
alembic upgrade head  # Apply database migrations
python main.py
```

#### Frontend Setup

```bash
cd client
npm install
npm run dev
```

#### Requirements for Local Development

- MySQL server running locally
- Environment variables configured (see `server/config.py`)
- Potential compatibility issues with AI model dependencies

## 🛠 Technology Stack

### Frontend

- **React 18** - Modern UI framework
- **Tailwind CSS** - Utility-first styling
- **Vite** - Fast development build tool
- **ReactMarkdown** - Rich text rendering for AI responses

### Backend

- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - Database ORM with Alembic migrations
- **MySQL** - Primary database
- **Local AI Model** - Qwen/Qwen3-0.6B (any-to-any model, currently text-to-text only). Chosen for its lower parameter count (0.6B) to enable easier local development and testing. Production deployments can scale up to larger parameter models for enhanced performance

### Infrastructure

- **Docker & Docker Compose** - Containerized deployment
- **Nginx** - Reverse proxy (in production)

## 🗄️ Database Schema Design

The application uses a well-structured relational database schema designed for scalability and conversation management:

### Core Tables

#### **Users Table**

```sql
users (
    id: INTEGER PRIMARY KEY,
    username: VARCHAR(50) UNIQUE,
    email: VARCHAR(100) UNIQUE,
    password_hash: VARCHAR(255),
    created_at: TIMESTAMP,
    updated_at: TIMESTAMP
)
```

_Currently using dummy user (ID: 1) for development. Will be expanded with proper authentication._

#### **Conversations Table**

```sql
conversations (
    id: INTEGER PRIMARY KEY,
    user_id: INTEGER FOREIGN KEY → users.id,
    title: VARCHAR(255),
    prompt: TEXT,
    created_at: TIMESTAMP,
    updated_at: TIMESTAMP
)
```

_Stores conversation metadata and initial prompts for context._

#### **Messages Table**

```sql
messages (
    id: INTEGER PRIMARY KEY,
    conversation_id: INTEGER FOREIGN KEY → conversations.id,
    content: TEXT,
    sent_by: ENUM('user', 'assistant'),
    created_at: TIMESTAMP
)
```

_Stores all chat messages with sender identification._

### Schema Features

- **Referential Integrity**: Foreign key constraints ensure data consistency
- **Soft Deletion Ready**: Schema supports future soft deletion implementation
- **Timestamp Tracking**: All entities track creation and modification times
- **Scalable Design**: Normalized structure supports millions of conversations and messages
- **Migration Support**: Alembic handles schema versioning and updates

### Database Migrations

The project uses **Alembic** for database schema management:

```bash
# View migration history
alembic history

# Apply pending migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

## ✨ Key Features

### 🎯 Core Functionality

- **Real-time Chat Interface** - Smooth messaging experience with typing indicators
- **Continuous Conversations** - AI maintains context across multiple messages within each conversation
- **Conversation Management** - Create, switch, and organize multiple conversations
- **AI Integration** - Local AI model with intelligent responses
- **Persistent Storage** - Conversation history saved across sessions

### 🎨 User Experience

- **Conversation Sidebar** - Easy navigation between chats
- **Visual Feedback** - Loading states, animations, and status indicators
- **localStorage Persistence** - Remembers active conversation across page refreshes

### 🔧 Developer Experience

- **Clean Architecture** - Modular component structure
- **Error Handling** - Helpful error messages for developers
- **Docker Integration** - One-command deployment
- **Database Migrations** - Version-controlled schema changes

## 🎨 Creative Design Choices

### Frontend Architecture

- **Component Modularization**: Extracted reusable components (`ConversationTab`, UI components) for better maintainability
- **State Lifting**: Centralized state management in `ChatPage` component for complex inter-component communication
- **Barrel Exports**: Clean import statements using `index.js` files
- **Error Message Externalization**: Separated error messages into dedicated utility files for better code organization

### User Interface Decisions

- **Conversation Freezing**: When creating new conversations, other tabs become disabled to prevent confusion and ensure focused interaction
- **Visual Feedback**: Animated thinking indicators and status-aware UI components
- **Intuitive Icons**: X buttons for closing temporary conversations, + button for creating new ones

### Backend Design

- **Consistent API Responses**: Standardized array responses even for empty results
- **Startup Event Handling**: Automatic dummy user creation for development
- **Modular Router Structure**: Separated concerns with dedicated routers for different functionalities

### Development Workflow

- **Developer-Friendly Error Messages**: Humorous, informative error messages that guide developers through common issues
- **Hot Reload Support**: Fast development cycle with Vite and FastAPI auto-reload
- **Container-First Approach**: Docker as primary deployment method

## 🚧 Future Improvements

### High Priority

- **Real Authentication System**: Replace dummy user with proper registration/login pages (user creation endpoint already exists, but full auth system implementation is deprioritized to focus on core chat functionality)
- **Delete Conversation Feature**: Button and endpoint for removing unwanted conversations
- **Stop Generation Button**: Allow users to terminate AI response generation mid-process
- **Multi-media Support**: Enable image, audio, and video inputs (leveraging any-to-any model capabilities)

### Performance & Scalability

- **Sliding Window + Running Summary**:
  - Keep only last N messages verbatim (12-30 turns)
  - Maintain running summary of older content
  - Prevent performance issues with large conversations
- **Lazy Loading**: Only load the newest n conversations and the newest n messages in a conversation. There should be "Load more..." pagination for conversations and messages
- **NoSQL Database Migration**: Migrate messages and conversations to MongoDB or similar NoSQL database for better performance with large-scale chat data (flexible schema for different message types, better horizontal scaling, optimized for document-based chat storage patterns)
- **Separate AI Service + Queue System**: Move AI model to dedicated microservice with task queue (Redis/RabbitMQ) for async processing. Currently, the API service blocks during AI model processing, preventing other requests from being handled. A queue system would enable non-blocking request handling and better resource utilization
- **Message Streaming**: Real-time response streaming instead of waiting for complete responses

### User Experience Enhancements

- **Multiple Model Selection**: Add user interface to switch between different AI models (e.g., lightweight models for speed vs. larger models for quality) allowing users to choose the best model for their specific use case
- **Responsive Design**: Optimize UI for different devices including desktop, tablets, and mobile phones with self-adjusting layouts and touch-friendly interfaces
- **Message Layout Redesign**: Move away from left/right bubble layout to a more modern centered approach
- **Turn down token Length Limits**: For local deployments, I limited the response length (can be configured in MAX_NEW_TOKENS in `server/config.js`) for faster response.
- **Thinking Process Visualization**: Stream and display AI reasoning process
- **Enhanced Error Recovery**: Better handling of network failures and errors. Use Toast to display user friendly error messages.

### Code Quality & Testing

- **Comprehensive Test Coverage**: Add more test cases
- **Integration Tests**: Full API testing with FastAPI TestClient
- **Unit Tests**: Isolated testing of core functions with mocking
- **Code Refactoring**: Break down large functions into smaller, focused units following the single responsibility principle. Currently, several functions handle multiple concerns and could be decomposed into specialized sub-functions for improved readability, maintainability, and testability.

### Architecture Evolution

- **Service-Oriented Architecture**:
  - Independent AI service scaling
  - Better resource management
  - Service isolation for reliability
  - Zero-downtime AI model updates

## 📁 Project Structure

```
chat-box/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   │   ├── ChatBox/    # Chat interface components
│   │   │   ├── ChatSideBar/ # Conversation management
│   │   │   └── ui/         # Basic UI primitives
│   │   ├── pages/          # Main page components
│   │   ├── utils/          # Utility functions and constants
│   │   └── styles/         # Global styles
│   └── public/             # Static assets
├── server/                 # FastAPI backend
│   ├── routers/            # API route handlers
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── database/           # Database configuration
│   ├── utils/              # Helper functions
│   └── tests/              # Test files
└── docker-compose.yml      # Container orchestration
```
