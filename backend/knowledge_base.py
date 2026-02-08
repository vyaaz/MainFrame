"""
Simple RAG Knowledge Base for MainFrame

This module contains curated knowledge documents about tech stacks,
best practices, and architectural patterns that get retrieved based
on the user's architecture design.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import hashlib

# In-memory storage for added documents (resets on server restart)
CUSTOM_DOCUMENTS = []

KNOWLEDGE_DOCUMENTS = [
    {
        "id": "react-frontend",
        "title": "React Frontend Best Practices",
        "tags": ["userInput", "output", "frontend", "react", "javascript"],
        "content": """
React is ideal for building interactive user interfaces. Key recommendations:
- Use functional components with hooks (useState, useEffect, useContext)
- Implement proper form validation with libraries like react-hook-form or Formik
- Use React Query or SWR for server state management
- Implement loading states and error boundaries for better UX
- Use TypeScript for type safety in larger applications
"""
    },
    {
        "id": "api-integration",
        "title": "API Integration Patterns",
        "tags": ["context", "api", "integration", "external"],
        "content": """
When integrating external APIs, follow these patterns:
- Use axios or fetch with proper error handling and retries
- Implement request/response interceptors for auth tokens
- Cache responses where appropriate to reduce API calls
- Use environment variables for API keys (never hardcode)
- Implement rate limiting awareness and backoff strategies
- Consider using API gateway patterns for multiple services
"""
    },
    {
        "id": "database-design",
        "title": "Database Design Principles",
        "tags": ["database", "storage", "postgresql", "data"],
        "content": """
For robust data persistence:
- PostgreSQL is recommended for relational data with complex queries
- Use proper indexing on frequently queried columns
- Implement database migrations for schema changes (Prisma, Alembic)
- Use connection pooling for production environments
- Consider Redis for caching frequently accessed data
- Implement soft deletes for data recovery capabilities
"""
    },
    {
        "id": "validation-logic",
        "title": "Input Validation & Business Logic",
        "tags": ["logicBlock", "validation", "security", "logic"],
        "content": """
Proper validation prevents security issues and data corruption:
- Validate on both client and server side (never trust client only)
- Use schema validation libraries (Zod, Yup, Pydantic)
- Sanitize inputs to prevent XSS and SQL injection
- Implement proper error messages without exposing internals
- Use middleware patterns for reusable validation logic
- Consider using the repository pattern for data access
"""
    },
    {
        "id": "authentication",
        "title": "Authentication & Authorization",
        "tags": ["userInput", "security", "auth", "jwt"],
        "content": """
Secure authentication implementation:
- Use JWT tokens with short expiration + refresh tokens
- Store tokens in httpOnly cookies (not localStorage)
- Implement proper password hashing (bcrypt, argon2)
- Use OAuth2 for third-party authentication
- Implement role-based access control (RBAC)
- Add rate limiting to prevent brute force attacks
"""
    },
    {
        "id": "output-display",
        "title": "Data Display & Visualization",
        "tags": ["output", "display", "ui", "charts"],
        "content": """
For effective data presentation:
- Use pagination or virtual scrolling for large datasets
- Implement skeleton loaders for better perceived performance
- Consider Chart.js or Recharts for data visualization
- Use proper number and date formatting (Intl API)
- Implement responsive tables with horizontal scroll on mobile
- Add export functionality (CSV, PDF) for user convenience
"""
    },
    {
        "id": "scalability",
        "title": "Scalability Considerations",
        "tags": ["database", "api", "performance", "scale"],
        "content": """
Building for scale from the start:
- Implement horizontal scaling with stateless services
- Use message queues (Redis, RabbitMQ) for async operations
- Implement CDN for static assets
- Use database read replicas for read-heavy workloads
- Consider microservices for complex domains
- Implement proper logging and monitoring (structured logs)
"""
    },
    {
        "id": "error-handling",
        "title": "Error Handling Patterns",
        "tags": ["logicBlock", "output", "errors", "logging"],
        "content": """
Robust error handling improves reliability:
- Use try-catch with specific error types
- Implement global error handlers (Express middleware, React boundaries)
- Log errors with context (user ID, request ID, stack trace)
- Return user-friendly error messages
- Implement retry logic for transient failures
- Use circuit breakers for external service calls
"""
    },
]


def retrieve_relevant_docs(node_types: list[str], descriptions: list[str], top_k: int = 3) -> list[dict]:
    """
    Smart RAG retrieval with semantic relationships and flexible matching.
    """
    scored_docs = []

    # Combine all descriptions into searchable text
    search_text = " ".join(descriptions).lower()

    # Search both built-in and custom documents
    all_documents = KNOWLEDGE_DOCUMENTS + CUSTOM_DOCUMENTS

    # Semantic relationships: which tags relate to which node types
    TAG_RELATIONSHIPS = {
        "userInput": ["frontend", "ui", "form", "input", "react", "user", "interface", "ux", "design", "component"],
        "output": ["frontend", "ui", "display", "react", "charts", "visualization", "dashboard", "interface", "design"],
        "logicBlock": ["validation", "backend", "logic", "security", "auth", "algorithm", "processing"],
        "database": ["database", "storage", "sql", "data", "backend", "cache", "persistence"],
        "context": ["api", "integration", "backend", "external", "fetch", "http", "rest", "graphql"],
    }

    # Important keywords that indicate relevance
    RELEVANCE_KEYWORDS = [
        "react", "frontend", "backend", "api", "database", "ui", "ux", "design",
        "component", "form", "input", "validation", "auth", "security", "display",
        "chart", "table", "user", "interface", "data", "query", "fetch", "state",
        "hook", "typescript", "javascript", "python", "node", "express", "fastapi"
    ]

    print(f"\n=== RAG RETRIEVAL ===")
    print(f"Node types: {node_types}")
    print(f"Search text: {search_text[:100]}...")
    print(f"Total documents to search: {len(all_documents)}")

    for doc in all_documents:
        score = 0
        reasons = []
        doc_tags = [t.lower() for t in doc["tags"]]
        doc_content = doc["content"].lower()

        # 1. Direct tag match with node types (+15)
        for tag in doc["tags"]:
            if tag in node_types:
                score += 15
                reasons.append(f"direct:{tag}")

        # 2. Semantic relationship matching (+10)
        for node_type in node_types:
            related_tags = TAG_RELATIONSHIPS.get(node_type, [])
            for related in related_tags:
                if related in doc_tags or related in doc_content:
                    score += 8
                    reasons.append(f"semantic:{node_type}→{related}")
                    break  # Only count once per node type

        # 3. Keyword matching in document content vs descriptions (+5 each)
        search_words = set(search_text.split())
        for word in search_words:
            if len(word) > 3:
                if word in doc_content:
                    score += 3
                    if len(reasons) < 5:  # Limit logged reasons
                        reasons.append(f"keyword:{word}")

        # 4. Important keyword bonus - if doc contains key terms (+3 each)
        for keyword in RELEVANCE_KEYWORDS:
            if keyword in doc_content and keyword in search_text:
                score += 5
                if len(reasons) < 8:
                    reasons.append(f"important:{keyword}")

        # 5. Tag overlap with search text (+4)
        for tag in doc_tags:
            if tag in search_text:
                score += 4
                reasons.append(f"tag-in-search:{tag}")

        # 6. Boost URL-sourced docs slightly if they have good content length
        if doc.get("source") == "url" and len(doc["content"]) > 500:
            score += 3
            reasons.append("url-content-boost")

        if score > 0:
            print(f"  [{doc.get('id', 'unknown')}] score={score} | {', '.join(reasons[:6])}")
            scored_docs.append({
                "doc": doc,
                "score": score
            })

    # Sort by score and return top_k
    scored_docs.sort(key=lambda x: x["score"], reverse=True)

    results = [
        {
            "id": item["doc"]["id"],
            "title": item["doc"]["title"],
            "content": item["doc"]["content"].strip(),
            "relevance_score": item["score"],
            "source": item["doc"].get("source", "built-in"),
            "url": item["doc"].get("url")
        }
        for item in scored_docs[:top_k]
    ]

    print(f"\n=== TOP {top_k} RETRIEVED ===")
    for r in results:
        print(f"  - {r['title']} (score: {r['relevance_score']}, source: {r['source']})")
    print("=== END RAG ===\n")

    return results


def enhance_prompt_with_context(base_prompt: str, retrieved_docs: list[dict]) -> str:
    """
    Enhance the generated prompt with retrieved knowledge context.
    """
    if not retrieved_docs:
        return base_prompt

    context_section = "\n\n## Retrieved Best Practices\n"
    context_section += "Based on your architecture, consider these recommendations:\n\n"

    for doc in retrieved_docs:
        context_section += f"### {doc['title']}\n"
        context_section += f"{doc['content']}\n\n"

    # Insert context before implementation guidelines
    if "## Implementation Guidelines" in base_prompt:
        return base_prompt.replace(
            "## Implementation Guidelines",
            f"{context_section}## Implementation Guidelines"
        )
    else:
        return base_prompt + context_section


def fetch_url_content(url: str) -> dict:
    """
    Fetch and parse content from a URL.
    Returns title and cleaned text content.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Get title
        title = soup.title.string if soup.title else urlparse(url).netloc

        # Get meta description for additional context
        meta_desc = ""
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag and meta_tag.get('content'):
            meta_desc = meta_tag['content']

        # Also try og:description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            meta_desc = meta_desc or og_desc['content']

        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'iframe']):
            element.decompose()

        # Get main content - try common content containers
        main_content = None
        for selector in ['article', 'main', '[role="main"]', '.content', '.post-content', '.article-content', '.entry-content', '#content', '.post', '.article']:
            main_content = soup.select_one(selector)
            if main_content:
                break

        if not main_content:
            main_content = soup.body

        # Extract text from paragraphs and headings for cleaner content
        text_parts = []
        if main_content:
            for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li']):
                text = element.get_text(strip=True)
                if len(text) > 20:  # Skip very short fragments
                    text_parts.append(text)

        # If we got good paragraph content, use it; otherwise fall back to all text
        if len(text_parts) > 3:
            text = ' '.join(text_parts)
        else:
            text = main_content.get_text(separator=' ', strip=True) if main_content else soup.get_text(separator=' ', strip=True)

        # Clean up whitespace
        text = ' '.join(text.split())

        # Prepend meta description for better context
        if meta_desc:
            text = f"{meta_desc} {text}"

        # Increased limit to 4000 chars for better context
        text = text[:4000]

        print(f"Fetched URL: {url}")
        print(f"Title: {title}")
        print(f"Content length: {len(text)} chars")

        return {
            "success": True,
            "title": title.strip() if title else "Untitled",
            "content": text,
            "url": url
        }
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def add_document_from_url(url: str, tags: list[str] = None) -> dict:
    """
    Fetch content from URL and add it to the knowledge base.
    """
    # Generate unique ID from URL
    doc_id = hashlib.md5(url.encode()).hexdigest()[:8]

    # Check if already exists
    for doc in CUSTOM_DOCUMENTS:
        if doc.get("url") == url:
            return {"success": False, "error": "URL already in knowledge base"}

    # Fetch content
    result = fetch_url_content(url)

    if not result["success"]:
        return result

    # Auto-generate tags if not provided
    if not tags:
        content_lower = result["content"].lower()
        title_lower = result["title"].lower()
        combined_text = content_lower + " " + title_lower
        auto_tags = []

        # Map keywords to tags - check both content AND title
        tag_keywords = {
            # Node type matches (critical for RAG)
            "userInput": ["form", "input", "user input", "login", "signup", "register", "submit", "field", "text field"],
            "logicBlock": ["validation", "logic", "process", "transform", "calculate", "algorithm", "function", "business logic"],
            "context": ["api", "fetch", "request", "external", "integration", "webhook", "endpoint", "http", "rest"],
            "database": ["database", "sql", "postgresql", "mysql", "mongodb", "redis", "storage", "query", "schema", "data model"],
            "output": ["display", "render", "output", "view", "chart", "table", "list", "dashboard", "visualization"],
            # UI/UX tags - important for frontend docs
            "ui": ["ui", "user interface", "interface design", "visual design", "ui design"],
            "ux": ["ux", "user experience", "usability", "interaction design", "ixd"],
            "design": ["design", "designer", "designing", "design system", "design pattern"],
            # Tech tags
            "react": ["react", "component", "hooks", "useState", "jsx", "nextjs", "react native"],
            "frontend": ["frontend", "front-end", "front end", "css", "html", "tailwind", "style", "styling", "responsive"],
            "backend": ["backend", "back-end", "back end", "server", "node", "express", "fastapi", "django"],
            "auth": ["auth", "authentication", "password", "jwt", "oauth", "session", "token", "login"],
            "security": ["security", "xss", "injection", "sanitize", "encrypt", "https", "vulnerability"],
        }

        for tag, keywords in tag_keywords.items():
            if any(kw in combined_text for kw in keywords):
                auto_tags.append(tag)

        # Always include at least these if it's about UI/design
        if "interface" in combined_text or "design" in combined_text:
            if "userInput" not in auto_tags:
                auto_tags.append("userInput")
            if "output" not in auto_tags:
                auto_tags.append("output")

        tags = auto_tags if auto_tags else ["general"]
        print(f"Auto-generated tags for URL: {tags}")

    # Create document
    new_doc = {
        "id": f"url-{doc_id}",
        "title": result["title"],
        "tags": tags,
        "content": result["content"],
        "url": url,
        "source": "url"
    }

    CUSTOM_DOCUMENTS.append(new_doc)

    print(f"\n=== URL ADDED TO KNOWLEDGE BASE ===")
    print(f"Title: {new_doc['title']}")
    print(f"Tags: {new_doc['tags']}")
    print(f"Content preview: {new_doc['content'][:100]}...")
    print(f"Total custom documents: {len(CUSTOM_DOCUMENTS)}")
    print("===================================\n")

    return {
        "success": True,
        "document": {
            "id": new_doc["id"],
            "title": new_doc["title"],
            "tags": new_doc["tags"],
            "content_preview": new_doc["content"][:200] + "..."
        }
    }


def get_all_documents() -> list[dict]:
    """Return all documents (built-in + custom)."""
    all_docs = []

    for doc in KNOWLEDGE_DOCUMENTS:
        all_docs.append({
            "id": doc["id"],
            "title": doc["title"],
            "tags": doc["tags"],
            "source": "built-in"
        })

    for doc in CUSTOM_DOCUMENTS:
        all_docs.append({
            "id": doc["id"],
            "title": doc["title"],
            "tags": doc["tags"],
            "source": "url",
            "url": doc.get("url")
        })

    return all_docs


def remove_document(doc_id: str) -> bool:
    """Remove a custom document by ID."""
    global CUSTOM_DOCUMENTS
    original_len = len(CUSTOM_DOCUMENTS)
    CUSTOM_DOCUMENTS = [d for d in CUSTOM_DOCUMENTS if d["id"] != doc_id]
    return len(CUSTOM_DOCUMENTS) < original_len
