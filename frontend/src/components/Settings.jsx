import React, { useState } from 'react';
import { User, ShieldAlert, RefreshCw, Save, Trash2 } from 'lucide-react';
import { auth, monitoring } from '../services/api';

const Settings = () => {
    const [user, setUser] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState('');

    React.useEffect(() => {
        const fetchUser = async () => {
            try {
                const response = await auth.me();
                setUser(response.data);
            } catch (error) {
                console.error('Failed to fetch user:', error);
            }
        };
        fetchUser();
    }, []);

    const handleResetBudget = async () => {
        if (!confirm('Are you sure you want to reset the privacy budget? This action will be logged.')) return;

        setIsLoading(true);
        try {
            await monitoring.resetBudget();
            setMessage('Privacy budget reset successfully');
            setTimeout(() => setMessage(''), 3000);
        } catch (error) {
            console.error('Reset failed:', error);
            setMessage('Failed to reset budget: ' + (error.response?.data?.detail || 'Unknown error'));
        } finally {
            setIsLoading(false);
        }
    };

    const handlePlatformReset = async () => {
        if (!confirm('WARNING: This will delete ALL audit logs and reset the privacy budget. This cannot be undone. Are you sure?')) return;

        setIsLoading(true);
        try {
            await monitoring.resetPlatform();
            setMessage('Platform reset successfully! Logs cleared and budget restored.');
            setTimeout(() => setMessage(''), 3000);
        } catch (error) {
            console.error('Platform reset failed:', error);
            setMessage('Failed to reset platform: ' + (error.response?.data?.detail || 'Unknown error'));
        } finally {
            setIsLoading(false);
        }
    };

    if (!user) return <div className="text-slate-500 p-8">Loading settings...</div>;

    return (
        <div className="p-8 max-w-4xl mx-auto space-y-8">
            <h1 className="text-2xl font-bold text-slate-900">Settings</h1>

            {/* Profile Section */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2 mb-6">
                    <User className="w-5 h-5 text-blue-600" />
                    Profile Information
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
                        <input type="text" value={user.username} disabled className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-500" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
                        <input type="text" value={user.email} disabled className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-500" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Role</label>
                        <input type="text" value={user.role || 'Analyst'} disabled className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-500 capitalize" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Organization</label>
                        <input type="text" value={user.organization || 'PrivacyFirst Inc.'} disabled className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-500" />
                    </div>
                </div>
            </div>

            {/* Admin Actions */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 border-l-4 border-l-red-500">
                <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2 mb-2">
                    <ShieldAlert className="w-5 h-5 text-red-500" />
                    Administrative Actions
                </h2>
                <p className="text-sm text-slate-500 mb-6">Sensitive actions that affect the entire system privacy guarantees.</p>

                <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-red-50 rounded-xl border border-red-100">
                        <div>
                            <h3 className="font-semibold text-red-900">Reset Privacy Budget</h3>
                            <p className="text-xs text-red-700">Restores epsilon budget to initial 10.0 for your account.</p>
                        </div>
                        <button
                            onClick={handleResetBudget}
                            disabled={isLoading}
                            className="flex items-center gap-2 px-4 py-2 bg-white border border-red-200 text-red-600 rounded-lg text-sm font-medium hover:bg-red-50 transition-colors shadow-sm"
                        >
                            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                            {isLoading ? 'Resetting...' : 'Reset Budget'}
                        </button>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-red-100 rounded-xl border border-red-200">
                        <div>
                            <h3 className="font-bold text-red-900">Factory Reset Platform</h3>
                            <p className="text-xs text-red-800">Clears ALL audit logs and resets budget. Use with caution.</p>
                        </div>
                        <button
                            onClick={handlePlatformReset}
                            disabled={isLoading}
                            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white border border-red-600 rounded-lg text-sm font-medium hover:bg-red-700 transition-colors shadow-sm shadow-red-500/30"
                        >
                            <Trash2 className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                            {isLoading ? 'Resetting...' : 'Factory Reset'}
                        </button>
                    </div>
                </div>
                {message && (
                    <div className="mt-4 p-3 bg-green-50 text-green-700 rounded-lg text-sm text-center">
                        {message}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Settings;
