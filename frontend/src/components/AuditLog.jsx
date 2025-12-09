import React from 'react';
import { Clock, CheckCircle, XCircle } from 'lucide-react';

const AuditLog = ({ logs = [] }) => {
    // Helper to format timestamp
    const formatTime = (isoString) => {
        if (!isoString) return '--:--:--';
        return new Date(isoString).toLocaleTimeString();
    };

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-6 border-b border-slate-100">
                <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                    <Clock className="w-5 h-5 text-blue-600" />
                    Audit Log
                </h2>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 text-slate-500 font-medium">
                        <tr>
                            <th className="px-6 py-3">Time</th>
                            <th className="px-6 py-3">Query</th>
                            <th className="px-6 py-3">Budget (ε)</th>
                            <th className="px-6 py-3">Status</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {logs && logs.length > 0 ? (
                            logs.map((log) => (
                                <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                                    <td className="px-6 py-4 text-slate-500 font-mono text-xs">{formatTime(log.timestamp)}</td>
                                    <td className="px-6 py-4 font-medium text-slate-900">{log.query_type}</td>
                                    <td className="px-6 py-4 text-slate-600">{log.epsilon_used}</td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${log.status === 'success'
                                            ? 'bg-green-50 text-green-700'
                                            : 'bg-red-50 text-red-700'
                                            }`}>
                                            {log.status === 'success' ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                                            {log.status ? (log.status.charAt(0).toUpperCase() + log.status.slice(1)) : 'Unknown'}
                                        </span>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="4" className="px-6 py-4 text-center text-slate-500">
                                    No logs available
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AuditLog;
