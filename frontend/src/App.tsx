import { useState, useCallback } from 'react';
import type { Node, Edge } from '@xyflow/react';
import { ReactFlowProvider } from '@xyflow/react';
import { Sparkles, Database, Brain, Loader2 } from 'lucide-react';

import ComponentPalette from './components/ComponentPalette';
import Canvas from './components/Canvas';
import QuestionModal from './components/QuestionModal';
import PromptOutput from './components/PromptOutput';
import KnowledgePanel from './components/KnowledgePanel';
import type { ComponentType, Question, GenerateResponse } from './types';

// Initial example graph
const initialNodes: Node[] = [
  {
    id: 'node-1',
    type: 'userInput',
    position: { x: 250, y: 50 },
    data: { description: 'User submits email form' },
  },
  {
    id: 'node-2',
    type: 'logicBlock',
    position: { x: 250, y: 220 },
    data: { description: 'Validate email format' },
  },
  {
    id: 'node-3',
    type: 'database',
    position: { x: 250, y: 390 },
    data: { description: 'Store user in database' },
  },
  {
    id: 'node-4',
    type: 'output',
    position: { x: 250, y: 560 },
    data: { description: 'Show success message' },
  },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: 'node-1', target: 'node-2' },
  { id: 'e2-3', source: 'node-2', target: 'node-3' },
  { id: 'e3-4', source: 'node-3', target: 'node-4' },
];

type AppState = 'canvas' | 'questions' | 'loading' | 'result';

function App() {
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);
  const [appState, setAppState] = useState<AppState>('canvas');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [generatedResult, setGeneratedResult] = useState<GenerateResponse | null>(null);
  const [isKnowledgePanelOpen, setIsKnowledgePanelOpen] = useState(false);
  const [isScoring, setIsScoring] = useState(false);
  const [overallScore, setOverallScore] = useState<number | null>(null);
  const [nodeScores, setNodeScores] = useState<Record<string, any>>({});

  const handleDragStart = useCallback(
    (event: React.DragEvent, nodeType: ComponentType) => {
      event.dataTransfer.setData('application/reactflow', nodeType);
      event.dataTransfer.effectAllowed = 'move';
    },
    []
  );

  const handleDescriptionChange = useCallback((id: string, description: string) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === id ? { ...node, data: { ...node.data, description } } : node
      )
    );
  }, []);

  const handleAnalyze = async () => {
    try {
      const payload = {
        nodes: nodes.map((n) => ({
          id: n.id,
          type: n.type,
          description: n.data.description || '',
        })),
        edges: edges.map((e) => ({
          source: e.source,
          target: e.target,
        })),
      };

      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      setQuestions(data.questions);
      setAppState('questions');
    } catch (error) {
      console.error('Failed to analyze:', error);
    }
  };

  const handleQuestionsComplete = async (answers: Record<string, string>) => {
    setAppState('loading');

    try {
      const payload = {
        nodes: nodes.map((n) => ({
          id: n.id,
          type: n.type,
          description: n.data.description || '',
        })),
        edges: edges.map((e) => ({
          source: e.source,
          target: e.target,
        })),
        answers,
      };

      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      setGeneratedResult(data);
      setAppState('result');
    } catch (error) {
      console.error('Failed to generate:', error);
      setAppState('canvas');
    }
  };

  const handleStartOver = () => {
    setNodes([]);
    setEdges([]);
    setAppState('canvas');
    setGeneratedResult(null);
    setQuestions([]);
  };

  const handleCloseModal = () => {
    setAppState('canvas');
  };

  const handleScoreDescriptions = async () => {
    if (nodes.length === 0) return;

    setIsScoring(true);
    try {
      const payload = {
        nodes: nodes.map((n) => ({
          id: n.id,
          type: n.type,
          description: n.data.description || '',
        })),
        edges: edges.map((e) => ({
          source: e.source,
          target: e.target,
        })),
      };

      console.log('Scoring payload:', payload);

      const response = await fetch('/api/score-descriptions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Score response:', data);

      // Create a map of node scores
      const scoresMap: Record<string, any> = {};
      for (const nodeResult of data.nodes) {
        scoresMap[nodeResult.node_id] = {
          score: nodeResult.score,
          percentage: nodeResult.percentage,
          feedback: nodeResult.feedback,
          quality: nodeResult.quality,
        };
      }

      setNodeScores(scoresMap);
      setOverallScore(data.overall_percentage);

      // Update nodes with score data
      setNodes((nds) =>
        nds.map((node) => ({
          ...node,
          data: {
            ...node.data,
            scoreData: scoresMap[node.id],
          },
        }))
      );
    } catch (error) {
      console.error('Failed to score:', error);
      alert(`Failed to score: ${error}. Make sure the backend is running on port 8000.`);
    } finally {
      setIsScoring(false);
    }
  };

  return (
    <ReactFlowProvider>
      <div className="flex h-screen w-screen">
        <ComponentPalette onDragStart={handleDragStart} />

        <div className="flex-1 relative">
          <Canvas
            nodes={nodes}
            edges={edges}
            setNodes={setNodes}
            setEdges={setEdges}
            onDescriptionChange={handleDescriptionChange}
          />

        {/* Bottom Action Buttons */}
        <div className="absolute bottom-8 right-8 flex items-center gap-3">
          {/* Score Button */}
          <button
            onClick={handleScoreDescriptions}
            disabled={nodes.length === 0 || isScoring}
            className="group flex items-center gap-2 px-5 py-3 rounded-xl font-medium text-white transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed"
            style={{
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              boxShadow: nodes.length > 0 ? '0 4px 20px rgba(16, 185, 129, 0.3)' : 'none',
            }}
          >
            {isScoring ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Brain className="w-4 h-4" />
            )}
            <span>{isScoring ? 'Scoring...' : 'Score Descriptions'}</span>
            {overallScore !== null && (
              <span className="ml-1 px-2 py-0.5 rounded-full bg-white/20 text-xs">
                {overallScore}%
              </span>
            )}
          </button>

          {/* Generate Button */}
          <button
            onClick={handleAnalyze}
            disabled={nodes.length === 0}
            className="group flex items-center gap-3 px-7 py-4 rounded-2xl font-semibold text-white transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100"
            style={{
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              boxShadow: nodes.length > 0 ? '0 8px 32px rgba(99, 102, 241, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.1) inset' : 'none',
            }}
          >
            <Sparkles className="w-5 h-5 group-hover:animate-pulse" />
            <span>Generate Prompt</span>
            <svg className="w-4 h-4 opacity-60 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>

        {/* Header */}
        <div className="absolute top-0 left-0 right-0 pointer-events-none">
          <div className="flex justify-between items-center px-6 py-4 bg-gradient-to-b from-black/40 to-transparent">
            <div className="pointer-events-auto flex items-center gap-4">
              {/* Logo */}
              <div className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-xl blur opacity-40 group-hover:opacity-60 transition-opacity" />
                <div className="relative w-10 h-10 rounded-xl bg-[#0a0f1a] border border-white/10 flex items-center justify-center overflow-hidden">
                  <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none">
                    <path d="M4 4h16v16H4V4z" stroke="url(#frame-gradient)" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M8 8h8v8H8V8z" stroke="url(#frame-gradient)" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M4 4l4 4M20 4l-4 4M4 20l4-4M20 20l-4-4" stroke="url(#frame-gradient)" strokeWidth="2" strokeLinecap="round"/>
                    <defs>
                      <linearGradient id="frame-gradient" x1="4" y1="4" x2="20" y2="20">
                        <stop stopColor="#818cf8"/>
                        <stop offset="0.5" stopColor="#a78bfa"/>
                        <stop offset="1" stopColor="#c084fc"/>
                      </linearGradient>
                    </defs>
                  </svg>
                </div>
              </div>

              {/* Title */}
              <div>
                <h1 className="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
                  MainFrame
                  <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 uppercase tracking-wider">Beta</span>
                </h1>
                <p className="text-xs text-white/40">
                  Visual prompt engineering
                </p>
              </div>
            </div>

            {/* Right side */}
            <div className="pointer-events-auto flex items-center gap-3">
              {/* Knowledge Base button */}
              <button
                onClick={() => setIsKnowledgePanelOpen(true)}
                className="group flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20 hover:border-amber-500/40 backdrop-blur-sm transition-all hover:scale-[1.02]"
              >
                <Database className="w-4 h-4 text-amber-400" />
                <span className="text-xs text-amber-400/80 group-hover:text-amber-400">Knowledge Base</span>
              </button>

              {/* Node count badge */}
              {nodes.length > 0 && (
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 backdrop-blur-sm">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-xs text-white/50">{nodes.length} nodes</span>
                  <span className="text-white/20">|</span>
                  <span className="text-xs text-white/50">{edges.length} connections</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Question Modal */}
      {(appState === 'questions' || appState === 'loading') && (
        <QuestionModal
          questions={questions}
          onComplete={handleQuestionsComplete}
          onClose={handleCloseModal}
          isLoading={appState === 'loading'}
        />
      )}

      {/* Result Modal */}
      {appState === 'result' && generatedResult && (
        <PromptOutput result={generatedResult} onStartOver={handleStartOver} />
      )}

      {/* Knowledge Panel */}
      <KnowledgePanel
        isOpen={isKnowledgePanelOpen}
        onClose={() => setIsKnowledgePanelOpen(false)}
      />
      </div>
    </ReactFlowProvider>
  );
}

export default App;
