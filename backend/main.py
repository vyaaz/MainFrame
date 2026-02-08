from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from models import (
    AnalyzeRequest,
    AnalyzeResponse,
    GenerateRequest,
    GenerateResponse,
    AddUrlRequest,
    KnowledgeDocument,
)
from prompt_generator import get_questions, generate_prompt
from knowledge_base import (
    retrieve_relevant_docs,
    enhance_prompt_with_context,
    add_document_from_url,
    get_all_documents,
    remove_document,
)
from ai_generator import generate_ai_prompt, generate_stack_reasoning_ai
from neural_network import get_scorer

app = FastAPI(
    title="MainFrame API",
    description="API for analyzing app architecture and generating AI prompts with RAG + GPT",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    """Pre-train the neural network on startup"""
    print("\n" + "="*50)
    print("INITIALIZING NEURAL NETWORK...")
    print("="*50)
    get_scorer()  # This trains the model
    print("="*50)
    print("NEURAL NETWORK READY!")
    print("="*50 + "\n")

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "MainFrame API is running", "features": ["RAG", "GPT-4o-mini"]}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Analyze the graph structure and return clarifying questions.
    """
    questions = get_questions()
    return AnalyzeResponse(questions=questions)


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    Generate an optimized prompt using:
    1. RAG retrieval for relevant best practices
    2. GPT-4o-mini for polished prompt generation
    """
    print("\n" + "="*50)
    print("GENERATE ENDPOINT CALLED")
    print("="*50)

    # Extract node types and descriptions for RAG retrieval (exclude notes)
    node_types = [node.type for node in request.nodes if node.type != "notes"]
    descriptions = [node.description for node in request.nodes if node.description and node.type != "notes"]

    print(f"Extracted node types: {node_types}")
    print(f"Extracted descriptions: {descriptions}")

    # RAG: Retrieve relevant documents from knowledge base
    retrieved_docs = retrieve_relevant_docs(
        node_types=node_types,
        descriptions=descriptions,
        top_k=3
    )

    print(f"RAG retrieved {len(retrieved_docs)} documents")

    # Generate base prompt (for tech stack extraction)
    base_result = generate_prompt(
        nodes=request.nodes,
        edges=request.edges,
        answers=request.answers,
    )

    # Prepare node/edge data for AI
    nodes_data = [{"id": n.id, "type": n.type, "description": n.description} for n in request.nodes]
    edges_data = [{"source": e.source, "target": e.target} for e in request.edges]

    # Try AI-powered generation
    ai_prompt = generate_ai_prompt(
        nodes=nodes_data,
        edges=edges_data,
        answers=request.answers,
        retrieved_docs=retrieved_docs,
        base_tech_stack=base_result["tech_stack"],
    )

    # Try AI-powered reasoning
    ai_reasoning = generate_stack_reasoning_ai(
        nodes=nodes_data,
        answers=request.answers,
        tech_stack=base_result["tech_stack"],
    )

    # Use AI results or fall back to template-based
    if ai_prompt:
        print("Using AI-generated prompt (GPT-4o-mini)")
        final_prompt = ai_prompt
    else:
        print("Falling back to template-based prompt with RAG enhancement")
        final_prompt = enhance_prompt_with_context(
            base_prompt=base_result["prompt"],
            retrieved_docs=retrieved_docs
        )

    final_reasoning = ai_reasoning if ai_reasoning else base_result["stack_reasoning"]

    print(f"Final prompt length: {len(final_prompt)} chars")
    print("="*50 + "\n")

    return GenerateResponse(
        prompt=final_prompt,
        stack_reasoning=final_reasoning,
        tech_stack=base_result["tech_stack"],
        retrieved_docs=retrieved_docs
    )


@app.get("/api/knowledge")
async def list_knowledge():
    """
    List all documents in the knowledge base (built-in + custom).
    """
    return {"documents": get_all_documents()}


@app.post("/api/knowledge/add-url")
async def add_url_to_knowledge(request: AddUrlRequest):
    """
    Fetch content from a URL and add it to the knowledge base.
    """
    result = add_document_from_url(url=request.url, tags=request.tags)
    return result


@app.delete("/api/knowledge/{doc_id}")
async def delete_knowledge_doc(doc_id: str):
    """
    Remove a custom document from the knowledge base.
    """
    success = remove_document(doc_id)
    if success:
        return {"success": True, "message": f"Document {doc_id} removed"}
    return {"success": False, "error": "Document not found or is built-in"}


@app.post("/api/knowledge/refresh-all")
async def refresh_all_urls():
    """
    Re-fetch and re-tag all URL-sourced documents with improved tagging.
    """
    from knowledge_base import CUSTOM_DOCUMENTS, fetch_url_content

    refreshed = []
    for doc in CUSTOM_DOCUMENTS:
        if doc.get("source") == "url" and doc.get("url"):
            url = doc["url"]
            result = fetch_url_content(url)
            if result["success"]:
                # Re-generate tags with new logic
                content_lower = result["content"].lower()
                title_lower = result["title"].lower()
                combined_text = content_lower + " " + title_lower

                new_tags = []
                tag_keywords = {
                    "userInput": ["form", "input", "user input", "login", "signup", "field"],
                    "logicBlock": ["validation", "logic", "process", "algorithm"],
                    "context": ["api", "fetch", "request", "integration", "endpoint"],
                    "database": ["database", "sql", "storage", "query", "data model"],
                    "output": ["display", "render", "chart", "dashboard", "visualization"],
                    "ui": ["ui", "user interface", "interface design", "ui design"],
                    "ux": ["ux", "user experience", "usability", "interaction"],
                    "design": ["design", "designer", "designing", "design system"],
                    "frontend": ["frontend", "front-end", "css", "html", "react"],
                }

                for tag, keywords in tag_keywords.items():
                    if any(kw in combined_text for kw in keywords):
                        new_tags.append(tag)

                if "interface" in combined_text or "design" in combined_text:
                    if "userInput" not in new_tags:
                        new_tags.append("userInput")
                    if "output" not in new_tags:
                        new_tags.append("output")

                doc["tags"] = new_tags if new_tags else ["general"]
                doc["content"] = result["content"]
                refreshed.append({
                    "id": doc["id"],
                    "title": doc["title"],
                    "new_tags": doc["tags"]
                })

    return {"refreshed": refreshed, "count": len(refreshed)}


@app.get("/api/knowledge/test-rag")
async def test_rag(
    nodes: str = "userInput,logicBlock,database,output",
    query: str = "user interface design form validation"
):
    """
    Test RAG retrieval with custom queries.

    Example: /api/knowledge/test-rag?nodes=userInput,output&query=ui design interface
    """
    test_node_types = [n.strip() for n in nodes.split(",")]
    test_descriptions = [query]

    docs = retrieve_relevant_docs(
        node_types=test_node_types,
        descriptions=test_descriptions,
        top_k=5
    )

    return {
        "query": {
            "node_types": test_node_types,
            "search_text": query
        },
        "retrieved_docs": [
            {
                "id": d["id"],
                "title": d["title"],
                "score": d["relevance_score"],
                "source": d["source"],
                "content_preview": d["content"][:200] + "..."
            }
            for d in docs
        ],
        "total_found": len(docs)
    }


@app.post("/api/score-descriptions")
async def score_descriptions(request: AnalyzeRequest):
    """
    Score the quality of node descriptions using a neural network.
    Built from scratch - no ML frameworks!
    """
    scorer = get_scorer()

    results = []
    for node in request.nodes:
        if node.type == "notes":
            continue

        description = node.description or ""
        if description:
            score_result = scorer.score(description)
        else:
            score_result = {
                "score": 0.0,
                "percentage": 0,
                "feedback": "No description provided. Add a description to improve prompt quality.",
                "quality": "missing"
            }

        results.append({
            "node_id": node.id,
            "node_type": node.type,
            "description": description,
            **score_result
        })

    # Calculate overall score
    valid_scores = [r["score"] for r in results if r["quality"] != "missing"]
    overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0

    return {
        "nodes": results,
        "overall_score": round(overall_score, 2),
        "overall_percentage": round(overall_score * 100),
        "model_info": {
            "name": "DescriptionQualityNetwork",
            "architecture": "3-layer feedforward neural network",
            "built_from_scratch": True,
            "framework": "NumPy only (no PyTorch/TensorFlow)"
        }
    }


@app.get("/api/model-info")
async def model_info():
    """
    Get information about the neural network model.
    """
    return {
        "name": "Description Quality Neural Network",
        "version": "1.0.0",
        "architecture": {
            "type": "Feedforward Neural Network",
            "input_layer": "208 neurons (200 vocab + 8 features)",
            "hidden_layer_1": "64 neurons, ReLU activation",
            "hidden_layer_2": "32 neurons, ReLU activation",
            "output_layer": "1 neuron, Sigmoid activation",
            "total_parameters": "~15,000"
        },
        "training": {
            "algorithm": "Backpropagation with Gradient Descent",
            "loss_function": "Binary Cross-Entropy",
            "training_samples": 40,
            "epochs": 2000
        },
        "built_from_scratch": True,
        "frameworks_used": ["NumPy"],
        "no_ml_frameworks": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
