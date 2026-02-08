import { COMPONENT_CONFIGS } from '../types';
import type { ComponentType } from '../types';

interface ComponentPaletteProps {
  onDragStart: (event: React.DragEvent, nodeType: ComponentType) => void;
}

export default function ComponentPalette({ onDragStart }: ComponentPaletteProps) {
  const components = Object.values(COMPONENT_CONFIGS);

  return (
    <div className="w-[240px] h-full bg-[#0a0f1a]/80 backdrop-blur-xl border-r border-white/5 flex flex-col">
      {/* Header */}
      <div className="p-5 border-b border-white/5">
        <h2 className="text-sm font-semibold text-white/90 tracking-wide uppercase">Components</h2>
        <p className="text-xs text-white/40 mt-1.5 leading-relaxed">
          Drag onto canvas to build
        </p>
      </div>

      {/* Components List */}
      <div className="flex-1 p-4 space-y-2 overflow-y-auto">
        {components.map((config) => (
          <div
            key={config.type}
            draggable
            onDragStart={(e) => onDragStart(e, config.type)}
            className="group relative flex items-center gap-3 p-3.5 rounded-xl cursor-grab active:cursor-grabbing transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
            style={{
              background: `linear-gradient(135deg, ${config.color}15, ${config.color}05)`,
              border: `1px solid ${config.color}25`,
            }}
          >
            {/* Glow effect on hover */}
            <div
              className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
              style={{
                background: `radial-gradient(circle at center, ${config.color}20, transparent 70%)`,
              }}
            />

            {/* Icon container */}
            <div
              className="relative w-10 h-10 rounded-lg flex items-center justify-center text-xl"
              style={{
                background: `linear-gradient(135deg, ${config.color}30, ${config.color}10)`,
                boxShadow: `0 0 20px ${config.color}20`,
              }}
            >
              {config.icon}
            </div>

            {/* Label */}
            <div className="relative flex-1">
              <span
                className="font-medium text-sm"
                style={{ color: config.color }}
              >
                {config.label}
              </span>
            </div>

            {/* Drag indicator */}
            <div className="relative flex flex-col gap-0.5 opacity-30 group-hover:opacity-60 transition-opacity">
              <div className="flex gap-0.5">
                <div className="w-1 h-1 rounded-full bg-white/60" />
                <div className="w-1 h-1 rounded-full bg-white/60" />
              </div>
              <div className="flex gap-0.5">
                <div className="w-1 h-1 rounded-full bg-white/60" />
                <div className="w-1 h-1 rounded-full bg-white/60" />
              </div>
              <div className="flex gap-0.5">
                <div className="w-1 h-1 rounded-full bg-white/60" />
                <div className="w-1 h-1 rounded-full bg-white/60" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer tip */}
      <div className="p-4 border-t border-white/5">
        <div className="flex items-start gap-2 text-[11px] text-white/30 leading-relaxed">
          <svg className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Connect nodes by dragging between handles</span>
        </div>
      </div>
    </div>
  );
}
