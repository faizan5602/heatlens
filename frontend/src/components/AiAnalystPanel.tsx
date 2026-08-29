import React, { useState } from 'react';
import { queryAiAnalyst } from '../services/api';

export const AiAnalystPanel: React.FC<{ context: any }> = ({ context }) => {
  const [query, setQuery] = useState('');
  const [chat, setChat] = useState<Array<{ sender: string; text: string }>>([]);
  const [loading, setLoading] = useState(false);
  const [cooldown, setCooldown] = useState(false);

  const handleSend = async () => {
    if (!query.trim() || loading || cooldown) return;

    const userQ = query.trim().slice(0, 300);
    setQuery('');
    setChat((prev) => [...prev, { sender: 'user', text: userQ }]);
    setLoading(true);
    setCooldown(true);
    window.setTimeout(() => setCooldown(false), 3000);

    try {
      const ans = await queryAiAnalyst(userQ, context);
      setChat((prev) => [...prev, { sender: 'ai', text: ans }]);
    } catch (err: any) {
      setChat((prev) => [...prev, { sender: 'ai', text: `Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl flex flex-col h-96">
      <div className="flex items-center space-x-2 mb-4">
        <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        <h3 className="text-sm font-semibold text-slate-200">AI Analyst</h3>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-2 text-xs mb-4">
        {chat.length === 0 && (
          <p className="text-slate-500 italic">Ask questions like: "Is humidity correlated with heat?" or "Why is exposure high?"</p>
        )}
        {chat.map((msg, i) => (
          <div key={i} className={`p-3 rounded-lg ${msg.sender === 'user' ? 'bg-slate-800 text-slate-200 ml-8' : 'bg-slate-950 text-emerald-300 mr-8 border border-slate-800'}`}>
            {msg.text}
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          maxLength={300}
          onChange={(e) => setQuery(e.target.value.slice(0, 300))}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask AI Analyst..."
          className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-slate-600"
        />
        <button
          onClick={handleSend}
          disabled={loading || cooldown}
          className="bg-red-600 hover:bg-red-500 text-white font-semibold text-xs px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
        >
          {loading ? 'Analyzing...' : cooldown ? 'Wait...' : 'Ask'}
        </button>
      </div>
    </div>
  );
};
