from models import NodeData, EdgeData


def get_questions():
    """Return the standard set of clarifying questions."""
    return [
        {
            "id": "experience",
            "question": "What's your experience level?",
            "options": [
                {"label": "Beginner", "description": "I'll suggest easier tools and simpler patterns"},
                {"label": "Intermediate", "description": "Balance between power and simplicity"},
                {"label": "Expert", "description": "Optimize for performance and scalability"},
            ],
        },
        {
            "id": "users",
            "question": "Expected number of users?",
            "options": [
                {"label": "Just me", "description": "Personal project or prototype"},
                {"label": "10-100 users", "description": "Small team or beta launch"},
                {"label": "100-1000 users", "description": "Growing product"},
                {"label": "1000+ users", "description": "Scale for high traffic"},
            ],
        },
        {
            "id": "timeline",
            "question": "What's your timeline?",
            "options": [
                {"label": "Prototype in < 1 day", "description": "Quick MVP, speed over polish"},
                {"label": "Production-ready in a week", "description": "Solid foundation with basic features"},
                {"label": "Long-term project", "description": "Invest in architecture and testing"},
            ],
        },
        {
            "id": "language",
            "question": "Preferred programming language?",
            "options": [
                {"label": "JavaScript/TypeScript", "description": "Full-stack JS with Node.js backend"},
                {"label": "Python", "description": "Python backend with FastAPI or Django"},
                {"label": "No preference", "description": "I'll suggest the best fit"},
            ],
        },
    ]


def analyze_graph(nodes: list[NodeData], edges: list[EdgeData]) -> dict:
    """Analyze the graph structure and identify patterns."""
    # Filter out notes from analysis (they're just annotations)
    functional_nodes = [n for n in nodes if n.type != "notes"]
    node_types = {n.type for n in functional_nodes}
    node_map = {n.id: n for n in nodes}

    warnings = []
    suggestions = []

    # Check for User Input -> Database without Logic Block
    for edge in edges:
        source = node_map.get(edge.source)
        target = node_map.get(edge.target)
        if source and target:
            if source.type == "userInput" and target.type == "database":
                warnings.append("Direct connection from User Input to Database detected. Consider adding a Logic Block for validation.")

    # Check for Context node (external API)
    if "context" in node_types:
        suggestions.append("External API integration detected - will include API client setup")

    # Check for Output node
    if "output" in node_types:
        suggestions.append("Output display needed - will include UI components")

    return {
        "node_types": node_types,
        "warnings": warnings,
        "suggestions": suggestions,
        "has_database": "database" in node_types,
        "has_api": "context" in node_types,
        "has_logic": "logicBlock" in node_types,
        "has_input": "userInput" in node_types,
        "has_output": "output" in node_types,
    }


def generate_prompt(
    nodes: list[NodeData],
    edges: list[EdgeData],
    answers: dict[str, str],
) -> dict:
    """Generate an optimized prompt based on the graph and answers."""
    analysis = analyze_graph(nodes, edges)

    experience = answers.get("experience", "Intermediate")
    users = answers.get("users", "10-100 users")
    timeline = answers.get("timeline", "Production-ready in a week")
    language = answers.get("language", "JavaScript/TypeScript")

    # Determine tech stack based on answers and analysis
    tech_stack = []
    reasoning_parts = []

    # Frontend
    if analysis["has_input"] or analysis["has_output"]:
        if experience == "Beginner":
            tech_stack.append("React")
            tech_stack.append("Create React App")
            reasoning_parts.append("React with Create React App for a beginner-friendly setup")
        else:
            tech_stack.append("React")
            tech_stack.append("Vite")
            tech_stack.append("TypeScript")
            reasoning_parts.append("React + Vite + TypeScript for modern, type-safe development")

    # Backend
    if language == "JavaScript/TypeScript":
        if experience == "Beginner":
            tech_stack.append("Express.js")
            reasoning_parts.append("Express.js for a straightforward Node.js backend")
        elif users in ["1000+ users"]:
            tech_stack.append("NestJS")
            reasoning_parts.append("NestJS for scalable, enterprise-grade architecture")
        else:
            tech_stack.append("Express.js")
            reasoning_parts.append("Express.js for flexible and lightweight backend")
    elif language == "Python":
        if timeline == "Prototype in < 1 day":
            tech_stack.append("FastAPI")
            reasoning_parts.append("FastAPI for rapid API development with automatic docs")
        else:
            tech_stack.append("FastAPI")
            reasoning_parts.append("FastAPI for high-performance async Python backend")
    else:
        tech_stack.append("Express.js")
        reasoning_parts.append("Express.js as a versatile default choice")

    # Database
    if analysis["has_database"]:
        if timeline == "Prototype in < 1 day":
            tech_stack.append("SQLite")
            reasoning_parts.append("SQLite for zero-config database setup")
        elif users in ["1000+ users"]:
            tech_stack.append("PostgreSQL")
            tech_stack.append("Redis")
            reasoning_parts.append("PostgreSQL + Redis for scalable data layer with caching")
        else:
            tech_stack.append("PostgreSQL")
            reasoning_parts.append("PostgreSQL for reliable relational data storage")

    # API Integration
    if analysis["has_api"]:
        tech_stack.append("Axios")
        reasoning_parts.append("Axios for robust HTTP client with interceptors")

    # Additional tools based on experience
    if experience == "Beginner":
        tech_stack.append("Tailwind CSS")
        reasoning_parts.append("Tailwind CSS for utility-first styling without complex CSS")
    else:
        tech_stack.append("Tailwind CSS")
        reasoning_parts.append("Tailwind CSS for rapid UI development")

    # Deployment
    if timeline == "Prototype in < 1 day":
        tech_stack.append("Vercel")
        reasoning_parts.append("Vercel for instant deployment with zero config")

    # Build the prompt
    node_descriptions = []
    notes_descriptions = []
    for node in nodes:
        desc = node.description if node.description else f"[{node.type}]"
        if node.type == "notes":
            if node.description:
                notes_descriptions.append(f"- {node.description}")
        else:
            node_descriptions.append(f"- {node.type}: {desc}")

    flow_description = []
    node_map = {n.id: n for n in nodes}
    for edge in edges:
        source = node_map.get(edge.source)
        target = node_map.get(edge.target)
        if source and target:
            s_desc = source.description or source.type
            t_desc = target.description or target.type
            flow_description.append(f"  {s_desc} -> {t_desc}")

    # Add warnings if any
    warnings_text = ""
    if analysis["warnings"]:
        warnings_text = "\n\n## Important Notes\n" + "\n".join(f"- {w}" for w in analysis["warnings"])

    # Add developer notes if any
    notes_text = ""
    if notes_descriptions:
        notes_text = "\n\n## Developer Notes\n" + "\n".join(notes_descriptions)

    prompt = f"""Build a web application with the following architecture and requirements:

## Application Flow
The app consists of these components:
{chr(10).join(node_descriptions)}

Data flows through the system as follows:
{chr(10).join(flow_description)}

## Tech Stack
Use the following technologies:
- Frontend: {', '.join([t for t in tech_stack if t in ['React', 'Vite', 'TypeScript', 'Create React App', 'Tailwind CSS']])}
- Backend: {', '.join([t for t in tech_stack if t in ['Express.js', 'NestJS', 'FastAPI']])}
- Database: {', '.join([t for t in tech_stack if t in ['PostgreSQL', 'SQLite', 'Redis']]) or 'None required'}
- Deployment: {', '.join([t for t in tech_stack if t in ['Vercel']]) or 'Docker recommended'}

## Requirements
- Experience level: {experience} ({"use simple patterns and clear comments" if experience == "Beginner" else "optimize for maintainability" if experience == "Intermediate" else "focus on performance and scalability"})
- Scale: {users}
- Timeline: {timeline}
{warnings_text}{notes_text}

## Implementation Guidelines
1. Start with the data models and database schema
2. Build the API endpoints
3. Create the frontend components
4. Connect frontend to backend
5. Add error handling and validation
6. Test the complete flow

Please implement this step by step, starting with the project setup and folder structure."""

    stack_reasoning = " | ".join(reasoning_parts)

    return {
        "prompt": prompt,
        "stack_reasoning": stack_reasoning,
        "tech_stack": tech_stack,
    }
