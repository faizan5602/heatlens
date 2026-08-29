import React from 'react';
import { CorrelationPair } from '../types/heatlens';

interface CorrelationMatrixProps {
  correlations: CorrelationPair[];
  correlationMatrix: Record<string, Record<string, number>>;
}

const formatVariable = (variable: string) => variable.replace(/_/g, ' ');

const getCellColor = (value: number) => {
  const intensity = Math.min(Math.abs(value), 1);
  if (value >= 0) return `rgba(239, 68, 68, ${0.12 + intensity * 0.55})`;
  return `rgba(59, 130, 246, ${0.12 + intensity * 0.55})`;
};

export const CorrelationMatrix: React.FC<CorrelationMatrixProps> = ({ correlations, correlationMatrix }) => {
  const variables = Object.keys(correlationMatrix);
  const keyPairs = correlations.slice(0, 4);

  return (
    <section className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
      <div className="flex items-start justify-between gap-4 mb-5">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">Correlation Matrix</h3>
          <p className="text-xs text-slate-500 mt-1">Pearson relationship across measured signals</p>
        </div>
        <span className="text-xs text-slate-500">r coefficient</span>
      </div>
      {variables.length > 0 && (
        <div className="overflow-x-auto mb-5">
          <div className="grid gap-1 min-w-[360px]" style={{ gridTemplateColumns: `minmax(110px, 1.4fr) repeat(${variables.length}, minmax(48px, 1fr))` }}>
            <div />
            {variables.map((variable) => <div key={variable} className="text-[10px] text-slate-500 text-center truncate px-1" title={formatVariable(variable)}>{formatVariable(variable)}</div>)}
            {variables.map((row) => (
              <React.Fragment key={row}>
                <div className="text-[10px] text-slate-400 truncate flex items-center" title={formatVariable(row)}>{formatVariable(row)}</div>
                {variables.map((column) => {
                  const value = correlationMatrix[row]?.[column] ?? 0;
                  return <div key={`${row}-${column}`} className="h-10 flex items-center justify-center rounded text-[10px] font-mono text-white" style={{ backgroundColor: getCellColor(value) }}>{value.toFixed(2)}</div>;
                })}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}
      <div className="space-y-2 pt-4 border-t border-slate-800">
        {keyPairs.length === 0 && <span className="text-xs text-slate-500">No correlation pairs available.</span>}
        {keyPairs.map((pair) => (
          <div key={`${pair.variable_x}-${pair.variable_y}`} className="flex items-center justify-between gap-3 text-xs">
            <span className="text-slate-300 truncate">{formatVariable(pair.variable_x)} <span className="text-slate-600">↔</span> {formatVariable(pair.variable_y)}</span>
            <span className={`shrink-0 px-2 py-1 rounded border font-semibold ${pair.coefficient >= 0 ? 'bg-red-500/10 text-red-400 border-red-500/20' : 'bg-blue-500/10 text-blue-400 border-blue-500/20'}`}>
              {pair.coefficient >= 0 ? 'Positive' : 'Negative'} · {pair.coefficient.toFixed(2)}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
};
