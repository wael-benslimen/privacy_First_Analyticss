import React, { useState } from 'react';
import DPForm from './DPForm';
import DPResult from './DPResult';
import AuditLog from './AuditLog';
import PolicyPanel from './PolicyPanel';

const Dashboard = ({ token }) => {
    const [isRunning, setIsRunning] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleRunAnalysis = async (params) => {
        setIsRunning(true);
        setError(null);
        try {
            const response = await fetch('http://127.0.0.1:8000/api/query/count/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    epsilon: params.epsilon,
                    filters: {} // Add filters if needed
                })
            });

            const data = await response.json();

            if (response.ok) {
                setResult({
                    rawValue: data.result.true_result, // Adjust based on actual API response structure
                    privateValue: data.result.noisy_result,
                    noise: data.result.noise_added,
                    uncertainty: 0, // Calculate or get from API
                    chartData: [ // Placeholder or fetch histogram
                        { name: '0-10', value: 400 },
                        { name: '10-20', value: 300 },
                        { name: '20-30', value: 200 },
                        { name: '30-40', value: 278 },
                        { name: '40-50', value: 189 },
                        { name: '50+', value: 239 },
                    ]
                });
            } else {
                setError(data.error || 'Analysis failed');
            }
        } catch (err) {
            setError('Failed to connect to server');
        } finally {
            setIsRunning(false);
        }
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Analytics Dashboard</h1>
                    <p className="text-slate-500">Manage differential privacy parameters and view results</p>
                </div>
                <div className="flex gap-3">
                    <button className="px-4 py-2 bg-white border border-slate-200 rounded-lg text-slate-600 text-sm font-medium hover:bg-slate-50 transition-colors">
                        Export Report
                    </button>
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors shadow-lg shadow-blue-500/30">
                        New Analysis
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                <div className="lg:col-span-4">
                    <DPForm onRunAnalysis={handleRunAnalysis} isRunning={isRunning} />
                </div>
                <div className="lg:col-span-8">
                    <DPResult result={result} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <AuditLog />
                <PolicyPanel />
            </div>
        </div>
    );
};

export default Dashboard;
