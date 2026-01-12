import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    AlertCircle,
    BookOpen,
    TrendingUp,
    Clock,
    ChevronRight,
    Zap
} from 'lucide-react';
import { dashboardAPI, sosAPI } from '../api/client';

export default function Dashboard({ user }) {
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        loadDashboard();
    }, []);

    const loadDashboard = async () => {
        try {
            const data = await dashboardAPI.getTeacher();
            setDashboardData(data);
        } catch (err) {
            setError('Failed to load dashboard');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Welcome Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-6 lg:p-8 text-white"
            >
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                    <div>
                        <h1 className="text-2xl lg:text-3xl font-bold mb-2">
                            Welcome back, {user?.name?.split(' ')[0] || 'Teacher'}! 👋
                        </h1>
                        <p className="text-primary-100">
                            Ready to transform your classroom today? Need help? Just ask.
                        </p>
                    </div>
                    <Link
                        to="/sos"
                        className="inline-flex items-center gap-2 bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-primary-50 transition-colors"
                    >
                        <AlertCircle className="w-5 h-5" />
                        New SOS Request
                        <ChevronRight className="w-4 h-4" />
                    </Link>
                </div>
            </motion.div>

            {/* Stats Cards */}
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                    {
                        label: 'Total SOS Requests',
                        value: dashboardData?.total_sos_requests || 0,
                        icon: AlertCircle,
                        color: 'bg-red-500',
                        bgLight: 'bg-red-50',
                    },
                    {
                        label: 'Successful Resolutions',
                        value: dashboardData?.total_successful_resolutions || 0,
                        icon: BookOpen,
                        color: 'bg-secondary-500',
                        bgLight: 'bg-secondary-50',
                    },
                    {
                        label: 'Active Subjects',
                        value: dashboardData?.subjects_taught?.length || 0,
                        icon: TrendingUp,
                        color: 'bg-primary-500',
                        bgLight: 'bg-primary-50',
                    },
                    {
                        label: 'Avg Response Time',
                        value: '<10s',
                        icon: Clock,
                        color: 'bg-accent-500',
                        bgLight: 'bg-accent-50',
                    },
                ].map((stat, index) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="stat-card"
                    >
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-slate-500 text-sm mb-1">{stat.label}</p>
                                <p className="text-3xl font-bold text-slate-800">{stat.value}</p>
                            </div>
                            <div className={`${stat.bgLight} p-3 rounded-xl`}>
                                <stat.icon className={`w-6 h-6 text-${stat.color.replace('bg-', '')}`} style={{ color: getColorHex(stat.color) }} />
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Quick SOS Section */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="glass-card p-6 lg:p-8"
            >
                <div className="flex items-center gap-3 mb-6">
                    <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center">
                        <Zap className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-slate-800">Need Classroom Help?</h2>
                        <p className="text-slate-600">Describe your problem and get instant AI-powered solutions</p>
                    </div>
                </div>

                <Link
                    to="/sos"
                    className="block w-full bg-gradient-to-r from-red-500 to-red-600 text-white text-center py-4 rounded-xl font-semibold text-lg hover:from-red-600 hover:to-red-700 transition-all shadow-lg hover:shadow-xl"
                >
                    🆘 Start New SOS Request
                </Link>
            </motion.div>

            {/* Recent SOS and Top Issues */}
            <div className="grid lg:grid-cols-2 gap-6">
                {/* Recent SOS */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                    className="stat-card"
                >
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="font-semibold text-lg text-slate-800">Recent Requests</h3>
                        <Link to="/history" className="text-primary-600 text-sm hover:underline">
                            View All
                        </Link>
                    </div>

                    {dashboardData?.recent_sos?.length > 0 ? (
                        <div className="space-y-4">
                            {dashboardData.recent_sos.slice(0, 3).map((sos) => (
                                <div key={sos.id} className="flex items-start gap-3 p-3 bg-slate-50 rounded-xl">
                                    <div className={`w-2 h-2 rounded-full mt-2 ${sos.status === 'resolved' ? 'bg-secondary-500' : 'bg-yellow-500'}`}></div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-slate-800 text-sm truncate">{sos.raw_input}</p>
                                        <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                                            <span>{sos.subject || 'General'}</span>
                                            <span>•</span>
                                            <span className="capitalize">{sos.status}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-slate-500">
                            <AlertCircle className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                            <p>No SOS requests yet</p>
                            <p className="text-sm">Submit your first request when you need help!</p>
                        </div>
                    )}
                </motion.div>

                {/* Top Issues */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 }}
                    className="stat-card"
                >
                    <h3 className="font-semibold text-lg text-slate-800 mb-6">Common Issues</h3>

                    {dashboardData?.top_issues?.length > 0 ? (
                        <div className="space-y-4">
                            {dashboardData.top_issues.slice(0, 5).map((issue, index) => (
                                <div key={issue.issue} className="flex items-center gap-3">
                                    <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center text-primary-600 font-semibold text-sm">
                                        {index + 1}
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-slate-800 capitalize">{issue.issue?.replace('_', ' ')}</p>
                                        <div className="w-full bg-slate-100 rounded-full h-2 mt-1">
                                            <div
                                                className="bg-primary-500 h-2 rounded-full"
                                                style={{ width: `${Math.min((issue.count / 10) * 100, 100)}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                    <span className="text-slate-500 text-sm">{issue.count}x</span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-slate-500">
                            <TrendingUp className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                            <p>No patterns detected yet</p>
                            <p className="text-sm">Patterns will appear after multiple requests</p>
                        </div>
                    )}
                </motion.div>
            </div>
        </div>
    );
}

function getColorHex(colorClass) {
    const colors = {
        'bg-red-500': '#ef4444',
        'bg-secondary-500': '#43a047',
        'bg-primary-500': '#1976d2',
        'bg-accent-500': '#ff9800',
    };
    return colors[colorClass] || '#64748b';
}
