import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    Clock,
    CheckCircle,
    XCircle,
    AlertCircle,
    ChevronRight,
    Search,
    Filter,
    BookOpen
} from 'lucide-react';
import { sosAPI } from '../api/client';

export default function History() {
    const [sosRequests, setSOSRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedSOS, setSelectedSOS] = useState(null);

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        try {
            const data = await sosAPI.getHistory(0, 50);
            setSOSRequests(data);
        } catch (err) {
            console.error('Failed to load history:', err);
        } finally {
            setLoading(false);
        }
    };

    const loadSOSDetails = async (id) => {
        try {
            const data = await sosAPI.getById(id);
            setSelectedSOS(data);
        } catch (err) {
            console.error('Failed to load SOS details:', err);
        }
    };

    const filteredRequests = sosRequests.filter(sos => {
        const matchesFilter = filter === 'all' || sos.status === filter;
        const matchesSearch = sos.raw_input.toLowerCase().includes(searchQuery.toLowerCase()) ||
            sos.subject?.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    const getStatusIcon = (status) => {
        switch (status) {
            case 'resolved':
                return <CheckCircle className="w-5 h-5 text-secondary-500" />;
            case 'failed':
                return <XCircle className="w-5 h-5 text-red-500" />;
            case 'processing':
                return <Clock className="w-5 h-5 text-accent-500 animate-pulse" />;
            default:
                return <AlertCircle className="w-5 h-5 text-slate-400" />;
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'resolved': return 'bg-secondary-50 text-secondary-700';
            case 'failed': return 'bg-red-50 text-red-700';
            case 'processing': return 'bg-accent-50 text-accent-700';
            default: return 'bg-slate-100 text-slate-600';
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
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">SOS History</h1>
                    <p className="text-slate-600">View all your past classroom rescue requests</p>
                </div>
                <Link to="/sos" className="btn-primary flex items-center gap-2 self-start">
                    <AlertCircle className="w-5 h-5" />
                    New SOS
                </Link>
            </div>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                    <input
                        type="text"
                        placeholder="Search by problem or subject..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="input-field pl-12"
                    />
                </div>
                <div className="flex gap-2">
                    {['all', 'resolved', 'processing', 'pending', 'failed'].map((status) => (
                        <button
                            key={status}
                            onClick={() => setFilter(status)}
                            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${filter === status
                                    ? 'bg-primary-500 text-white'
                                    : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'
                                }`}
                        >
                            {status === 'all' ? 'All' : status.charAt(0).toUpperCase() + status.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            {/* List */}
            <div className="space-y-4">
                {filteredRequests.length === 0 ? (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-center py-16 bg-white rounded-2xl border border-slate-200"
                    >
                        <AlertCircle className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-slate-700 mb-2">No requests found</h3>
                        <p className="text-slate-500 mb-6">
                            {filter !== 'all' ? 'Try changing your filter' : 'Submit your first SOS to get started'}
                        </p>
                        <Link to="/sos" className="btn-primary">
                            Create SOS Request
                        </Link>
                    </motion.div>
                ) : (
                    filteredRequests.map((sos, index) => (
                        <motion.div
                            key={sos.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            onClick={() => loadSOSDetails(sos.id)}
                            className="stat-card cursor-pointer hover:shadow-xl transition-shadow"
                        >
                            <div className="flex items-start gap-4">
                                <div className="flex-shrink-0">
                                    {getStatusIcon(sos.status)}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-slate-800 font-medium line-clamp-2">
                                        {sos.raw_input}
                                    </p>
                                    <div className="flex flex-wrap items-center gap-2 mt-2">
                                        {sos.subject && (
                                            <span className="px-2 py-1 bg-primary-50 text-primary-600 rounded-lg text-xs">
                                                {sos.subject}
                                            </span>
                                        )}
                                        {sos.grade && (
                                            <span className="px-2 py-1 bg-secondary-50 text-secondary-600 rounded-lg text-xs">
                                                Grade {sos.grade}
                                            </span>
                                        )}
                                        <span className={`px-2 py-1 rounded-lg text-xs capitalize ${getStatusColor(sos.status)}`}>
                                            {sos.status}
                                        </span>
                                        {sos.processing_time_ms && (
                                            <span className="text-xs text-slate-500">
                                                {(sos.processing_time_ms / 1000).toFixed(1)}s
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-xs text-slate-400 mt-2">
                                        {new Date(sos.created_at).toLocaleString()}
                                    </p>
                                </div>
                                <ChevronRight className="w-5 h-5 text-slate-300 flex-shrink-0" />
                            </div>
                        </motion.div>
                    ))
                )}
            </div>

            {/* SOS Detail Modal */}
            {selectedSOS && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
                    onClick={() => setSelectedSOS(null)}
                >
                    <motion.div
                        initial={{ scale: 0.95, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        onClick={(e) => e.stopPropagation()}
                        className="bg-white rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6"
                    >
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-bold text-slate-900">SOS Details</h2>
                            <button
                                onClick={() => setSelectedSOS(null)}
                                className="p-2 hover:bg-slate-100 rounded-lg"
                            >
                                ✕
                            </button>
                        </div>

                        {/* Problem */}
                        <div className="mb-6">
                            <h3 className="font-medium text-slate-700 mb-2">Your Problem</h3>
                            <p className="text-slate-600 bg-slate-50 p-4 rounded-xl">
                                {selectedSOS.raw_input}
                            </p>
                        </div>

                        {/* Context */}
                        <div className="flex flex-wrap gap-2 mb-6">
                            {selectedSOS.subject && (
                                <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                                    {selectedSOS.subject}
                                </span>
                            )}
                            {selectedSOS.grade && (
                                <span className="px-3 py-1 bg-secondary-100 text-secondary-700 rounded-full text-sm">
                                    Grade {selectedSOS.grade}
                                </span>
                            )}
                            <span className={`px-3 py-1 rounded-full text-sm capitalize ${getStatusColor(selectedSOS.status)}`}>
                                {selectedSOS.status}
                            </span>
                        </div>

                        {/* Playbook */}
                        {selectedSOS.playbook && (
                            <div className="playbook-card">
                                <div className="flex items-center gap-3 mb-4">
                                    <BookOpen className="w-6 h-6 text-primary-600" />
                                    <h3 className="font-bold text-lg text-slate-900">
                                        {selectedSOS.playbook.title || 'Teaching Playbook'}
                                    </h3>
                                </div>
                                <p className="text-slate-600 mb-4">{selectedSOS.playbook.summary}</p>

                                {selectedSOS.playbook.immediate_actions?.length > 0 && (
                                    <div className="mb-4">
                                        <h4 className="font-semibold text-red-600 mb-2">⚡ Immediate Actions</h4>
                                        <ul className="space-y-2">
                                            {selectedSOS.playbook.immediate_actions.map((action, i) => (
                                                <li key={i} className="flex items-start gap-2 text-sm">
                                                    <span className="w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center text-xs flex-shrink-0">
                                                        {i + 1}
                                                    </span>
                                                    {action}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        )}
                    </motion.div>
                </motion.div>
            )}
        </div>
    );
}
