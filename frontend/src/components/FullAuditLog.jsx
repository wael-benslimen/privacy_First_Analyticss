import React, { useState, useEffect } from 'react';
import { FileText, Download, Filter } from 'lucide-react';
import { monitoring } from '../services/api';
import AuditLog from './AuditLog';

const FullAuditLog = () => {
    const [logs, setLogs] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const response = await monitoring.logs();
                // Handle potential pagination structure from DRF
                const results = response.data.results || response.data;
                setLogs(results);
            } catch (error) {
                console.error('Failed to fetch logs:', error);
            } finally {
                setIsLoading(false);
            }
        };
        fetchLogs();
    }, []);

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
                        <FileText className="w-8 h-8 text-blue-600" />
                        System Audit Logs
                    </h1>
                    <p className="text-slate-500">Complete history of all differential privacy queries and system events.</p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={() => exportToCSV(logs)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors shadow-lg shadow-blue-500/30 flex items-center gap-2"
                    >
                        <Download className="w-4 h-4" />
                        Export CSV
                    </button>
                </div>
            </div>

            {isLoading ? (
                <div className="text-center py-12 text-slate-500">Loading audit history...</div>
            ) : (
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                    <AuditLog logs={logs} />
                </div>
            )}
        </div>
    );
};

// Helper for CSV export
const exportToCSV = (logs) => {
    const headers = ['Timestamp', 'Query Type', 'Epsilon', 'Status', 'User', 'IP'];
    const csvContent = [
        headers.join(','),
        ...logs.map(log => [
            new Date(log.timestamp).toISOString(),
            log.query_type,
            log.epsilon_used,
            log.status,
            log.user || 'Unknown',
            log.ip_address || 'N/A'
        ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('button'); // specific workaround not needed, creating anchor
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit_logs_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
};

export default FullAuditLog;
