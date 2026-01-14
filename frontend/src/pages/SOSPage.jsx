import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Mic,
    MicOff,
    Send,
    Loader2,
    CheckCircle,
    AlertCircle,
    Clock,
    BookOpen,
    ArrowLeft,
    ChevronDown,
    GraduationCap,
    Sparkles
} from 'lucide-react';
import { sosAPI } from '../api/client';

export default function SOSPage() {
    const [input, setInput] = useState('');
    const [subject, setSubject] = useState('');
    const [grade, setGrade] = useState('');
    const [isRecording, setIsRecording] = useState(false);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const recognitionRef = useRef(null);

    // Initialize Web Speech API
    useEffect(() => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = true;
            recognitionRef.current.interimResults = true;
            recognitionRef.current.lang = 'en-IN';

            recognitionRef.current.onresult = (event) => {
                let transcript = '';
                for (let i = 0; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript;
                }
                setInput(transcript);
            };

            recognitionRef.current.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                setIsRecording(false);
            };

            recognitionRef.current.onend = () => {
                setIsRecording(false);
            };
        }
    }, []);

    const toggleRecording = () => {
        if (!recognitionRef.current) {
            setError('Voice input not supported in this browser');
            return;
        }

        if (isRecording) {
            recognitionRef.current.stop();
            setIsRecording(false);
        } else {
            recognitionRef.current.start();
            setIsRecording(true);
            setError('');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) {
            setError('Please describe your classroom problem');
            return;
        }

        setError('');
        setLoading(true);
        setResult(null);

        try {
            const response = await sosAPI.quick(input, subject || null, grade || null);
            if (response.success) {
                setResult(response);
            } else {
                setError(response.error || 'Failed to generate playbook');
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to connect to server');
        } finally {
            setLoading(false);
        }
    };

    const resetForm = () => {
        setInput('');
        setSubject('');
        setGrade('');
        setResult(null);
        setError('');
    };

    return (
        <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
            {/* Header */}
            <header className="bg-white shadow-sm sticky top-0 z-50">
                <div className="max-w-4xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <Link to="/" className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
                                <GraduationCap className="w-6 h-6 text-white" />
                            </div>
                            <span className="font-bold text-xl text-primary-700">SAHAYAK AI</span>
                        </Link>
                        <Link to="/login" className="text-primary-600 hover:underline text-sm">
                            Sign In for Full Features →
                        </Link>
                    </div>
                </div>
            </header>

            <main className="max-w-4xl mx-auto px-4 py-8">
                <AnimatePresence mode="wait">
                    {!result ? (
                        <motion.div
                            key="form"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                        >
                            {/* Title */}
                            <div className="text-center mb-8">
                                <motion.div
                                    initial={{ scale: 0.9, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    className="inline-flex items-center gap-2 px-4 py-2 bg-red-50 rounded-full text-red-600 font-medium text-sm mb-4"
                                >
                                    <AlertCircle className="w-4 h-4" />
                                    Classroom Emergency? We're Here to Help!
                                </motion.div>
                                <h1 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-4">
                                    🆘 Quick SOS
                                </h1>
                                <p className="text-slate-600 max-w-lg mx-auto">
                                    Describe your classroom problem using voice or text.
                                    Our AI will generate an instant teaching rescue playbook.
                                </p>
                            </div>

                            {/* Error */}
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl mb-6 text-sm max-w-xl mx-auto"
                                >
                                    {error}
                                </motion.div>
                            )}

                            {/* Input Form */}
                            <form onSubmit={handleSubmit} className="max-w-xl mx-auto space-y-6">
                                {/* Voice/Text Input */}
                                <div className="glass-card p-6">
                                    <label className="block text-sm font-medium text-slate-700 mb-3">
                                        What's happening in your classroom? *
                                    </label>

                                    <div className="relative">
                                        <textarea
                                            value={input}
                                            onChange={(e) => setInput(e.target.value)}
                                            placeholder="E.g., Students in my Class 5 are not understanding how to add fractions with different denominators. They keep adding numerators and denominators separately..."
                                            className="input-field min-h-[150px] resize-none pr-16"
                                            rows={5}
                                        />

                                        {/* Voice Button */}
                                        <button
                                            type="button"
                                            onClick={toggleRecording}
                                            className={`absolute bottom-4 right-4 w-12 h-12 rounded-full flex items-center justify-center transition-all ${isRecording
                                                ? 'bg-red-500 text-white animate-pulse'
                                                : 'bg-primary-100 text-primary-600 hover:bg-primary-200'
                                                }`}
                                        >
                                            {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                                        </button>
                                    </div>

                                    {isRecording && (
                                        <motion.div
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            className="flex items-center gap-2 mt-3 text-red-500 text-sm"
                                        >
                                            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                                            Recording... Speak now
                                        </motion.div>
                                    )}
                                </div>

                                {/* Context Fields */}
                                <div className="grid sm:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-2">
                                            Subject (Optional)
                                        </label>
                                        <select
                                            value={subject}
                                            onChange={(e) => setSubject(e.target.value)}
                                            className="input-field"
                                        >
                                            <option value="">Auto-detect</option>
                                            <option value="Mathematics">Mathematics</option>
                                            <option value="Science">Science</option>
                                            <option value="English">English</option>
                                            <option value="Hindi">Hindi</option>
                                            <option value="Social Studies">Social Studies</option>
                                            <option value="EVS">EVS</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-2">
                                            Grade/Class (Optional)
                                        </label>
                                        <select
                                            value={grade}
                                            onChange={(e) => setGrade(e.target.value)}
                                            className="input-field"
                                        >
                                            <option value="">Auto-detect</option>
                                            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(g => (
                                                <option key={g} value={g}>Class {g}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>

                                {/* Submit Button */}
                                <button
                                    type="submit"
                                    disabled={loading || !input.trim()}
                                    className="btn-primary w-full flex items-center justify-center gap-2 py-4 text-lg"
                                >
                                    {loading ? (
                                        <>
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                            Generating Playbook...
                                        </>
                                    ) : (
                                        <>
                                            <Sparkles className="w-5 h-5" />
                                            Get AI Rescue Playbook
                                        </>
                                    )}
                                </button>
                            </form>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="result"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            {/* Success Header */}
                            <div className="text-center mb-8">
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    className="w-20 h-20 bg-secondary-100 rounded-full flex items-center justify-center mx-auto mb-4"
                                >
                                    <CheckCircle className="w-10 h-10 text-secondary-600" />
                                </motion.div>
                                <h2 className="text-2xl font-bold text-slate-900 mb-2">
                                    🎉 Playbook Generated!
                                </h2>
                                <p className="text-slate-600">
                                    Here's your instant teaching rescue strategy
                                </p>
                            </div>

                            {/* Playbook Display */}
                            <div className="playbook-card mb-6">
                                <div className="flex items-start gap-4 mb-6">
                                    <div className="w-12 h-12 bg-primary-500 rounded-xl flex items-center justify-center flex-shrink-0">
                                        <BookOpen className="w-6 h-6 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-bold text-slate-900">
                                            {result.playbook?.title || 'Teaching Rescue Playbook'}
                                        </h3>
                                        <p className="text-slate-600 mt-1">{result.playbook?.summary}</p>
                                    </div>
                                </div>

                                {/* Context Pills */}
                                <div className="flex flex-wrap gap-2 mb-6">
                                    {result.detected_subject && (
                                        <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                                            {result.detected_subject}
                                        </span>
                                    )}
                                    {result.detected_grade && (
                                        <span className="px-3 py-1 bg-secondary-100 text-secondary-700 rounded-full text-sm">
                                            Grade {result.detected_grade}
                                        </span>
                                    )}
                                    <span className="px-3 py-1 bg-accent-100 text-accent-700 rounded-full text-sm capitalize">
                                        {result.urgency} urgency
                                    </span>
                                    <span className="px-3 py-1 bg-slate-100 text-slate-600 rounded-full text-sm flex items-center gap-1">
                                        <Clock className="w-3 h-3" />
                                        {result.playbook?.time_minutes || 10} min
                                    </span>
                                </div>

                                {/* Immediate Actions */}
                                {result.playbook?.immediate_actions?.length > 0 && (
                                    <div className="mb-6">
                                        <h4 className="font-semibold text-red-600 mb-3 flex items-center gap-2">
                                            ⚡ Immediate Actions (Do NOW)
                                        </h4>
                                        <div className="space-y-2">
                                            {result.playbook.immediate_actions.map((action, i) => (
                                                <div key={i} className="flex items-start gap-3 p-3 bg-red-50 rounded-lg">
                                                    <span className="step-number bg-red-500 flex-shrink-0">{i + 1}</span>
                                                    <p className="text-slate-700">{action}</p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Recovery Steps */}
                                {result.playbook?.recovery_steps?.length > 0 && (
                                    <div className="mb-6">
                                        <h4 className="font-semibold text-primary-600 mb-3 flex items-center gap-2">
                                            📖 Recovery Steps
                                        </h4>
                                        <div className="space-y-3">
                                            {result.playbook.recovery_steps.map((step, i) => (
                                                <div key={i} className="flex items-start gap-3 p-4 bg-white rounded-lg border border-primary-100">
                                                    <span className="step-number flex-shrink-0">{step.step}</span>
                                                    <div>
                                                        <p className="text-slate-800 font-medium">{step.action}</p>
                                                        {step.minutes && (
                                                            <p className="text-sm text-slate-500 mt-1">
                                                                ⏱️ {step.minutes} minutes
                                                            </p>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Alternatives */}
                                {result.playbook?.alternatives?.length > 0 && (
                                    <div className="mb-6">
                                        <h4 className="font-semibold text-accent-600 mb-3">
                                            🔄 Alternative Strategies
                                        </h4>
                                        <ul className="list-disc list-inside space-y-1 text-slate-700">
                                            {result.playbook.alternatives.map((alt, i) => (
                                                <li key={i}>{alt}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {/* Success Indicators */}
                                {result.playbook?.success_indicators?.length > 0 && (
                                    <div className="mb-6">
                                        <h4 className="font-semibold text-secondary-600 mb-3">
                                            ✅ Success Indicators
                                        </h4>
                                        <ul className="list-disc list-inside space-y-1 text-slate-700">
                                            {result.playbook.success_indicators.map((ind, i) => (
                                                <li key={i}>{ind}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {/* YouTube Videos */}
                                {result.playbook?.youtube_videos?.length > 0 && (
                                    <div className="mb-6">
                                        <h4 className="font-semibold text-red-600 mb-3 flex items-center gap-2">
                                            📺 Recommended Videos
                                        </h4>
                                        <div className="space-y-3">
                                            {result.playbook.youtube_videos.map((video, i) => (
                                                <a
                                                    key={i}
                                                    href={video.url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="flex items-center gap-3 p-3 bg-red-50 hover:bg-red-100 rounded-lg transition-colors group"
                                                >
                                                    <div className="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center flex-shrink-0">
                                                        <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
                                                            <path d="M10 15l5.19-3L10 9v6m11.56-7.83c.13.47.22 1.1.28 1.9.07.8.1 1.49.1 2.09L22 12c0 2.19-.16 3.8-.44 4.83-.25.9-.83 1.48-1.73 1.73-.47.13-1.33.22-2.65.28-1.3.07-2.49.1-3.59.1L12 19c-4.19 0-6.8-.16-7.83-.44-.9-.25-1.48-.83-1.73-1.73-.13-.47-.22-1.1-.28-1.9-.07-.8-.1-1.49-.1-2.09L2 12c0-2.19.16-3.8.44-4.83.25-.9.83-1.48 1.73-1.73.47-.13 1.33-.22 2.65-.28 1.3-.07 2.49-.1 3.59-.1L12 5c4.19 0 6.8.16 7.83.44.9.25 1.48.83 1.73 1.73z" />
                                                        </svg>
                                                    </div>
                                                    <div className="flex-1">
                                                        <p className="font-medium text-slate-800 group-hover:text-red-600">{video.title}</p>
                                                        {video.description && (
                                                            <p className="text-sm text-slate-500">{video.description}</p>
                                                        )}
                                                    </div>
                                                    <span className="text-red-500 text-sm">Watch →</span>
                                                </a>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* NCERT Reference */}
                                {result.playbook?.ncert_reference && (
                                    <div className="mb-6">
                                        <h4 className="font-semibold text-blue-600 mb-3 flex items-center gap-2">
                                            📚 NCERT Reference
                                        </h4>
                                        <div className="p-4 bg-blue-50 rounded-lg text-slate-700">
                                            <p className="whitespace-pre-wrap">{result.playbook.ncert_reference}</p>
                                        </div>
                                    </div>
                                )}

                                {/* Teaching Tips */}
                                {result.playbook?.teaching_tips?.length > 0 && (
                                    <div className="mb-6">
                                        <h4 className="font-semibold text-amber-600 mb-3 flex items-center gap-2">
                                            💡 Quick Teaching Tips
                                        </h4>
                                        <ul className="space-y-2">
                                            {result.playbook.teaching_tips.map((tip, i) => (
                                                <li key={i} className="flex items-start gap-2 text-slate-700">
                                                    <span className="text-amber-500">💡</span>
                                                    <span>{tip}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {/* Teaching Resources */}
                                {result.playbook?.teaching_resources?.length > 0 && (
                                    <div>
                                        <h4 className="font-semibold text-purple-600 mb-3 flex items-center gap-2">
                                            🔗 Teaching Resources
                                        </h4>
                                        <div className="space-y-2">
                                            {result.playbook.teaching_resources.map((resource, i) => (
                                                <div key={i} className="flex items-center gap-2 p-2 bg-purple-50 rounded-lg text-slate-700">
                                                    <span className="px-2 py-0.5 bg-purple-200 text-purple-700 rounded text-xs uppercase">
                                                        {resource.resource_type}
                                                    </span>
                                                    <span>{resource.title}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Processing Time */}
                            {result.processing_time_ms && (
                                <p className="text-center text-sm text-slate-500 mb-6">
                                    Generated in {(result.processing_time_ms / 1000).toFixed(1)}s
                                </p>
                            )}

                            {/* Actions */}
                            <div className="flex flex-col sm:flex-row gap-4 justify-center">
                                <button
                                    onClick={resetForm}
                                    className="btn-primary flex items-center justify-center gap-2"
                                >
                                    <AlertCircle className="w-5 h-5" />
                                    New SOS Request
                                </button>
                                <Link
                                    to="/register"
                                    className="btn-secondary flex items-center justify-center gap-2"
                                >
                                    Save & Track History
                                </Link>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </main>
        </div>
    );
}
