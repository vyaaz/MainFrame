import { useState, useEffect } from 'react';
import { Plus, Link, Trash2, Database, X, Loader2, Check, RefreshCw } from 'lucide-react';

interface KnowledgeDoc {
  id: string;
  title: string;
  tags: string[];
  source: string;
  url?: string;
}

interface KnowledgePanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function KnowledgePanel({ isOpen, onClose }: KnowledgePanelProps) {
  const [documents, setDocuments] = useState<KnowledgeDoc[]>([]);
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetchDocuments();
    }
  }, [isOpen]);

  const fetchDocuments = async () => {
    try {
      const response = await fetch('/api/knowledge');
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    }
  };

  const handleAddUrl = async () => {
    if (!url.trim()) return;

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch('/api/knowledge/add-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() }),
      });

      const data = await response.json();

      if (data.success) {
        setSuccess(`Added: ${data.document.title}`);
        setUrl('');
        fetchDocuments();
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError(data.error || 'Failed to add URL');
      }
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    try {
      const response = await fetch(`/api/knowledge/${docId}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      if (data.success) {
        fetchDocuments();
      }
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  const handleRefreshAll = async () => {
    setIsRefreshing(true);
    setError('');
    try {
      const response = await fetch('/api/knowledge/refresh-all', {
        method: 'POST',
      });
      const data = await response.json();
      if (data.count > 0) {
        setSuccess(`Refreshed ${data.count} URLs with improved tagging`);
        fetchDocuments();
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setSuccess('No URLs to refresh');
        setTimeout(() => setSuccess(''), 2000);
      }
    } catch (err) {
      setError('Failed to refresh URLs');
    } finally {
      setIsRefreshing(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-6 animate-fade-in">
      <div className="bg-[#0f1629]/95 backdrop-blur-xl rounded-3xl max-w-2xl w-full max-h-[80vh] border border-white/10 shadow-2xl overflow-hidden flex flex-col animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/30">
              <Database className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Knowledge Base</h2>
              <p className="text-xs text-white/40">Add URLs to enhance RAG retrieval</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleRefreshAll}
              disabled={isRefreshing}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-white/60 hover:text-white hover:bg-white/5 rounded-lg transition-colors disabled:opacity-50"
              title="Re-fetch URLs with improved tagging"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh Tags
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/5 rounded-xl transition-colors"
            >
              <X className="w-5 h-5 text-white/40 hover:text-white/80" />
            </button>
          </div>
        </div>

        {/* Add URL Section */}
        <div className="px-6 py-4 border-b border-white/5">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Link className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddUrl()}
                placeholder="Paste a URL to add to knowledge base..."
                className="w-full bg-black/30 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder-white/30 focus:outline-none focus:border-amber-500/50 transition-colors"
              />
            </div>
            <button
              onClick={handleAddUrl}
              disabled={isLoading || !url.trim()}
              className="flex items-center gap-2 px-5 py-3 rounded-xl font-medium text-white transition-all disabled:opacity-40 disabled:cursor-not-allowed hover:scale-[1.02] active:scale-[0.98]"
              style={{
                background: 'linear-gradient(135deg, #f59e0b 0%, #ea580c 100%)',
              }}
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Plus className="w-4 h-4" />
              )}
              Add
            </button>
          </div>

          {/* Status messages */}
          {error && (
            <p className="mt-2 text-sm text-red-400">{error}</p>
          )}
          {success && (
            <p className="mt-2 text-sm text-emerald-400 flex items-center gap-1">
              <Check className="w-4 h-4" />
              {success}
            </p>
          )}
        </div>

        {/* Documents List */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-3">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className={`p-4 rounded-xl border transition-all ${
                  doc.source === 'url'
                    ? 'bg-gradient-to-br from-amber-500/5 to-orange-500/5 border-amber-500/20'
                    : 'bg-white/5 border-white/10'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-white/90 truncate">
                        {doc.title}
                      </span>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded uppercase tracking-wider ${
                        doc.source === 'url'
                          ? 'bg-amber-500/20 text-amber-400'
                          : 'bg-indigo-500/20 text-indigo-400'
                      }`}>
                        {doc.source}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {doc.tags.map((tag) => {
                        // Highlight node-type matching tags
                        const isNodeType = ['userInput', 'logicBlock', 'context', 'database', 'output'].includes(tag);
                        return (
                          <span
                            key={tag}
                            className={`text-[10px] px-2 py-0.5 rounded-full ${
                              isNodeType
                                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                : 'bg-white/10 text-white/50'
                            }`}
                            title={isNodeType ? 'Matches node type - will be retrieved!' : 'Topic tag'}
                          >
                            {tag}
                          </span>
                        );
                      })}
                    </div>
                    {doc.url && (
                      <p className="text-xs text-white/30 mt-1 truncate">{doc.url}</p>
                    )}
                  </div>
                  {doc.source === 'url' && (
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="p-2 hover:bg-red-500/20 rounded-lg transition-colors group"
                    >
                      <Trash2 className="w-4 h-4 text-white/30 group-hover:text-red-400" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {documents.length === 0 && (
            <div className="text-center py-12 text-white/30">
              <Database className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No documents in knowledge base</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-white/5 bg-white/[0.02]">
          <p className="text-xs text-white/30 text-center">
            Added URLs will be used for RAG retrieval when generating prompts
          </p>
        </div>
      </div>
    </div>
  );
}
