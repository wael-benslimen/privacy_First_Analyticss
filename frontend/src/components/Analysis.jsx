import React, { useState } from 'react';
import DPForm from './DPForm';
import DPResult from './DPResult';
import { query, monitoring } from '../services/api';

const Analysis = () => {
    const [isRunning, setIsRunning] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleRunAnalysis = async (params) => {
        setIsRunning(true);
        setError(null);
        try {
            // Prepare payload
            // Prepare payload
            const payload = {
                epsilon: params.epsilon,
                delta: params.delta,
                sensitivity: params.sensitivity,
                mechanism: params.mechanism,
                filters: params.filters || {}
            };

            // Handle column/columns mapping based on query type
            if (['mean', 'sum'].includes(params.queryType)) {
                payload.columns = [params.column]; // Backend expects list
            } else if (params.queryType !== 'count') {
                payload.column = params.column; // Median/Histogram expect single column string
            }

            if (params.queryType === 'histogram') payload.bins = 10;

            const response = await query.run(params.queryType, payload);
            const data = response.data;

            // Format values
            const formatValue = (val) => {
                if (Array.isArray(val)) return 'See Chart';
                if (typeof val === 'object') return JSON.stringify(val);
                if (typeof val === 'number') return val.toFixed(2);
                return val;
            };

            setResult({
                queryType: params.queryType,
                rawValue: formatValue(data.result.true_result),
                privateValue: formatValue(data.result.noisy_result),
                noise: typeof data.result.noise_added === 'number' ? data.result.noise_added.toFixed(2) : 'N/A',
                uncertainty: 0,
                chartData: params.queryType === 'histogram'
                    ? data.result.noisy_result.map((val, idx) => ({ name: `Bin ${idx}`, value: val }))
                    : [
                        { name: 'True', value: typeof data.result.true_result === 'number' ? data.result.true_result : 0 },
                        { name: 'Private', value: typeof data.result.noisy_result === 'number' ? data.result.noisy_result : 0 }
                    ]
            });

        } catch (err) {
            console.error('Analysis error:', err);
            const errorMessage = err.response?.data?.error || err.response?.data?.detail || 'Analysis failed';
            setError(errorMessage);
        } finally {
            setIsRunning(false);
        }
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">New Analysis</h1>
                    <p className="text-slate-500">Run differential privacy queries on patient data.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                <div className="lg:col-span-4">
                    <DPForm onRunAnalysis={handleRunAnalysis} isRunning={isRunning} />
                    {error && (
                        <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg text-sm border border-red-100">
                            {error}
                        </div>
                    )}
                </div>
                <div className="lg:col-span-8">
                    <DPResult result={result} />
                </div>
            </div>
        </div>
    );
};

export default Analysis;
