import React from 'react';
import { Clock, CheckCircle, XCircle } from 'lucide-react';

const AuditLog = () => {
    const logs = [
        { id: 1, time: '10:42:23', query: 'AVG(salary)', epsilon: 0.5, status: 'success' },
        { id: 2, time: '10:30:15', query: 'COUNT(patients)', epsilon: 1.0, status: 'success' },
        { id: 3, time: '09:15:00', query: 'SUM(transactions)', epsilon: 2.0, status: 'blocked' },
        { id: 4, time: '09:10:45', query: 'MAX(age)', epsilon: 0.1, status: 'success' },
    ];

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
                        {logs.map((log) => (
                            <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                                <td className="px-6 py-4 text-slate-500 font-mono text-xs">{log.time}</td>
                                <td className="px-6 py-4 font-medium text-slate-900">{log.query}</td>
                                <td className="px-6 py-4 text-slate-600">{log.epsilon}</td>
                                <td className="px-6 py-4">
                                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${log.status === 'success'
                                            ? 'bg-green-50 text-green-700'
                                            : 'bg-red-50 text-red-700'
                                        }`}>
                                        {log.status === 'success' ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                                        {log.status.charAt(0).toUpperCase() + log.status.slice(1)}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AuditLog;
