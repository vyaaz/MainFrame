# MainFrame

Visual prompt engineering for AI coding assistants. Design your app architecture with drag-and-drop components, then generate optimized prompts tailored to your stack and experience level.

## Quick Start

### Backend (FastAPI)

```bash
cd backend
pip3 install -r requirements.txt
python3 main.py
```

The backend will run on http://localhost:8000

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on http://localhost:5173

## Features

- **Component Palette**: Drag 5 different component types onto the canvas:
  - User Input (blue)
  - Logic Block (purple)
  - Context/API (orange)
  - Database (green)
  - Output (yellow)

- **Visual Canvas**: Connect components by dragging between handles to define data flow

- **Smart Analysis**: Click "Generate Prompt" to answer clarifying questions about your project

- **RAG-Enhanced Prompts**: Retrieves relevant best practices from a knowledge base to enhance your prompt

## RAG (Retrieval-Augmented Generation)

MainFrame uses RAG to enhance generated prompts with relevant best practices:

### How It Works

1. **Knowledge Base**: A curated collection of documents about tech stacks, best practices, and architectural patterns (`backend/knowledge_base.py`)

2. **Retrieval**: When you generate a prompt, the system:
   - Extracts node types from your architecture (userInput, database, etc.)
   - Analyzes your component descriptions for keywords
   - Scores each knowledge document based on relevance
   - Returns the top 3 most relevant documents

3. **Augmentation**: The retrieved documents are:
   - Displayed in the UI with relevance scores
   - Injected into the generated prompt as "Best Practices" section

### Knowledge Documents Include:
- React Frontend Best Practices
- API Integration Patterns
- Database Design Principles
- Input Validation & Security
- Authentication & Authorization
- Data Display & Visualization
- Scalability Considerations
- Error Handling Patterns

## Tech Stack

- **Frontend**: React + Vite + TypeScript + ReactFlow + Tailwind CSS
- **Backend**: FastAPI (Python) with RAG pipeline
