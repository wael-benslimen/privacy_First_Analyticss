import React, { useState } from 'react';
import { Sliders, HelpCircle } from 'lucide-react';

const DPForm = ({ onRunAnalysis, isRunning }) => {
    const [epsilon, setEpsilon] = useState(1.0);
    const [delta, setDelta] = useState(0.00001);
    const [sensitivity, setSensitivity] = useState(1);
    const [mechanism, setMechanism] = useState('laplace');

    const handleSubmit = (e) => {
        e.preventDefault();
        onRunAnalysis({
            epsilon: parseFloat(epsilon),
            delta: parseFloat(delta),
            sensitivity: parseFloat(sensitivity),
            mechanism
        });
    };

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                    <Sliders className="w-5 h-5 text-blue-600" />
                    Privacy Parameters
                </h2>
                <button className="text-slate-400 hover:text-blue-600 transition-colors">
                    <HelpCircle className="w-5 h-5" />
                </button>
            </div>

            <form className="space-y-6" onSubmit={handleSubmit}>
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                        Privacy Budget (ε)
                    </label>
                    <div className="flex items-center gap-4">
                        <input
                            type="range"
                            min="0.1"
                            max="10"
                            step="0.1"
                            value={epsilon}
                            onChange={(e) => setEpsilon(e.target.value)}
                            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                        />
                        <span className="w-12 text-right font-mono text-sm font-semibold text-blue-600 bg-blue-50 px-2 py-1 rounded">{epsilon}</span>
                    </div>
                    <p className="text-xs text-slate-500 mt-2">Lower values provide stronger privacy but less utility.</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            Delta (δ)
                        </label>
                        <input
                            type="number"
                            value={delta}
                            onChange={(e) => setDelta(e.target.value)}
                            step="0.00001"
                            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            Sensitivity
                        </label>
                        <input
                            type="number"
                            value={sensitivity}
                            onChange={(e) => setSensitivity(e.target.value)}
                            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                        />
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                        Mechanism
                    </label>
                    <select
                        value={mechanism}
                        onChange={(e) => setMechanism(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                    >
                        <option value="laplace">Laplace Mechanism</option>
                        <option value="gaussian">Gaussian Mechanism</option>
                        <option value="exponential">Exponential Mechanism</option>
                    </select>
                </div>

                <button
                    type="submit"
                    disabled={isRunning}
                    className={`w-full py-3 px-4 rounded-xl text-white font-semibold shadow-lg shadow-blue-500/30 transition-all transform active:scale-95 ${isRunning
                        ? 'bg-slate-400 cursor-not-allowed shadow-none'
                        : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700'
                        }`}
                >
                    {isRunning ? 'Processing...' : 'Run Analysis'}
                </button>
            </form>
        </div>
    );
};

export default DPForm;
