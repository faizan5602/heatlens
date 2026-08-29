import React from 'react';
import { HeatExposureScore } from '../types/heatlens';

export const ScoreCard: React.FC<{ score: HeatExposureScore }> = ({ score }) => {
  const getBadgeColor = (classification: string) => {
    if (classification.includes('EXTREME')) return 'bg-red-500/20 text-red-400 border-red-500/30';
    if (classification.includes('HIGH')) return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
    return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
      <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
        Heat Exposure Score
      </div>
      <div className="flex items-baseline space-x-3 mb-4">
        <span className="text-5xl font-extrabold text-white">{score.overall_score}</span>
        <span className="text-xl font-medium text-slate-500">/ 100</span>
        <span className={`ml-auto px-3 py-1 rounded-full text-xs font-bold border ${getBadgeColor(score.classification)}`}>
          {score.classification}
        </span>
      </div>

      <div className="space-y-3 pt-4 border-t border-slate-800 text-xs">
        <div>
          <div className="flex justify-between text-slate-400 mb-1">
            <span>Intensity Factor</span>
            <span className="font-mono text-slate-200">{score.breakdown.intensity_component}</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5">
            <div className="bg-red-500 h-1.5 rounded-full" style={{ width: `${score.breakdown.intensity_component}%` }} />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-slate-400 mb-1">
            <span>Persistence Factor</span>
            <span className="font-mono text-slate-200">{score.breakdown.persistence_component}</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5">
            <div className="bg-orange-500 h-1.5 rounded-full" style={{ width: `${score.breakdown.persistence_component}%` }} />
          </div>
        </div>
      </div>
    </div>
  );
};
