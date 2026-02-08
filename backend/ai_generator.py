"""
AI-powered prompt generation using OpenAI GPT with Gemini fallback.

This module uses OpenAI to generate polished, professional prompts
based on the user's architecture and retrieved RAG context.
Falls back to Google Gemini if OpenAI fails.
"""

import os
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')


def generate_with_openai(system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
    """Try to generate with OpenAI GPT-4o-mini"""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=max_tokens,
        )
        print("✓ Generated with OpenAI GPT-4o-mini")
        return response.choices[0].message.content
    except Exception as e:
        print(f"✗ OpenAI failed: {e}")
        return None


def generate_with_gemini(system_prompt: str, user_prompt: str) -> str:
    """Fallback to Google Gemini"""
    try:
        # Combine system and user prompt for Gemini
        full_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
        response = gemini_model.generate_content(full_prompt)
        print("✓ Generated with Google Gemini (fallback)")
        return response.text
    except Exception as e:
        print(f"✗ Gemini also failed: {e}")
        return None


def generate_ai_prompt(
    nodes: list[dict],
    edges: list[dict],
    answers: dict[str, str],
    retrieved_docs: list[dict],
    base_tech_stack: list[str],
) -> str:
    """
    Use GPT to generate a polished, comprehensive prompt based on:
    - User's architecture (nodes and connections)
    - Their preferences (experience, scale, timeline, language)
    - Retrieved RAG context (best practices)

    Falls back to Gemini if OpenAI fails.
    """

    # Build architecture description
    node_descriptions = "\n".join([
        f"- {node['type']}: {node['description'] or 'No description'}"
        for node in nodes
    ])

    # Build flow description
    node_map = {n['id']: n for n in nodes}
    flows = []
    for edge in edges:
        source = node_map.get(edge['source'], {})
        target = node_map.get(edge['target'], {})
        flows.append(f"{source.get('description', source.get('type', '?'))} → {target.get('description', target.get('type', '?'))}")
    flow_description = "\n".join(flows) if flows else "No connections defined"

    # Build RAG context
    rag_context = "\n\n".join([
        f"### {doc['title']}\n{doc['content']}"
        for doc in retrieved_docs
    ]) if retrieved_docs else "No additional context"

    # Build the meta-prompt for GPT
    system_prompt = """You are an expert software architect and technical writer.
Your job is to generate clear, actionable prompts that developers can give to AI coding assistants (like GitHub Copilot, Cursor, or Claude) to build applications.

The prompts you generate should:
1. Be specific and actionable
2. Include clear technical requirements
3. Reference the recommended tech stack
4. Include best practices from the provided context
5. Be structured with clear sections
6. Be ready to copy-paste into an AI coding assistant"""

    user_prompt = f"""Generate a comprehensive prompt for building an application based on this architecture:

## User's Architecture
Components:
{node_descriptions}

Data Flow:
{flow_description}

## User Preferences
- Experience Level: {answers.get('experience', 'Intermediate')}
- Expected Scale: {answers.get('users', 'Small team')}
- Timeline: {answers.get('timeline', 'Standard')}
- Preferred Language: {answers.get('language', 'JavaScript/TypeScript')}

## Recommended Tech Stack
{', '.join(base_tech_stack)}

## Best Practices Context (from RAG retrieval)
{rag_context}

---

Now generate a polished, professional prompt that someone could give to an AI coding assistant to build this application.
The prompt should be comprehensive but focused, incorporating the best practices where relevant.
Format it with clear markdown sections."""

    # Try OpenAI first, then Gemini
    result = generate_with_openai(system_prompt, user_prompt)
    if result:
        return result

    result = generate_with_gemini(system_prompt, user_prompt)
    if result:
        return result

    # Both failed
    return None


def generate_stack_reasoning_ai(
    nodes: list[dict],
    answers: dict[str, str],
    tech_stack: list[str],
) -> str:
    """
    Use GPT to generate a natural explanation for the tech stack choices.
    Falls back to Gemini if OpenAI fails.
    """

    node_types = [n['type'] for n in nodes]

    system_prompt = "You are a helpful technical advisor."
    user_prompt = f"""Explain in 2-3 sentences why this tech stack was chosen:

Tech Stack: {', '.join(tech_stack)}

For an app with these components: {', '.join(node_types)}
User experience level: {answers.get('experience', 'Intermediate')}
Expected scale: {answers.get('users', 'Small')}
Timeline: {answers.get('timeline', 'Standard')}

Be concise and focus on the key reasons. Don't use bullet points."""

    # Try OpenAI first, then Gemini
    result = generate_with_openai(system_prompt, user_prompt, max_tokens=200)
    if result:
        return result

    result = generate_with_gemini(system_prompt, user_prompt)
    if result:
        return result

    return None
