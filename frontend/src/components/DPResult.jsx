import React from 'react';
import { Lock, Unlock, AlertTriangle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const DPResult = ({ result }) => {
    if (!result) return (
        <div className="h-full flex flex-col items-center justify-center text-slate-400 p-12 border-2 border-dashed border-slate-200 rounded-2xl">
            <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                <BarChart className="w-8 h-8 text-slate-300" />
            </div>
            <p className="font-medium">No analysis results yet</p>
            <p className="text-sm">Configure parameters and run analysis to see results</p>
        </div>
    );

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                    <div className="flex items-center gap-2 mb-2 text-slate-500 text-sm font-medium">
                        <Unlock className="w-4 h-4" />
                        <span>Raw Value</span>
                    </div>
                    <div className="text-2xl font-bold text-slate-900 blur-sm select-none hover:blur-none transition-all duration-300 cursor-pointer" title="Hover to reveal">
                        {result.rawValue}
                    </div>
                </div>

                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-5 rounded-2xl shadow-sm border border-blue-100">
                    <div className="flex items-center gap-2 mb-2 text-blue-600 text-sm font-medium">
                        <Lock className="w-4 h-4" />
                        <span>Private Result</span>
                    </div>
                    <div className="text-3xl font-bold text-blue-700">
                        {result.privateValue}
                    </div>
                    <div className="text-xs text-blue-500 mt-1">
                        ± {result.uncertainty} (95% CI)
                    </div>
                </div>

                <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                    <div className="flex items-center gap-2 mb-2 text-slate-500 text-sm font-medium">
                        <AlertTriangle className="w-4 h-4" />
                        <span>Noise Added</span>
                    </div>
                    <div className="text-2xl font-bold text-slate-700 font-mono">
                        {result.noise > 0 ? '+' : ''}{result.noise}
                    </div>
                </div>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 h-80">
                <h3 className="text-sm font-bold text-slate-900 mb-6">Distribution Analysis</h3>
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={result.chartData}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                        <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dy={10} />
                        <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                        <Tooltip
                            cursor={{ fill: '#f1f5f9' }}
                            contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        />
                        <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default DPResult;
