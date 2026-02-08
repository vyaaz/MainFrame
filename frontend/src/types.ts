export type ComponentType = 'userInput' | 'logicBlock' | 'context' | 'database' | 'output' | 'notes';

export interface ComponentConfig {
  type: ComponentType;
  label: string;
  icon: string;
  color: string;
  bgColor: string;
}

export const COMPONENT_CONFIGS: Record<ComponentType, ComponentConfig> = {
  userInput: {
    type: 'userInput',
    label: 'User Input',
    icon: '👤',
    color: '#60a5fa',
    bgColor: 'rgba(96, 165, 250, 0.1)',
  },
  logicBlock: {
    type: 'logicBlock',
    label: 'Logic Block',
    icon: '🧠',
    color: '#a78bfa',
    bgColor: 'rgba(167, 139, 250, 0.1)',
  },
  context: {
    type: 'context',
    label: 'API / Context',
    icon: '🔗',
    color: '#fb923c',
    bgColor: 'rgba(251, 146, 60, 0.1)',
  },
  database: {
    type: 'database',
    label: 'Database',
    icon: '💾',
    color: '#4ade80',
    bgColor: 'rgba(74, 222, 128, 0.1)',
  },
  output: {
    type: 'output',
    label: 'Output',
    icon: '📊',
    color: '#facc15',
    bgColor: 'rgba(250, 204, 21, 0.1)',
  },
  notes: {
    type: 'notes',
    label: 'Notes',
    icon: '📝',
    color: '#94a3b8',
    bgColor: 'rgba(148, 163, 184, 0.1)',
  },
};

export interface AppNode {
  id: string;
  type: ComponentType;
  position: { x: number; y: number };
  data: { description: string };
}

export interface AppEdge {
  id: string;
  source: string;
  target: string;
}

export interface Question {
  id: string;
  question: string;
  options: { label: string; description: string }[];
}

export interface AnalyzeResponse {
  questions: Question[];
}

export interface RetrievedDocument {
  id: string;
  title: string;
  content: string;
  relevance_score: number;
  source: 'built-in' | 'url';
  url?: string;
}

export interface GenerateResponse {
  prompt: string;
  stack_reasoning: string;
  tech_stack: string[];
  retrieved_docs: RetrievedDocument[];
}
