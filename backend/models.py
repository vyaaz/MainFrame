from pydantic import BaseModel
from typing import Optional


class NodeData(BaseModel):
    id: str
    type: str
    description: str


class EdgeData(BaseModel):
    source: str
    target: str


class AnalyzeRequest(BaseModel):
    nodes: list[NodeData]
    edges: list[EdgeData]


class QuestionOption(BaseModel):
    label: str
    description: str


class Question(BaseModel):
    id: str
    question: str
    options: list[QuestionOption]


class AnalyzeResponse(BaseModel):
    questions: list[Question]


class GenerateRequest(BaseModel):
    nodes: list[NodeData]
    edges: list[EdgeData]
    answers: dict[str, str]


class RetrievedDocument(BaseModel):
    id: str
    title: str
    content: str
    relevance_score: int
    source: str = "built-in"
    url: str | None = None


class GenerateResponse(BaseModel):
    prompt: str
    stack_reasoning: str
    tech_stack: list[str]
    retrieved_docs: list[RetrievedDocument]


class AddUrlRequest(BaseModel):
    url: str
    tags: list[str] | None = None


class KnowledgeDocument(BaseModel):
    id: str
    title: str
    tags: list[str]
    source: str
    url: str | None = None
    content_preview: str | None = None
