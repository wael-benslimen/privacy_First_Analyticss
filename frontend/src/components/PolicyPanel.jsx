import React from 'react';
import { ShieldCheck } from 'lucide-react';

const PolicyPanel = ({ policy }) => {
    if (!policy) return <div className="text-white">Loading policy...</div>;

    const data = {
        total_budget: policy.total_budget,
        remaining_budget: policy.remaining_budget,
        is_warning: policy.is_warning,
        last_reset: new Date(policy.last_reset).toLocaleDateString()
    };

    return (
        <div className="bg-slate-900 rounded-2xl shadow-lg overflow-hidden text-slate-300">
            <div className="p-6 border-b border-slate-800 flex items-center justify-between">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <ShieldCheck className="w-5 h-5 text-green-500" />
                    Privacy Budget Status
                </h2>
                <span className={`text-xs font-mono px-2 py-1 rounded ${data.remaining_budget < 1.0 ? 'bg-red-900 text-red-100' : 'bg-slate-800 text-slate-400'}`}>
                    Remaining: {data.remaining_budget.toFixed(2)}
                </span>
            </div>
            <div className="p-6 font-mono text-sm overflow-x-auto">
                <pre className="text-blue-300">
                    {JSON.stringify(data, null, 2)}
                </pre>
            </div>
            <div className="px-6 py-4 bg-slate-800/50 border-t border-slate-800 text-xs text-slate-500 flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${data.remaining_budget > 0 ? 'bg-green-500 animate-pulse' : 'bg-red-500'} `} />
                {data.remaining_budget > 0 ? 'Budget active' : 'Budget depleted'}
            </div>
        </div>
    );
};

export default PolicyPanel;
