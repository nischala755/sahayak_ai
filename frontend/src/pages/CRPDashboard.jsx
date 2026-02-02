/**
 * SAHAYAK AI - CRP (Cluster Resource Person) Dashboard
 * Features: Cluster trends, frequent problems, proven solutions, teacher engagement
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    Users,
    TrendingUp,
    AlertTriangle,
    Award,
    BarChart3,
    MapPin,
    Zap,
    ChevronDown,
    Star
} from 'lucide-react';
import { dashboardAPI } from '../api/client';

export default function CRPDashboard({ user }) {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    const [timeRange, setTimeRange] = useState(7);

    useEffect(() => {
        loadDashboard();
    }, [timeRange]);

    async function loadDashboard() {
        try {
            setLoading(true);
            const response = await dashboardAPI.getCRP(timeRange);
            if (response?.data) {
                setData(response.data);
            }
        } catch (error) {
            console.error('Error loading CRP dashboard:', error);
        } finally {
            setLoading(false);
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-teal-500 border-t-transparent" />
            </div>
        );
    }

    const summary = data?.summary || {
        total_teachers: 0,
        active_teachers: 0,
        engagement_rate: 0,
        total_sos: 0
    };

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <MapPin className="text-teal-500" />
                        Cluster Dashboard
                    </h1>
                    <p className="text-gray-600 mt-1">
                        Monitor teachers and identify intervention needs
                    </p>
                </div>
                <select
                    value={timeRange}
                    onChange={(e) => setTimeRange(parseInt(e.target.value))}
                    className="px-4 py-2 border rounded-lg bg-white text-gray-700 focus:ring-2 focus:ring-teal-500"
                >
                    <option value={7}>Last 7 days</option>
                    <option value={14}>Last 14 days</option>
                    <option value={30}>Last 30 days</option>
                </select>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatCard
                    icon={<Users className="text-blue-500" />}
                    label="Total Teachers"
                    value={summary.total_teachers}
                    bg="bg-blue-50"
                />
                <StatCard
                    icon={<Zap className="text-green-500" />}
                    label="Active Teachers"
                    value={summary.active_teachers}
                    bg="bg-green-50"
                />
                <StatCard
                    icon={<TrendingUp className="text-purple-500" />}
                    label="Engagement"
                    value={`${summary.engagement_rate}%`}
                    bg="bg-purple-50"
                />
                <StatCard
                    icon={<AlertTriangle className="text-orange-500" />}
                    label="Total SOS"
                    value={summary.total_sos}
                    bg="bg-orange-50"
                />
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Frequent Problems */}
                <div className="bg-white rounded-xl shadow-sm p-6">
                    <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <AlertTriangle size={18} className="text-red-500" />
                        Most Frequent Problems
                    </h3>
                    <div className="space-y-3">
                        {data?.frequent_problems?.length > 0 ? (
                            data.frequent_problems.slice(0, 8).map((item, i) => (
                                <div key={i} className="flex items-center justify-between">
                                    <span className="text-gray-700 text-sm flex-1 truncate">
                                        {item.problem}
                                    </span>
                                    <div className="flex items-center gap-2">
                                        <div className="w-20 h-2 bg-gray-100 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-gradient-to-r from-red-400 to-orange-400 rounded-full"
                                                style={{
                                                    width: `${Math.min(100, item.count * 5)}%`
                                                }}
                                            />
                                        </div>
                                        <span className="text-sm font-medium text-gray-600 w-8">
                                            {item.count}
                                        </span>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <p className="text-gray-500 text-center py-4">No data yet</p>
                        )}
                    </div>
                </div>

                {/* Proven Solutions */}
                <div className="bg-white rounded-xl shadow-sm p-6">
                    <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <Award size={18} className="text-yellow-500" />
                        Proven Solutions
                    </h3>
                    <div className="space-y-3">
                        {data?.proven_solutions?.length > 0 ? (
                            data.proven_solutions.slice(0, 5).map((solution, i) => (
                                <motion.div
                                    key={solution.id || i}
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ delay: i * 0.1 }}
                                    className="p-3 bg-gradient-to-r from-yellow-50 to-white rounded-lg border border-yellow-100"
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <h4 className="font-medium text-gray-900 text-sm">
                                                {solution.title}
                                            </h4>
                                            <p className="text-xs text-gray-500 mt-1">
                                                {solution.subject} • {solution.usage_count} teachers used this
                                            </p>
                                        </div>
                                        <div className="flex items-center gap-1 text-yellow-600">
                                            <Star size={14} fill="currentColor" />
                                            <span className="text-sm font-medium">
                                                {solution.trust_score?.toFixed(1)}
                                            </span>
                                        </div>
                                    </div>
                                </motion.div>
                            ))
                        ) : (
                            <p className="text-gray-500 text-center py-4">No solutions yet</p>
                        )}
                    </div>
                </div>

                {/* Issue Trends Chart */}
                <div className="bg-white rounded-xl shadow-sm p-6 lg:col-span-2">
                    <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <BarChart3 size={18} className="text-teal-500" />
                        Issue Trends Over Time
                    </h3>
                    <div className="h-48 flex items-end gap-2">
                        {data?.issue_trends?.length > 0 ? (
                            data.issue_trends.map((day, i) => {
                                const total = Object.values(day).reduce((a, b) =>
                                    typeof b === 'number' ? a + b : a, 0
                                );
                                return (
                                    <div
                                        key={day.date || i}
                                        className="flex-1 flex flex-col items-center"
                                    >
                                        <div
                                            className="w-full bg-gradient-to-t from-teal-500 to-cyan-400 rounded-t transition-all hover:opacity-80"
                                            style={{
                                                height: `${Math.max(10, total * 8)}%`
                                            }}
                                        />
                                        <span className="text-xs text-gray-400 mt-2 rotate-45 origin-left">
                                            {day.date?.slice(-5)}
                                        </span>
                                    </div>
                                );
                            })
                        ) : (
                            <p className="text-gray-500 text-center w-full py-8">
                                Trend data will appear here
                            </p>
                        )}
                    </div>
                </div>

                {/* Teacher Leaderboard */}
                <div className="bg-white rounded-xl shadow-sm p-6 lg:col-span-2">
                    <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <Award size={18} className="text-purple-500" />
                        Top Contributing Teachers
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="text-left text-sm text-gray-500 border-b">
                                    <th className="pb-3 font-medium">Rank</th>
                                    <th className="pb-3 font-medium">Teacher</th>
                                    <th className="pb-3 font-medium text-right">Solutions Shared</th>
                                    <th className="pb-3 font-medium text-right">Helpful Votes</th>
                                    <th className="pb-3 font-medium text-right">Score</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data?.teacher_leaderboard?.length > 0 ? (
                                    data.teacher_leaderboard.slice(0, 10).map((teacher, i) => (
                                        <tr key={teacher.teacher_id || i} className="border-b last:border-0">
                                            <td className="py-3">
                                                {i === 0 && '🥇'}
                                                {i === 1 && '🥈'}
                                                {i === 2 && '🥉'}
                                                {i > 2 && <span className="text-gray-400">{i + 1}</span>}
                                            </td>
                                            <td className="py-3 font-medium text-gray-900">
                                                {teacher.teacher_name}
                                            </td>
                                            <td className="py-3 text-right text-gray-600">
                                                {teacher.solutions_shared}
                                            </td>
                                            <td className="py-3 text-right text-gray-600">
                                                {teacher.helpful_votes}
                                            </td>
                                            <td className="py-3 text-right">
                                                <span className="text-purple-600 font-semibold">
                                                    {teacher.score}
                                                </span>
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan={5} className="py-8 text-center text-gray-500">
                                            No contributions yet
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatCard({ icon, label, value, bg }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`${bg} rounded-xl p-5`}
        >
            <div className="flex items-center gap-3">
                <div className="p-2.5 bg-white rounded-lg shadow-sm">
                    {icon}
                </div>
                <div>
                    <p className="text-sm text-gray-600">{label}</p>
                    <p className="text-2xl font-bold text-gray-900">{value}</p>
                </div>
            </div>
        </motion.div>
    );
}
