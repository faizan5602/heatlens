import React from 'react';
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

interface TimelineSeries {
  dataKey: string;
  name: string;
  color: string;
  strokeWidth?: number;
  strokeDasharray?: string;
}

const defaultSeries: TimelineSeries[] = [
  { dataKey: 'temperature', name: 'Temperature', color: '#ef4444', strokeWidth: 2 },
  { dataKey: 'heat_index', name: 'Heat Index', color: '#f97316', strokeWidth: 1.5, strokeDasharray: '4 4' },
];

export const HeatTimelineChart: React.FC<{ data: any[]; series?: TimelineSeries[]; title?: string }> = ({ data, series = defaultSeries, title = 'Temperature & Heat Index Timeline (°C)' }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl h-80">
      <h3 className="text-sm font-semibold text-slate-300 mb-4">{title}</h3>
      <div className="h-[calc(100%-2rem)] min-h-0">
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          <LineChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="timestamp" stroke="#64748b" tickFormatter={(t) => String(t).split('T')[1]?.slice(0, 5) || String(t)} />
            <YAxis stroke="#64748b" domain={['auto', 'auto']} />
            <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
            {series.map((line) => (
              <Line key={line.dataKey} type="monotone" dataKey={line.dataKey} stroke={line.color} strokeWidth={line.strokeWidth ?? 2} dot={false} strokeDasharray={line.strokeDasharray} name={line.name} connectNulls />
            ))}
            {series.length > 1 && <Legend wrapperStyle={{ fontSize: '11px' }} />}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
