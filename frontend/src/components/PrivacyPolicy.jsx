import React, { useState, useEffect } from 'react';
import { Shield, Info, AlertTriangle } from 'lucide-react';
import { monitoring } from '../services/api';
import PolicyPanel from './PolicyPanel';

const PrivacyPolicy = () => {
    const [policy, setPolicy] = useState(null);

    useEffect(() => {
        const fetchPolicy = async () => {
            try {
                const response = await monitoring.budget();
                setPolicy(response.data);
            } catch (error) {
                console.error('Failed to fetch policy:', error);
            }
        };
        fetchPolicy();
    }, []);

    return (
        <div className="p-8 max-w-5xl mx-auto space-y-8">
            <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
                <Shield className="w-8 h-8 text-blue-600" />
                Privacy Policy & Budget
            </h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Main Budget Panel */}
                <div className="md:col-span-2 space-y-6">
                    <PolicyPanel policy={policy} />

                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                        <h3 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
                            <Info className="w-5 h-5 text-blue-500" />
                            How Differential Privacy Works
                        </h3>
                        <p className="text-slate-600 text-sm leading-relaxed mb-4">
                            Differential Privacy adds carefully calibrated noise to query results to hide whether any individual's data is included in the dataset. This mathematical guarantee allows us to learn about the population while protecting individual privacy.
                        </p>
                        <h4 className="font-semibold text-slate-800 text-sm mb-2">Key Concepts:</h4>
                        <ul className="list-disc list-inside text-sm text-slate-600 space-y-1">
                            <li><strong>Epsilon (ε):</strong> The "privacy loss" parameter. Smaller ε means more privacy but less accuracy.</li>
                            <li><strong>Delta (δ):</strong> The probability that privacy guarantees fail (usually very small, e.g., 10⁻⁵).</li>
                            <li><strong>Sensitivity:</strong> How much one person's data can change the query result.</li>
                        </ul>
                    </div>
                </div>

                {/* Sidebar Info */}
                <div className="space-y-6">
                    <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100">
                        <h3 className="font-bold text-blue-900 mb-2">Available Mechanisms</h3>
                        <div className="space-y-3">
                            <div className="bg-white p-3 rounded-lg shadow-sm">
                                <span className="block font-medium text-slate-900 text-sm">Laplace Mechanism</span>
                                <span className="text-xs text-slate-500">Best for numerical queries (Count, Sum, Mean)</span>
                            </div>
                            <div className="bg-white p-3 rounded-lg shadow-sm">
                                <span className="block font-medium text-slate-900 text-sm">Gaussian Mechanism</span>
                                <span className="text-xs text-slate-500">Good for high-dimensional data, allows delta &gt; 0</span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-amber-50 p-6 rounded-2xl border border-amber-100">
                        <h3 className="font-bold text-amber-900 mb-2 flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4" />
                            Budget Warning
                        </h3>
                        <p className="text-xs text-amber-800 mb-3">
                            When your remaining budget drops below 2.0, non-critical queries may be throttled.
                            When budget reaches 0, all queries will be blocked until reset by an admin.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PrivacyPolicy;
