import React, { useMemo, useState } from 'react';
import { Activity, ArrowLeft, ArrowRight, BarChart3, BrainCircuit, Flame, Gauge, Search, ShieldAlert, Sparkles, ThermometerSun } from 'lucide-react';

import { AiAnalystPanel } from './components/AiAnalystPanel';
import { AnomalyPanel } from './components/AnomalyPanel';
import { CorrelationMatrix } from './components/CorrelationMatrix';
import { HeatTimelineChart } from './components/HeatTimelineChart';
import { ScoreCard } from './components/ScoreCard';
import { runAnalysis } from './services/api';
import { AnalysisResponse } from './types/heatlens';

const popularLocations = ['Downtown District', 'Midtown Area', 'Lakeside Zone', 'Industrial Area'];

const featureCards = [
  { icon: Gauge, title: 'Heat Exposure Score', description: 'A transparent 0–100 score derived from measurable heat conditions.' },
  { icon: ThermometerSun, title: 'Heat Patterns', description: 'Understand temperature intensity and persistence over time.' },
  { icon: BarChart3, title: 'Correlation Analysis', description: 'Discover relationships between temperature, humidity, and heat index signals.' },
  { icon: ShieldAlert, title: 'Anomaly Detection', description: 'Identify unusual temperature behavior using statistical baseline analysis.' },
  { icon: BrainCircuit, title: 'AI Heat Analyst', description: 'Ask questions about analyzed data and receive grounded explanations.' },
];

const howItWorks = [
  { step: '01', title: 'Collect', text: 'FortyGuard provides hyperlocal environmental observations.' },
  { step: '02', title: 'Analyze', text: 'HeatLens calculates heat intensity, persistence, anomalies, and exposure.' },
  { step: '03', title: 'Understand', text: 'AI interprets the calculated statistical results in human-readable language.' },
  { step: '04', title: 'Explore', text: 'Users investigate patterns and compare locations with confidence.' },
];

const getMetricValue = (entry: Record<string, any> | undefined, key: string) => {
  if (!entry) return null;
  const value = entry[key];
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string') {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
};

const formatNumber = (value: number | null | undefined, digits = 2) => value == null ? 'N/A' : value.toFixed(digits);

const compareTimelineData = (a: AnalysisResponse | null, b: AnalysisResponse | null) => {
  if (!a || !b) return [] as Array<Record<string, any>>;

  const map = new Map<string, Record<string, any>>();
  a.timeseries_data.forEach((point) => {
    const ts = String(point.timestamp || point.datetime || '');
    map.set(ts, { timestamp: ts, aTemperature: getMetricValue(point, 'temperature'), aHeatIndex: getMetricValue(point, 'heat_index') });
  });

  b.timeseries_data.forEach((point) => {
    const ts = String(point.timestamp || point.datetime || '');
    const current = map.get(ts) ?? { timestamp: ts, aTemperature: null, aHeatIndex: null };
    current.bTemperature = getMetricValue(point, 'temperature');
    current.bHeatIndex = getMetricValue(point, 'heat_index');
    map.set(ts, current);
  });

  return Array.from(map.values()).sort((left, right) => String(left.timestamp).localeCompare(String(right.timestamp))).slice(0, 48);
};

export const App: React.FC = () => {
  const [view, setView] = useState<'landing' | 'dashboard'>('landing');
  const [location, setLocation] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('');
  const [data, setData] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [compareMode, setCompareMode] = useState(false);
  const [comparisonLocation, setComparisonLocation] = useState('Industrial Area');
  const [comparisonData, setComparisonData] = useState<AnalysisResponse | null>(null);
  const [comparisonLoading, setComparisonLoading] = useState(false);

  const comparisonChartData = useMemo(() => compareTimelineData(data, comparisonData), [data, comparisonData]);

  const fetchAnalysis = async (loc: string) => {
    const trimmed = loc.trim();
    if (!trimmed) {
      setError('Please enter a location to analyze.');
      return false;
    }

    setLoading(true);
    setError('');

    try {
      const res = await runAnalysis(trimmed);
      setSelectedLocation(trimmed);
      setLocation(trimmed);
      setData(res);
      setComparisonData(null);
      setCompareMode(false);
      setView('dashboard');
      window.requestAnimationFrame(() => document.getElementById('dashboard')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
      return true;
    } catch (err: any) {
      setError(err?.message || 'Unable to analyze this location right now. Please try again.');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (event?: React.FormEvent) => {
    event?.preventDefault();
    await fetchAnalysis(location);
  };

  const fetchComparison = async () => {
    const target = comparisonLocation.trim();
    if (!target || target === selectedLocation.trim()) return;

    setComparisonLoading(true);
    try {
      const result = await runAnalysis(target);
      setComparisonData(result);
    } catch (err: any) {
      setError(err?.message || 'Unable to compare this location right now. Please try again.');
    } finally {
      setComparisonLoading(false);
    }
  };

  const returnHome = () => {
    setView('landing');
    setError('');
    setCompareMode(false);
    setComparisonData(null);
    setSelectedLocation('');
    setData(null);
    setLocation('');
  };

  const renderLandingPage = () => (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <a href="#home" className="flex items-center gap-3">
            <Flame className="h-8 w-8 fill-orange-500 text-red-500" aria-hidden="true" />
            <div className="text-base font-black tracking-[0.22em]"><span className="text-red-500">HEAT</span> <span className="text-white">LENS</span></div>
          </a>

          <nav className="hidden items-center gap-8 text-sm text-slate-300 md:flex">
            <a href="#home" className="transition hover:text-white">Home</a>
            <a href="#how-it-works" className="transition hover:text-white">How It Works</a>
            <a href="#features" className="transition hover:text-white">Features</a>
            <a href="#analysis" className="transition hover:text-white">Analyze</a>
          </nav>

          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1 text-[10px] font-medium text-emerald-300 sm:flex">
              <span className="h-2 w-2 rounded-full bg-emerald-400" />
              Live Data
            </div>
          </div>
        </div>
      </header>

      <main>
        <section id="home" className="relative overflow-hidden">
          <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top,_rgba(239,68,68,0.16),transparent_22%),radial-gradient(circle_at_bottom_right,_rgba(59,130,246,0.12),transparent_26%)]" />
          <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8 lg:py-20">
            <div className="mx-auto max-w-4xl text-center">
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/80 px-3 py-1.5 text-[11px] font-medium uppercase tracking-[0.2em] text-slate-300">
                <Sparkles className="h-3.5 w-3.5 text-orange-400" />
                Hyperlocal Heat Intelligence
              </div>

              <h1 className="text-4xl font-black leading-tight tracking-[-0.05em] text-white sm:text-5xl lg:text-6xl">
                Understand Heat.<br />
                <span className="text-red-400">Before It Becomes a Problem.</span>
              </h1>

              <p className="mx-auto mt-6 max-w-2xl text-base text-slate-300 sm:text-lg">
                HeatLens transforms hyperlocal temperature data into meaningful intelligence — revealing intensity, persistence, anomalies, and relationships that ordinary weather dashboards miss.
              </p>

              <div className="mt-8 flex flex-wrap items-center justify-center gap-3 text-[11px] uppercase tracking-[0.18em] text-slate-400">
                <span className="rounded-full border border-slate-800 bg-slate-900 px-3 py-2">Real-time Data</span>
                <span className="rounded-full border border-slate-800 bg-slate-900 px-3 py-2">Statistical Analysis</span>
                <span className="rounded-full border border-slate-800 bg-slate-900 px-3 py-2">AI-Powered Insights</span>
              </div>

              <div id="analysis" className="mx-auto mt-10 max-w-3xl rounded-2xl border border-slate-800 bg-slate-900/85 p-4 shadow-2xl shadow-slate-950/40 sm:p-5">
                <div className="mb-4 text-left">
                  <h2 className="text-2xl font-bold text-white">Analyze Any Location</h2>
                  <p className="mt-1 text-sm text-slate-400">Search for a city, district, or location to start your heat intelligence analysis.</p>
                </div>

                <form onSubmit={handleSubmit} className="flex flex-col gap-3 sm:flex-row sm:items-center">
                  <div className="flex flex-1 items-center gap-3 rounded-xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-left">
                    <Search className="h-4 w-4 text-slate-400" />
                    <input
                      type="text"
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      placeholder="Search a supported US district or area..."
                      className="w-full bg-transparent text-sm text-white placeholder:text-slate-500 focus:outline-none"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-red-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-70"
                  >
                    {loading ? 'Analyzing...' : 'Analyze'}
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </form>

                {error && (
                  <div className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-left text-sm text-red-300">
                    {error}
                  </div>
                )}

                {loading && (
                  <div className="mt-4 flex items-center justify-center gap-2 rounded-lg border border-slate-800 bg-slate-950/80 px-3 py-2 text-sm text-slate-300">
                    <Activity className="h-4 w-4 animate-pulse text-orange-400" />
                    Analyzing location...
                  </div>
                )}

                <div className="mt-5 flex flex-wrap items-center gap-2 text-xs text-slate-400">
                  <span className="mr-2 text-slate-500">Popular:</span>
                  {popularLocations.map((item) => (
                    <button
                      key={item}
                      type="button"
                      onClick={() => {
                        setLocation(item);
                        void fetchAnalysis(item);
                      }}
                      className="rounded-full border border-slate-700 bg-slate-950 px-2.5 py-1.5 transition hover:border-slate-500 hover:text-slate-200"
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
          <div className="mb-12 text-center">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400">How It Works</p>
            <h2 className="mt-4 text-3xl font-bold text-white">From Data to Actionable Intelligence</h2>
          </div>

          <div className="grid gap-5 md:grid-cols-4">
            {howItWorks.map((item) => (
              <div key={item.step} className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl shadow-slate-950/20">
                <div className="mb-4 text-xs font-semibold uppercase tracking-[0.2em] text-red-400">{item.step}</div>
                <h3 className="mb-3 text-xl font-bold text-white">{item.title}</h3>
                <p className="text-sm leading-relaxed text-slate-300">{item.text}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="features" className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
          <div className="mb-12 text-center">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400">Key Features</p>
            <h2 className="mt-4 text-3xl font-bold text-white">Powerful Insights for a Safer Tomorrow</h2>
          </div>

          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-5">
            {featureCards.map(({ icon: Icon, title, description }) => (
              <div key={title} className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl shadow-slate-950/20 transition hover:-translate-y-1 hover:border-slate-700">
                <div className="mb-5 inline-flex h-12 w-12 items-center justify-center rounded-xl border border-slate-700 bg-slate-950 text-red-400">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="mb-3 text-base font-semibold text-white">{title}</h3>
                <p className="text-sm leading-relaxed text-slate-300">{description}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-4 pb-24 sm:px-6 lg:px-8">
          <div className="rounded-3xl border border-red-500/30 bg-gradient-to-r from-red-600/20 via-orange-600/10 to-slate-900 p-8 shadow-2xl shadow-red-950/20 sm:p-10">
            <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.28em] text-red-200">Ready to explore heat intelligence?</p>
                <h3 className="mt-3 text-3xl font-black tracking-[-0.04em] text-white">Ready to Explore Heat Intelligence?</h3>
              </div>

              <button
                onClick={() => document.getElementById('analysis')?.scrollIntoView({ behavior: 'smooth', block: 'start' })}
                className="inline-flex items-center justify-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
              >
                Analyze a Location
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );

  const renderComparisonPanel = () => {
    if (!data) return null;

    const leftScore = data.heat_exposure_score?.overall_score ?? 0;
    const rightScore = comparisonData?.heat_exposure_score?.overall_score ?? 0;
    const scoreDiff = rightScore - leftScore;
    const scoreSummary = scoreDiff === 0 ? 'Both locations have similar exposure.' : scoreDiff > 0 ? `${comparisonData?.location_name ?? 'Comparison location'} has higher overall heat exposure.` : `${data.location_name} has higher overall heat exposure.`;

    const temperatureKeys = [
      ['temperature', 'Peak Temperature'],
      ['temperature', 'Average Temperature'],
      ['temperature', 'Minimum Temperature'],
      ['temperature', 'Maximum Temperature'],
      ['heat_index', 'Heat Index'],
      ['apparent_temperature', 'Apparent Temperature'],
    ] as const;

    const temperatureMetrics = temperatureKeys.map(([key, label]) => {
      const leftValue = data.descriptive_statistics?.[key]?.max ?? null;
      const rightValue = comparisonData?.descriptive_statistics?.[key]?.max ?? null;
      return { label, leftValue, rightValue };
    }).filter((metric) => metric.leftValue !== null || metric.rightValue !== null);

    return (
      <div className="space-y-6">
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl shadow-slate-950/30">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Comparison Result</p>
              <h3 className="mt-2 text-2xl font-bold text-white">{scoreSummary}</h3>
            </div>
            <div className="rounded-full border border-orange-500/30 bg-orange-500/10 px-3 py-2 text-sm font-semibold text-orange-200">
              {scoreDiff >= 0 ? '+' : ''}{scoreDiff} points
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {[data, comparisonData ?? data].map((item, index) => (
              <div key={`${item.location_name}-${index}`} className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                <div className="mb-3 text-sm font-semibold text-white">{item.location_name}</div>
                <div className="grid grid-cols-3 gap-3 text-xs">
                  <div>
                    <span className="block text-slate-500">Exposure</span>
                    <span className="text-lg font-bold text-red-400">{item.heat_exposure_score.overall_score}</span>
                  </div>
                  <div>
                    <span className="block text-slate-500">Intensity</span>
                    <span className="text-lg font-bold text-slate-100">{item.heat_exposure_score.breakdown.intensity_component}</span>
                  </div>
                  <div>
                    <span className="block text-slate-500">Persistence</span>
                    <span className="text-lg font-bold text-orange-400">{item.heat_exposure_score.breakdown.persistence_component}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl shadow-slate-950/30">
            <h3 className="mb-4 text-sm font-semibold text-slate-200">Temperature & Heat Metrics</h3>
            <div className="space-y-3">
              {temperatureMetrics.map((metric) => (
                <div key={metric.label} className="grid grid-cols-[1.4fr_1fr_1fr] items-center gap-3 border-b border-slate-800 pb-2 text-xs">
                  <span className="text-slate-300">{metric.label}</span>
                  <span className="text-slate-100 font-mono">{formatNumber(metric.leftValue, 2)}</span>
                  <span className="text-slate-100 font-mono">{formatNumber(metric.rightValue, 2)}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl shadow-slate-950/30">
            <h3 className="mb-4 text-sm font-semibold text-slate-200">Heat Persistence & Anomalies</h3>
            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-[1.4fr_1fr_1fr] gap-3 border-b border-slate-800 pb-2">
                <span className="text-slate-300">Longest Hot Spell</span>
                <span className="font-mono text-slate-100">{data.persistence.longest_continuous_hot_spell_hours}h</span>
                <span className="font-mono text-slate-100">{comparisonData?.persistence.longest_continuous_hot_spell_hours ?? 'N/A'}h</span>
              </div>
              <div className="grid grid-cols-[1.4fr_1fr_1fr] gap-3 border-b border-slate-800 pb-2">
                <span className="text-slate-300">Persistence Factor</span>
                <span className="font-mono text-slate-100">{data.heat_exposure_score.breakdown.persistence_component}</span>
                <span className="font-mono text-slate-100">{comparisonData?.heat_exposure_score.breakdown.persistence_component ?? 'N/A'}</span>
              </div>
              <div className="grid grid-cols-[1.4fr_1fr_1fr] gap-3 border-b border-slate-800 pb-2">
                <span className="text-slate-300">Anomalies Detected</span>
                <span className="font-mono text-slate-100">{data.anomalies.length}</span>
                <span className="font-mono text-slate-100">{comparisonData?.anomalies.length ?? 'N/A'}</span>
              </div>
              <div className="grid grid-cols-[1.4fr_1fr_1fr] gap-3 border-b border-slate-800 pb-2">
                <span className="text-slate-300">Z-score Baseline</span>
                <span className="font-mono text-slate-100">{data.anomalies[0]?.z_score ? data.anomalies[0].z_score.toFixed(2) : 'No anomalies'}</span>
                <span className="font-mono text-slate-100">{comparisonData?.anomalies[0]?.z_score ? comparisonData.anomalies[0].z_score.toFixed(2) : 'No anomalies'}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl shadow-slate-950/30">
          <h3 className="mb-4 text-sm font-semibold text-slate-200">Correlation Comparison</h3>
          <div className="space-y-3">
            {data.correlations.length === 0 && (!comparisonData || comparisonData.correlations.length === 0) ? (
              <div className="text-xs text-slate-500">No correlation data available for comparison.</div>
            ) : (
              Array.from(new Set([...data.correlations.map((pair) => `${pair.variable_x}|${pair.variable_y}`), ...(comparisonData ? comparisonData.correlations.map((pair) => `${pair.variable_x}|${pair.variable_y}`) : [])])).map((pairKey) => {
                const [x, y] = pairKey.split('|');
                const leftPair = data.correlations.find((entry) => entry.variable_x === x && entry.variable_y === y) ?? data.correlations.find((entry) => entry.variable_x === y && entry.variable_y === x);
                const rightPair = comparisonData?.correlations.find((entry) => entry.variable_x === x && entry.variable_y === y) ?? comparisonData?.correlations.find((entry) => entry.variable_x === y && entry.variable_y === x);

                return (
                  <div key={pairKey} className="grid grid-cols-[1.6fr_1fr_1fr] items-center gap-3 border-b border-slate-800 pb-2 text-xs">
                    <span className="text-slate-300">{x} ↔ {y}</span>
                    <span className="font-mono text-slate-100">{leftPair ? leftPair.coefficient.toFixed(2) : 'N/A'}</span>
                    <span className="font-mono text-slate-100">{rightPair ? rightPair.coefficient.toFixed(2) : 'N/A'}</span>
                  </div>
                );
              })
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl shadow-slate-950/30">
          <HeatTimelineChart
            data={comparisonChartData}
            title="Temperature Timeline Comparison (°C)"
            series={[
              { dataKey: 'aTemperature', name: data.location_name, color: '#ef4444' },
              { dataKey: 'bTemperature', name: comparisonData?.location_name ?? 'Comparison location', color: '#38bdf8' },
            ]}
          />
        </div>
      </div>
    );
  };

  const renderDashboard = () => (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <button onClick={returnHome} className="flex items-center gap-3 text-left">
            <Flame className="h-8 w-8 fill-orange-500 text-red-500" aria-hidden="true" />
            <div className="text-base font-black tracking-[0.22em]"><span className="text-red-500">HEAT</span> <span className="text-white">LENS</span></div>
          </button>

          <div className="flex items-center gap-3">
            <button
              onClick={returnHome}
              className="inline-flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-medium text-slate-200 transition hover:border-slate-500"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              Back to HeatLens
            </button>
          </div>
        </div>
      </header>

      <main id="dashboard" className="mx-auto max-w-7xl space-y-8 px-4 py-8 sm:px-6 lg:px-8">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/85 p-4 shadow-xl shadow-slate-950/30">
          <div className="flex flex-col gap-3 md:flex-row md:items-center">
            <label className="flex-1 text-xs uppercase tracking-[0.18em] text-slate-400">
              Location
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white focus:border-slate-500 focus:outline-none"
              />
            </label>
            <button
              onClick={() => fetchAnalysis(location)}
              disabled={loading}
              className="rounded-xl bg-red-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>

        {loading && (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/80 px-6 py-12 text-center text-slate-300">
            <div className="inline-flex items-center gap-3 rounded-full border border-slate-700 bg-slate-950 px-4 py-2 text-sm">
              <Activity className="h-4 w-4 animate-pulse text-orange-400" />
              Analyzing location...
            </div>
          </div>
        )}

        {error && !loading && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</div>
        )}

        {data && !loading && (
          <>
            <div className="mb-6 flex items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.26em] text-slate-400">Dashboard</p>
                <h2 className="mt-2 text-3xl font-bold text-white">{selectedLocation} Analysis</h2>
              </div>
              <button
                onClick={() => setCompareMode((active) => !active)}
                aria-pressed={compareMode}
                className={`rounded-full border px-4 py-2 text-sm font-medium transition ${compareMode ? 'border-orange-500/40 bg-orange-500/10 text-orange-200' : 'border-slate-700 bg-slate-900 text-slate-200 hover:border-slate-600'}`}
              >
                Compare Location
              </button>
            </div>

            {compareMode && (
              <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl shadow-slate-950/30">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
                  <label className="flex-1 text-xs uppercase tracking-[0.18em] text-slate-400">
                    Compare With
                    <input
                      type="text"
                      value={comparisonLocation}
                      onChange={(e) => setComparisonLocation(e.target.value)}
                      className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white focus:border-slate-500 focus:outline-none"
                    />
                  </label>
                  <button
                    onClick={fetchComparison}
                    disabled={comparisonLoading}
                    className="rounded-xl bg-orange-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-orange-500 disabled:opacity-60"
                  >
                    {comparisonLoading ? 'Comparing...' : 'Compare Locations'}
                  </button>
                </div>
              </section>
            )}

            {compareMode && comparisonData && renderComparisonPanel()}

            {!compareMode && (
              <>
                <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                  <ScoreCard score={data.heat_exposure_score} />

                  <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl shadow-slate-950/30 md:col-span-2">
                    <div>
                      <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Executive AI Interpretation</span>
                      <p className="mt-3 text-sm leading-relaxed text-slate-200">{data.gemini_interpretation}</p>
                    </div>

                    <div className="mt-5 grid grid-cols-3 gap-4 border-t border-slate-800 pt-4 text-xs">
                      <div>
                        <span className="block text-slate-500">Peak Temperature</span>
                        <span className="text-lg font-bold text-slate-100">{data.descriptive_statistics.temperature?.max}°C</span>
                      </div>
                      <div>
                        <span className="block text-slate-500">Longest Hot Spell</span>
                        <span className="text-lg font-bold text-slate-100">{data.persistence.longest_continuous_hot_spell_hours} hrs</span>
                      </div>
                      <div>
                        <span className="block text-slate-500">Anomalies Detected</span>
                        <span className="text-lg font-bold text-slate-100">{data.anomalies.length} points</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                  <HeatTimelineChart data={data.timeseries_data} />
                  <AiAnalystPanel context={data} />
                </div>

                <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                  <CorrelationMatrix correlations={data.correlations} correlationMatrix={data.correlation_matrix} />
                  <AnomalyPanel anomalies={data.anomalies} />
                </div>
              </>
            )}
          </>
        )}
      </main>
    </div>
  );

  return view === 'landing' ? renderLandingPage() : renderDashboard();
};

export default App;
