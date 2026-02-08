import { useState } from 'react';
import { X } from 'lucide-react';
import type { Question } from '../types';

interface QuestionModalProps {
  questions: Question[];
  onComplete: (answers: Record<string, string>) => void;
  onClose: () => void;
  isLoading: boolean;
}

export default function QuestionModal({
  questions,
  onComplete,
  onClose,
  isLoading,
}: QuestionModalProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const currentQuestion = questions[currentStep];
  const isLastStep = currentStep === questions.length - 1;

  const handleSelect = (optionLabel: string) => {
    setAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: optionLabel,
    }));
  };

  const handleNext = () => {
    if (isLastStep) {
      onComplete(answers);
    } else {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handleSkip = () => {
    if (isLastStep) {
      onComplete(answers);
    } else {
      setCurrentStep((prev) => prev + 1);
    }
  };

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in">
        <div className="bg-[#0f1629]/90 backdrop-blur-xl rounded-3xl p-10 max-w-md w-full mx-4 border border-white/10 shadow-2xl">
          <div className="flex flex-col items-center gap-6">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg" />
              </div>
            </div>
            <div className="text-center">
              <p className="text-white/90 font-medium">Generating your prompt...</p>
              <p className="text-white/40 text-sm mt-1">Analyzing architecture & preferences</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in">
      <div className="bg-[#0f1629]/90 backdrop-blur-xl rounded-3xl max-w-lg w-full mx-4 border border-white/10 shadow-2xl overflow-hidden animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-white/5">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              {questions.map((_, i) => (
                <div
                  key={i}
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    i < currentStep
                      ? 'w-6 bg-indigo-500'
                      : i === currentStep
                      ? 'w-6 bg-gradient-to-r from-indigo-500 to-purple-500'
                      : 'w-1.5 bg-white/20'
                  }`}
                />
              ))}
            </div>
            <span className="text-xs text-white/40 font-medium">
              {currentStep + 1} of {questions.length}
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/5 rounded-xl transition-colors"
          >
            <X className="w-5 h-5 text-white/40 hover:text-white/80" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <h3 className="text-xl font-semibold mb-6 text-white">
            {currentQuestion.question}
          </h3>

          <div className="flex flex-col gap-3">
            {currentQuestion.options.map((option) => {
              const isSelected = answers[currentQuestion.id] === option.label;
              return (
                <button
                  key={option.label}
                  onClick={() => handleSelect(option.label)}
                  className={`group p-4 rounded-2xl border text-left transition-all duration-200 ${
                    isSelected
                      ? 'border-indigo-500/50 bg-indigo-500/10'
                      : 'border-white/10 hover:border-white/20 hover:bg-white/5'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className={`font-medium ${isSelected ? 'text-white' : 'text-white/80'}`}>
                      {option.label}
                    </span>
                    <div
                      className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all ${
                        isSelected
                          ? 'border-indigo-500 bg-indigo-500'
                          : 'border-white/20 group-hover:border-white/40'
                      }`}
                    >
                      {isSelected && (
                        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </div>
                  {option.description && (
                    <p className={`text-sm mt-1.5 ${isSelected ? 'text-white/60' : 'text-white/40'}`}>
                      {option.description}
                    </p>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-between items-center px-6 py-5 border-t border-white/5 bg-white/[0.02]">
          <button
            onClick={handleSkip}
            className="px-4 py-2 text-white/40 hover:text-white/80 text-sm font-medium transition-colors"
          >
            Skip
          </button>
          <button
            onClick={handleNext}
            disabled={!answers[currentQuestion.id]}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl font-medium text-white transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            style={{
              background: answers[currentQuestion.id]
                ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)'
                : 'rgba(255, 255, 255, 0.1)',
            }}
          >
            <span>{isLastStep ? 'Generate' : 'Next'}</span>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
