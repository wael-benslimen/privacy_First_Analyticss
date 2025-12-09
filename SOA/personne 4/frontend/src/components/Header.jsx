import React from 'react';
import { Bell, Search, User } from 'lucide-react';

const Header = () => {
    return (
        <header className="h-20 bg-white border-b border-slate-200 flex items-center justify-between px-8 sticky top-0 z-40 ml-64">
            <div className="flex items-center gap-4 w-96">
                <div className="relative w-full group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                    <input
                        type="text"
                        placeholder="Search analytics, policies, or logs..."
                        className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border-none rounded-xl text-sm focus:ring-2 focus:ring-blue-100 focus:bg-white transition-all outline-none placeholder:text-slate-400"
                    />
                </div>
            </div>

            <div className="flex items-center gap-6">
                <button className="relative p-2 text-slate-400 hover:text-slate-600 transition-colors rounded-lg hover:bg-slate-50">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white" />
                </button>

                <div className="h-8 w-px bg-slate-200" />

                <div className="flex items-center gap-3 pl-2">
                    <div className="text-right hidden sm:block">
                        <p className="text-sm font-semibold text-slate-900">Dr. Sarah Connor</p>
                        <p className="text-xs text-slate-500">Lead Data Scientist</p>
                    </div>
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-600 p-0.5 cursor-pointer hover:shadow-lg transition-shadow">
                        <div className="w-full h-full rounded-full bg-white flex items-center justify-center">
                            <User className="w-5 h-5 text-blue-600" />
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
