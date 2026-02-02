/**
 * SAHAYAK AI - Teacher Dashboard
 * Features: Recent playbooks, saved responses, shared solutions, mentor insights
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    BookOpen,
    TrendingUp,
    Clock,
    ChevronRight,
    Zap,
    Heart,
    Share2,
    Brain,
    Lightbulb,
    BarChart3,
    Star,
    BookmarkPlus
} from 'lucide-react';
import { dashboardAPI, knowledgeAPI } from '../api/client';

export default function TeacherDashboard({ user }) {
    const [loading, setLoading] = useState(true);
    const [dashboardData, setDashboardData] = useState(null);
    const [savedSolutions, setSavedSolutions] = useState([]);
    const [mentorInsights, setMentorInsights] = useState(null);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        loadDashboard();
    }, []);

    async function loadDashboard() {
        try {
            setLoading(true);

            // Load dashboard data
            const [dashboardRes, solutionsRes, mentorRes] = await Promise.all([
                dashboardAPI.getTeacher().catch(() => null),
                knowledgeAPI.getMySolutions().catch(() => ({ data: [] })),
                knowledgeAPI.getMentorInsights().catch(() => null)
            ]);

            if (dashboardRes?.data) {
                setDashboardData(dashboardRes.data);
            }

            setSavedSolutions(solutionsRes?.data || []);
            setMentorInsights(mentorRes?.data);

        } catch (error) {
            console.error('Error loading dashboard:', error);
        } finally {
            setLoading(false);
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-500 border-t-transparent" />
            </div>
        );
    }

    const stats = dashboardData?.summary || {
        total_sos: 0,
        resolved: 0,
        resolution_rate: 0,
        saved_playbooks: 0
    };

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">
                        Welcome back, {user?.name || 'Teacher'}! 👋
                    </h1>
                    <p className="text-gray-600 mt-1">
                        Here's your teaching insights and saved resources
                    </p>
                </div>
                <Link
                    to="/sos"
                    className="px-6 py-3 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-xl flex items-center gap-2 transition-colors shadow-lg"
                >
                    <Zap size={20} />
                    SOS Help
                </Link>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatsCard
                    icon={<BookOpen className="text-indigo-500" />}
                    label="Total SOS"
                    value={stats.total_sos}
                    color="bg-indigo-50"
                />
                <StatsCard
                    icon={<TrendingUp className="text-green-500" />}
                    label="Resolved"
                    value={stats.resolved}
                    color="bg-green-50"
                />
                <StatsCard
                    icon={<Star className="text-yellow-500" />}
                    label="Resolution Rate"
                    value={`${stats.resolution_rate}%`}
                    color="bg-yellow-50"
                />
                <StatsCard
                    icon={<BookmarkPlus className="text-purple-500" />}
                    label="Saved Playbooks"
                    value={stats.saved_playbooks}
                    color="bg-purple-50"
                />
            </div>

            {/* Tabs */}
            <div className="flex gap-2 border-b">
                {['overview', 'shared', 'mentor'].map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`px-4 py-2 font-medium capitalize transition-colors ${activeTab === tab
                                ? 'text-indigo-600 border-b-2 border-indigo-600'
                                : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        {tab === 'overview' && '📊 Overview'}
                        {tab === 'shared' && '🤝 Shared Solutions'}
                        {tab === 'mentor' && '🧠 AI Mentor'}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            {activeTab === 'overview' && (
                <OverviewTab
                    dashboardData={dashboardData}
                    recentPlaybooks={dashboardData?.recent_playbooks || []}
                />
            )}

            {activeTab === 'shared' && (
                <SharedSolutionsTab
                    solutions={savedSolutions}
                    onRefresh={loadDashboard}
                />
            )}

            {activeTab === 'mentor' && (
                <MentorTab insights={mentorInsights} />
            )}
        </div>
    );
}

function StatsCard({ icon, label, value, color }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`${color} rounded-xl p-4 flex items-center gap-4`}
        >
            <div className="p-3 bg-white rounded-lg shadow-sm">
                {icon}
            </div>
            <div>
                <p className="text-sm text-gray-600">{label}</p>
                <p className="text-2xl font-bold text-gray-900">{value}</p>
            </div>
        </motion.div>
    );
}

function OverviewTab({ dashboardData, recentPlaybooks }) {
    const subjectDist = dashboardData?.subject_distribution || {};
    const dailyActivity = dashboardData?.daily_activity || [];

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Playbooks */}
            <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <Clock size={18} className="text-indigo-500" />
                    Recent Playbooks
                </h3>
                <div className="space-y-3">
                    {recentPlaybooks.length > 0 ? (
                        recentPlaybooks.map((playbook, i) => (
                            <div
                                key={playbook.id || i}
                                className="p-3 bg-gray-50 rounded-lg flex items-center justify-between hover:bg-gray-100 transition-colors"
                            >
                                <div>
                                    <p className="font-medium text-gray-900">{playbook.title}</p>
                                    <p className="text-sm text-gray-500">
                                        {new Date(playbook.created_at).toLocaleDateString()}
                                    </p>
                                </div>
                                <ChevronRight size={18} className="text-gray-400" />
                            </div>
                        ))
                    ) : (
                        <p className="text-gray-500 text-center py-4">
                            No playbooks yet. Create one using SOS!
                        </p>
                    )}
                </div>
            </div>

            {/* Subject Distribution */}
            <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <BarChart3 size={18} className="text-green-500" />
                    Subject Distribution
                </h3>
                <div className="space-y-3">
                    {Object.entries(subjectDist).length > 0 ? (
                        Object.entries(subjectDist).map(([subject, count]) => (
                            <div key={subject} className="flex items-center gap-3">
                                <div className="flex-1">
                                    <div className="flex justify-between mb-1">
                                        <span className="text-sm font-medium text-gray-700">{subject}</span>
                                        <span className="text-sm text-gray-500">{count}</span>
                                    </div>
                                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
                                            style={{
                                                width: `${Math.min(100, count * 10)}%`
                                            }}
                                        />
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <p className="text-gray-500 text-center py-4">
                            No subject data yet
                        </p>
                    )}
                </div>
            </div>

            {/* Activity Chart */}
            <div className="bg-white rounded-xl shadow-sm p-6 lg:col-span-2">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <TrendingUp size={18} className="text-blue-500" />
                    Daily Activity (Last 30 Days)
                </h3>
                <div className="h-40 flex items-end gap-1">
                    {dailyActivity.length > 0 ? (
                        dailyActivity.slice(-14).map((day, i) => (
                            <div
                                key={day.date || i}
                                className="flex-1 bg-indigo-100 hover:bg-indigo-200 transition-colors rounded-t"
                                style={{
                                    height: `${Math.max(10, day.count * 20)}%`
                                }}
                                title={`${day.date}: ${day.count} SOS`}
                            />
                        ))
                    ) : (
                        <p className="text-gray-500 text-center w-full py-8">
                            Activity data will appear here
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}

function SharedSolutionsTab({ solutions, onRefresh }) {
    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">
                    Solutions You've Shared ({solutions.length})
                </h3>
                <Link
                    to="/knowledge"
                    className="text-indigo-600 hover:text-indigo-700 text-sm font-medium"
                >
                    Browse Library →
                </Link>
            </div>

            {solutions.length > 0 ? (
                <div className="grid gap-4">
                    {solutions.map((solution) => (
                        <motion.div
                            key={solution.id}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="bg-white rounded-xl shadow-sm p-5 border border-gray-100"
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <h4 className="font-semibold text-gray-900">{solution.title}</h4>
                                    <p className="text-gray-600 text-sm mt-1">{solution.problem}</p>
                                </div>
                                <span className={`px-3 py-1 rounded-full text-xs font-medium ${solution.status === 'approved'
                                        ? 'bg-green-100 text-green-700'
                                        : 'bg-yellow-100 text-yellow-700'
                                    }`}>
                                    {solution.status}
                                </span>
                            </div>
                            <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                                <span className="flex items-center gap-1">
                                    <Star size={14} className="text-yellow-500" />
                                    {solution.trust_score?.toFixed(1)}
                                </span>
                                <span className="flex items-center gap-1">
                                    <Heart size={14} className="text-red-400" />
                                    {solution.usage_count} uses
                                </span>
                            </div>
                        </motion.div>
                    ))}
                </div>
            ) : (
                <div className="bg-gray-50 rounded-xl p-8 text-center">
                    <Share2 size={48} className="mx-auto text-gray-300 mb-4" />
                    <p className="text-gray-600">
                        You haven't shared any solutions yet.
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                        Help other teachers by sharing what works for you!
                    </p>
                </div>
            )}
        </div>
    );
}

function MentorTab({ insights }) {
    if (!insights) {
        return (
            <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-8 text-center">
                <Brain size={48} className="mx-auto text-indigo-400 mb-4" />
                <h3 className="font-semibold text-gray-900 mb-2">
                    AI Teaching Mentor
                </h3>
                <p className="text-gray-600">
                    Your personalized mentor insights will appear here as you use SAHAYAK AI more.
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Patterns */}
            {insights.patterns?.length > 0 && (
                <div className="bg-white rounded-xl shadow-sm p-6">
                    <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <TrendingUp size={18} className="text-blue-500" />
                        Teaching Patterns Detected
                    </h3>
                    <ul className="space-y-2">
                        {insights.patterns.map((pattern, i) => (
                            <li key={i} className="flex items-start gap-2 text-gray-700">
                                <span className="text-blue-500">•</span>
                                {pattern}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Suggestions */}
            {insights.suggestions?.length > 0 && (
                <div className="bg-white rounded-xl shadow-sm p-6">
                    <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <Lightbulb size={18} className="text-yellow-500" />
                        Personalized Suggestions
                    </h3>
                    <ul className="space-y-2">
                        {insights.suggestions.map((suggestion, i) => (
                            <li key={i} className="flex items-start gap-2 text-gray-700">
                                <span className="text-yellow-500">💡</span>
                                {suggestion}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Strengths & Growth */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {insights.strengths?.length > 0 && (
                    <div className="bg-green-50 rounded-xl p-5">
                        <h4 className="font-semibold text-green-800 mb-3">🌟 Your Strengths</h4>
                        <ul className="space-y-1 text-green-700 text-sm">
                            {insights.strengths.map((s, i) => (
                                <li key={i}>• {s}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {insights.growth_areas?.length > 0 && (
                    <div className="bg-orange-50 rounded-xl p-5">
                        <h4 className="font-semibold text-orange-800 mb-3">🎯 Growth Areas</h4>
                        <ul className="space-y-1 text-orange-700 text-sm">
                            {insights.growth_areas.map((g, i) => (
                                <li key={i}>• {g}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}
