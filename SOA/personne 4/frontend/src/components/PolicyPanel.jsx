import React from 'react';
import { ShieldCheck } from 'lucide-react';

const PolicyPanel = () => {
    const policy = {
        version: "1.2.0",
        global_epsilon_limit: 10.0,
        max_queries_per_hour: 50,
        allowed_mechanisms: ["laplace", "gaussian", "exponential"],
        restricted_columns: ["ssn", "email", "phone"],
        min_cohort_size: 100
    };

    return (
        <div className="bg-slate-900 rounded-2xl shadow-lg overflow-hidden text-slate-300">
            <div className="p-6 border-b border-slate-800 flex items-center justify-between">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <ShieldCheck className="w-5 h-5 text-green-500" />
                    Active Privacy Policy
                </h2>
                <span className="text-xs font-mono bg-slate-800 px-2 py-1 rounded text-slate-400">v{policy.version}</span>
            </div>
            <div className="p-6 font-mono text-sm overflow-x-auto">
                <pre className="text-blue-300">
                    {JSON.stringify(policy, null, 2)}
                </pre>
            </div>
            <div className="px-6 py-4 bg-slate-800/50 border-t border-slate-800 text-xs text-slate-500 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                Policy enforcement active
            </div>
        </div>
    );
};

export default PolicyPanel;
