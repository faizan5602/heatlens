import React from 'react';
import { AnomalyPoint } from '../types/heatlens';

export const AnomalyPanel: React.FC<{ anomalies: AnomalyPoint[] }> = ({ anomalies }) => (
  <section className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
    <div className="flex items-center justify-between mb-5">
      <div>
        <h3 className="text-sm font-semibold text-slate-200">Anomaly Inspection</h3>
        <p className="text-xs text-slate-500 mt-1">Z-score deviations from baseline</p>
      </div>
      <span className={`px-2 py-1 rounded border text-xs font-semibold ${anomalies.length ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'}`}>
        {anomalies.length ? `${anomalies.length} detected` : 'No anomalies'}
      </span>
    </div>
    {anomalies.length === 0 ? (
      <div className="border border-dashed border-slate-800 rounded-lg py-8 text-center text-xs text-slate-500">All observed points remain within the expected range.</div>
    ) : (
      <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
        {anomalies.map((anomaly, index) => (
          <div key={`${anomaly.timestamp}-${anomaly.variable}-${index}`} className="grid grid-cols-[1.3fr_0.8fr_0.8fr_0.8fr] gap-3 items-center bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs">
            <div className="min-w-0"><span className="text-slate-300 block truncate">{anomaly.variable.replace(/_/g, ' ')}</span><span className="text-slate-600 block truncate">{anomaly.timestamp}</span></div>
            <div><span className="text-slate-600 block">Observed</span><span className="text-slate-200 font-mono">{anomaly.observed_value.toFixed(2)}</span></div>
            <div><span className="text-slate-600 block">Baseline</span><span className="text-slate-200 font-mono">{anomaly.baseline_mean.toFixed(2)}</span></div>
            <div><span className="text-slate-600 block">Deviation</span><span className="text-orange-400 font-mono">{anomaly.deviation.toFixed(2)}</span></div>
          </div>
        ))}
      </div>
    )}
  </section>
);
