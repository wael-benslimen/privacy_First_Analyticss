import React from 'react';
import { User } from 'lucide-react';

const Header = ({ user }) => {
    return (

        <header className="h-20 bg-white border-b border-slate-200 flex items-center justify-end px-8 sticky top-0 z-40 ml-64">
            <div className="flex items-center gap-6">
                <div className="flex items-center gap-3 pl-2">
                    <div className="text-right hidden sm:block">
                        <p className="text-sm font-semibold text-slate-900">{user?.username || 'User'}</p>
                        <p className="text-xs text-slate-500 capitalize">{user?.role || 'Analyst'}</p>
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
