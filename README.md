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

## Neural Network (Built from Scratch)

MainFrame includes a **custom neural network built entirely from scratch using only NumPy** - no PyTorch, TensorFlow, or any ML framework.

### What It Does

Rates the quality of component descriptions (0-100%):

| Description | Score | Verdict |
|-------------|-------|---------|
| `"login"` | 18% | ❌ Too vague |
| `"user form"` | 23% | ❌ Needs detail |
| `"validate email format"` | 45% | ⚠️ Okay |
| `"user submits email and password through secure login form with validation"` | 89% | ✅ Excellent |

### Architecture

```
Input Layer (208 neurons)
      ↓ weights + bias
Hidden Layer 1 (64 neurons, ReLU)
      ↓ weights + bias
Hidden Layer 2 (32 neurons, ReLU)
      ↓ weights + bias
Output Layer (1 neuron, Sigmoid) → Score 0-1
```

### Implemented From Scratch

All neural network components are manually implemented in `backend/neural_network.py`:

```python
# Forward Pass
Z1 = np.dot(X, W1) + b1      # Matrix multiplication
A1 = np.maximum(0, Z1)        # ReLU activation
output = 1 / (1 + np.exp(-Z3)) # Sigmoid activation

# Backpropagation
dW = (1/m) * np.dot(A.T, dZ)  # Gradient calculation
W -= learning_rate * dW       # Weight update
```

### Key Components

| Component | Implementation |
|-----------|----------------|
| **Forward Propagation** | Matrix multiply + activation functions |
| **Backpropagation** | Chain rule for gradient calculation |
| **Gradient Descent** | Weight updates with learning rate |
| **Loss Function** | Binary cross-entropy |
| **Tokenizer** | Bag-of-words + feature extraction |

### Training

- **Dataset**: 40 labeled examples (description → quality score)
- **Epochs**: 2000 iterations
- **Learning Rate**: 0.05
- **Total Parameters**: ~15,000 weights

### Why Build From Scratch?

Demonstrates understanding of fundamental AI/ML concepts:
- How neural networks learn through backpropagation
- Matrix mathematics behind deep learning
- Gradient descent optimization
- No black-box dependencies

## Tech Stack

- **Frontend**: React + Vite + TypeScript + ReactFlow + Tailwind CSS
- **Backend**: FastAPI (Python) with RAG pipeline
- **AI**: Google Gemini + OpenAI GPT-4o-mini
- **Neural Network**: Custom implementation (NumPy only)
