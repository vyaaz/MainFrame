import { memo, useState, useRef, useEffect } from 'react';
import { Handle, Position } from '@xyflow/react';
import { COMPONENT_CONFIGS } from '../../types';
import type { ComponentType } from '../../types';

interface ScoreData {
  score: number;
  percentage: number;
  feedback: string;
  quality: 'missing' | 'poor' | 'needs_work' | 'okay' | 'good' | 'excellent';
}

interface CustomNodeProps {
  id: string;
  data: {
    description: string;
    onDescriptionChange: (id: string, description: string) => void;
    scoreData?: ScoreData;
  };
  type: ComponentType;
}

function CustomNode({ id, data, type }: CustomNodeProps) {
  const config = COMPONENT_CONFIGS[type];
  const [isEditing, setIsEditing] = useState(false);
  const [description, setDescription] = useState(data.description || '');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.select();
    }
  }, [isEditing]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [description]);

  const handleBlur = () => {
    setIsEditing(false);
    data.onDescriptionChange(id, description);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setIsEditing(false);
      setDescription(data.description || '');
    }
  };

  return (
    <div className="group relative">
      {/* Glow effect */}
      <div
        className="absolute -inset-1 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-xl"
        style={{ background: `${config.color}30` }}
      />

      {/* Main card */}
      <div
        className="relative min-w-[200px] max-w-[280px] rounded-xl overflow-hidden backdrop-blur-sm"
        style={{
          background: `linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.85) 100%)`,
          border: `1px solid ${config.color}40`,
          boxShadow: `0 4px 24px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.05) inset`,
        }}
      >
        {/* Top accent line */}
        <div
          className="absolute top-0 left-0 right-0 h-[2px]"
          style={{
            background: `linear-gradient(90deg, transparent, ${config.color}, transparent)`,
          }}
        />

        <Handle
          type="target"
          position={Position.Top}
          className="!w-3 !h-3 !border-2 !border-[#0f172a]"
          style={{ background: config.color }}
        />

        {/* Header */}
        <div
          className="px-4 py-3 flex items-center gap-3"
          style={{
            background: `linear-gradient(135deg, ${config.color}15, transparent)`,
            borderBottom: `1px solid ${config.color}20`,
          }}
        >
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-base"
            style={{
              background: `linear-gradient(135deg, ${config.color}30, ${config.color}10)`,
              boxShadow: `0 0 16px ${config.color}30`,
            }}
          >
            {config.icon}
          </div>
          <span
            className="font-semibold text-sm tracking-wide"
            style={{ color: config.color }}
          >
            {config.label}
          </span>
        </div>

        {/* Content */}
        <div className="p-4">
          {isEditing ? (
            <textarea
              ref={textareaRef}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              onBlur={handleBlur}
              onKeyDown={handleKeyDown}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm text-white/90 resize-none focus:outline-none focus:border-white/30 placeholder-white/30 transition-colors"
              placeholder="Describe this component..."
              rows={2}
            />
          ) : (
            <div
              onClick={() => setIsEditing(true)}
              className="cursor-text text-sm min-h-[44px] px-3 py-2 rounded-lg bg-black/20 border border-transparent hover:border-white/10 transition-all"
            >
              {description ? (
                <span className="text-white/80">{description}</span>
              ) : (
                <span className="text-white/30 italic">Click to describe...</span>
              )}
            </div>
          )}

          {/* Score Display - Compact inline version */}
          {data.scoreData && (
            <div className="mt-2 flex items-center gap-2 group/score" title={data.scoreData.feedback}>
              <div className="flex-1 h-1.5 bg-black/30 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    data.scoreData.quality === 'excellent' ? 'bg-emerald-500' :
                    data.scoreData.quality === 'good' ? 'bg-green-500' :
                    data.scoreData.quality === 'okay' ? 'bg-yellow-500' :
                    data.scoreData.quality === 'needs_work' ? 'bg-orange-500' :
                    'bg-red-500'
                  }`}
                  style={{ width: `${data.scoreData.percentage}%` }}
                />
              </div>
              <span className={`text-[10px] font-bold min-w-[32px] text-right cursor-help ${
                data.scoreData.quality === 'excellent' ? 'text-emerald-400' :
                data.scoreData.quality === 'good' ? 'text-green-400' :
                data.scoreData.quality === 'okay' ? 'text-yellow-400' :
                data.scoreData.quality === 'needs_work' ? 'text-orange-400' :
                'text-red-400'
              }`}>
                {data.scoreData.percentage}%
              </span>
            </div>
          )}
        </div>

        <Handle
          type="source"
          position={Position.Bottom}
          className="!w-3 !h-3 !border-2 !border-[#0f172a]"
          style={{ background: config.color }}
        />
      </div>
    </div>
  );
}

export default memo(CustomNode);
