import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    GraduationCap,
    Mic,
    Zap,
    BookOpen,
    Users,
    ArrowRight,
    CheckCircle,
    Globe
} from 'lucide-react';

export default function Landing() {
    return (
        <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
            {/* Header */}
            <header className="bg-white/80 backdrop-blur-sm border-b border-slate-100 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
                                <GraduationCap className="w-6 h-6 text-white" />
                            </div>
                            <span className="font-bold text-xl text-primary-700">SAHAYAK AI</span>
                        </div>
                        <div className="flex items-center gap-4">
                            <Link to="/login" className="text-slate-600 hover:text-primary-600 font-medium">
                                Login
                            </Link>
                            <Link to="/register" className="btn-primary text-sm py-2">
                                Get Started
                            </Link>
                        </div>
                    </div>
                </div>
            </header>

            {/* Hero Section */}
            <section className="relative overflow-hidden">
                <div className="absolute inset-0 bg-mesh"></div>
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32 relative">
                    <div className="grid lg:grid-cols-2 gap-12 items-center">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6 }}
                        >
                            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-50 rounded-full text-primary-600 font-medium text-sm mb-6">
                                <Zap className="w-4 h-4" />
                                AI-Powered Classroom Rescue
                            </div>
                            <h1 className="text-4xl lg:text-6xl font-bold text-slate-900 mb-6 leading-tight">
                                Get Instant Help
                                <span className="text-gradient block">When Class Breaks Down</span>
                            </h1>
                            <p className="text-lg text-slate-600 mb-8 max-w-lg">
                                SAHAYAK AI provides real-time pedagogical rescue for government school teachers.
                                Voice your problem, get an AI-generated teaching playbook in seconds.
                            </p>
                            <div className="flex flex-wrap gap-4">
                                <Link to="/sos" className="btn-primary flex items-center gap-2">
                                    <Mic className="w-5 h-5" />
                                    Try Quick SOS
                                    <ArrowRight className="w-4 h-4" />
                                </Link>
                                <Link to="/register" className="btn-secondary flex items-center gap-2">
                                    Create Free Account
                                </Link>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.6, delay: 0.2 }}
                            className="relative hidden lg:block"
                        >
                            <div className="glass-card p-8 relative">
                                <div className="absolute -top-4 -right-4 w-20 h-20 bg-accent-500 rounded-2xl flex items-center justify-center shadow-lg animate-float">
                                    <Mic className="w-10 h-10 text-white" />
                                </div>
                                <h3 className="font-semibold text-lg mb-4">Sample SOS Request</h3>
                                <p className="text-slate-600 italic mb-6">
                                    "Students in my Class 5 are not understanding how to add fractions with different denominators..."
                                </p>
                                <div className="bg-secondary-50 rounded-xl p-4 border border-secondary-200">
                                    <div className="flex items-center gap-2 text-secondary-700 font-medium mb-2">
                                        <CheckCircle className="w-5 h-5" />
                                        AI Playbook Generated
                                    </div>
                                    <p className="text-sm text-slate-600">
                                        ✓ Visual fraction strips activity<br />
                                        ✓ Peer teaching pairs<br />
                                        ✓ 12 min recovery time
                                    </p>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="py-20 bg-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-4">
                            How SAHAYAK AI Helps
                        </h2>
                        <p className="text-slate-600 max-w-2xl mx-auto">
                            Our AI understands classroom contexts and generates actionable teaching strategies instantly.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {features.map((feature, index) => (
                            <motion.div
                                key={feature.title}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.1 }}
                                viewport={{ once: true }}
                                className="stat-card text-center"
                            >
                                <div className={`w-16 h-16 mx-auto mb-6 rounded-2xl flex items-center justify-center ${feature.bg}`}>
                                    <feature.icon className={`w-8 h-8 ${feature.color}`} />
                                </div>
                                <h3 className="text-xl font-semibold text-slate-900 mb-3">{feature.title}</h3>
                                <p className="text-slate-600">{feature.description}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="py-20 bg-hero-pattern">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid md:grid-cols-4 gap-8 text-center text-white">
                        {stats.map((stat, index) => (
                            <motion.div
                                key={stat.label}
                                initial={{ opacity: 0 }}
                                whileInView={{ opacity: 1 }}
                                transition={{ delay: index * 0.1 }}
                                viewport={{ once: true }}
                            >
                                <div className="text-4xl lg:text-5xl font-bold mb-2">{stat.value}</div>
                                <div className="text-primary-200">{stat.label}</div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <h2 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-6">
                        Ready to Transform Your Classroom?
                    </h2>
                    <p className="text-slate-600 mb-8 max-w-2xl mx-auto">
                        Join thousands of teachers using SAHAYAK AI for instant classroom support.
                        No training needed - just speak or type your problem.
                    </p>
                    <div className="flex flex-wrap justify-center gap-4">
                        <Link to="/register" className="btn-primary text-lg px-8">
                            Start Free Today
                        </Link>
                        <Link to="/sos" className="btn-secondary text-lg px-8">
                            Try Demo
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-slate-900 text-slate-400 py-12">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
                                <GraduationCap className="w-6 h-6 text-white" />
                            </div>
                            <span className="font-bold text-white">SAHAYAK AI</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <Globe className="w-4 h-4" />
                            <span>Built for Indian Government Schools</span>
                        </div>
                        <p className="text-sm">© 2026 Shikshalokam. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}

const features = [
    {
        title: 'Voice SOS',
        description: 'Speak your classroom problem naturally. Our AI understands context, subject, and urgency.',
        icon: Mic,
        bg: 'bg-primary-100',
        color: 'text-primary-600',
    },
    {
        title: 'Instant Playbooks',
        description: 'Get structured rescue strategies with step-by-step actions in under 10 seconds.',
        icon: BookOpen,
        bg: 'bg-secondary-100',
        color: 'text-secondary-600',
    },
    {
        title: 'Classroom Memory',
        description: 'The system learns from past situations to give you personalized recommendations.',
        icon: Users,
        bg: 'bg-accent-100',
        color: 'text-accent-600',
    },
];

const stats = [
    { value: '10K+', label: 'Teachers Helped' },
    { value: '50K+', label: 'Playbooks Generated' },
    { value: '<10s', label: 'Response Time' },
    { value: '12', label: 'Languages' },
];
