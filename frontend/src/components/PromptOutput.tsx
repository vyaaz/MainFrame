import { useState } from 'react';
import { Copy, Check, ChevronDown, ChevronUp, RotateCcw, Database, Sparkles, Link, ExternalLink } from 'lucide-react';
import type { GenerateResponse } from '../types';

interface PromptOutputProps {
  result: GenerateResponse;
  onStartOver: () => void;
}

export default function PromptOutput({ result, onStartOver }: PromptOutputProps) {
  const [copied, setCopied] = useState(false);
  const [showReasoning, setShowReasoning] = useState(false);
  const [showRAG, setShowRAG] = useState(true);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(result.prompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-6 animate-fade-in">
      <div className="bg-[#0f1629]/95 backdrop-blur-xl rounded-3xl max-w-5xl w-full max-h-[90vh] border border-white/10 shadow-2xl overflow-hidden flex flex-col animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between px-8 py-6 border-b border-white/5">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/30">
                <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-white">
                Your Prompt is Ready
              </h2>
            </div>
            <p className="text-sm text-white/40 ml-[52px]">
              Enhanced with RAG-retrieved best practices
            </p>
          </div>
          <button
            onClick={handleCopy}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-white transition-all hover:scale-[1.02] active:scale-[0.98]"
            style={{
              background: copied
                ? 'linear-gradient(135deg, #10b981 0%, #14b8a6 100%)'
                : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              boxShadow: copied
                ? '0 4px 20px rgba(16, 185, 129, 0.4)'
                : '0 4px 20px rgba(99, 102, 241, 0.4)',
            }}
          >
            {copied ? (
              <>
                <Check className="w-4 h-4" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                Copy Prompt
              </>
            )}
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-8">
          {/* Tech Stack Tags */}
          <div className="flex flex-wrap gap-2 mb-6">
            {result.tech_stack.map((tech) => (
              <span
                key={tech}
                className="px-3 py-1.5 rounded-lg text-sm font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
              >
                {tech}
              </span>
            ))}
          </div>

          {/* RAG Retrieved Documents Section */}
          {result.retrieved_docs && result.retrieved_docs.length > 0 && (
            <div className="mb-6">
              <button
                onClick={() => setShowRAG(!showRAG)}
                className="flex items-center gap-2 text-white/80 hover:text-white transition-colors group mb-3"
              >
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-500/20 to-orange-500/20 border border-amber-500/30 flex items-center justify-center">
                  <Database className="w-4 h-4 text-amber-400" />
                </div>
                <span className="font-medium">RAG Context Retrieved</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400">
                  {result.retrieved_docs.length} docs
                </span>
                {result.retrieved_docs.filter(d => d.source === 'url').length > 0 && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400">
                    {result.retrieved_docs.filter(d => d.source === 'url').length} from your URLs
                  </span>
                )}
                <div className="w-5 h-5 rounded bg-white/5 flex items-center justify-center ml-1">
                  {showRAG ? (
                    <ChevronUp className="w-3 h-3 text-white/40" />
                  ) : (
                    <ChevronDown className="w-3 h-3 text-white/40" />
                  )}
                </div>
              </button>

              {showRAG && (
                <div className="grid gap-3 animate-fade-in">
                  {result.retrieved_docs.map((doc) => (
                    <div
                      key={doc.id}
                      className={`p-4 rounded-xl border ${
                        doc.source === 'url'
                          ? 'bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border-emerald-500/30'
                          : 'bg-gradient-to-br from-amber-500/5 to-orange-500/5 border-amber-500/20'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {doc.source === 'url' ? (
                            <Link className="w-4 h-4 text-emerald-400" />
                          ) : (
                            <Sparkles className="w-4 h-4 text-amber-400" />
                          )}
                          <span className="font-medium text-white/90">{doc.title}</span>
                          <span className={`text-[10px] px-1.5 py-0.5 rounded uppercase tracking-wider ${
                            doc.source === 'url'
                              ? 'bg-emerald-500/20 text-emerald-400'
                              : 'bg-indigo-500/20 text-indigo-400'
                          }`}>
                            {doc.source === 'url' ? 'Your URL' : 'Built-in'}
                          </span>
                        </div>
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          doc.source === 'url'
                            ? 'bg-emerald-500/20 text-emerald-400/80'
                            : 'bg-amber-500/20 text-amber-400/80'
                        }`}>
                          score: {doc.relevance_score}
                        </span>
                      </div>
                      {doc.source === 'url' && doc.url && (
                        <a
                          href={doc.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-xs text-emerald-400/70 hover:text-emerald-400 mb-2 transition-colors"
                        >
                          <ExternalLink className="w-3 h-3" />
                          {doc.url.length > 50 ? doc.url.slice(0, 50) + '...' : doc.url}
                        </a>
                      )}
                      <p className="text-sm text-white/50 leading-relaxed line-clamp-3">
                        {doc.content.slice(0, 200)}...
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Prompt */}
          <div className="relative group">
            <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-indigo-500/20 to-purple-500/20 opacity-0 group-hover:opacity-100 transition-opacity blur-xl" />
            <div className="relative bg-black/40 rounded-2xl p-6 border border-white/10">
              <pre className="whitespace-pre-wrap text-sm text-white/80 font-mono leading-relaxed">
                {result.prompt}
              </pre>
            </div>
          </div>

          {/* Reasoning Collapsible */}
          <div className="mt-6">
            <button
              onClick={() => setShowReasoning(!showReasoning)}
              className="flex items-center gap-2 text-white/40 hover:text-white/80 transition-colors group"
            >
              <div className="w-6 h-6 rounded-lg bg-white/5 flex items-center justify-center group-hover:bg-white/10 transition-colors">
                {showReasoning ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </div>
              <span className="text-sm font-medium">Why this stack?</span>
            </button>
            {showReasoning && (
              <div className="mt-4 p-5 rounded-2xl bg-white/5 border border-white/5 text-sm text-white/60 leading-relaxed animate-fade-in">
                {result.stack_reasoning}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-8 py-5 border-t border-white/5 bg-white/[0.02]">
          <button
            onClick={onStartOver}
            className="flex items-center gap-2 px-4 py-2 text-white/40 hover:text-white/80 hover:bg-white/5 rounded-xl transition-all"
          >
            <RotateCcw className="w-4 h-4" />
            <span className="text-sm font-medium">Start Over</span>
          </button>
        </div>
      </div>
    </div>
  );
}
