import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    LayoutDashboard,
    AlertCircle,
    History,
    Settings,
    LogOut,
    Menu,
    X,
    GraduationCap,
    ChevronRight
} from 'lucide-react';

const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/sos', label: 'New SOS', icon: AlertCircle },
    { path: '/history', label: 'History', icon: History },
];

export default function DashboardLayout({ children, user, onLogout }) {
    const location = useLocation();
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <div className="min-h-screen bg-slate-100">
            {/* Mobile Header */}
            <div className="lg:hidden bg-white shadow-sm px-4 py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
                        <GraduationCap className="w-6 h-6 text-white" />
                    </div>
                    <span className="font-bold text-xl text-primary-700">SAHAYAK AI</span>
                </div>
                <button
                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                    className="p-2 rounded-lg hover:bg-slate-100"
                >
                    {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                </button>
            </div>

            {/* Mobile Menu Overlay */}
            <AnimatePresence>
                {mobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="lg:hidden fixed inset-0 bg-black/50 z-40"
                        onClick={() => setMobileMenuOpen(false)}
                    />
                )}
            </AnimatePresence>

            {/* Mobile Sidebar */}
            <AnimatePresence>
                {mobileMenuOpen && (
                    <motion.div
                        initial={{ x: -280 }}
                        animate={{ x: 0 }}
                        exit={{ x: -280 }}
                        transition={{ type: 'spring', damping: 25 }}
                        className="lg:hidden fixed left-0 top-0 bottom-0 w-72 bg-white z-50 shadow-xl"
                    >
                        <SidebarContent
                            user={user}
                            onLogout={onLogout}
                            location={location}
                            onNavClick={() => setMobileMenuOpen(false)}
                        />
                    </motion.div>
                )}
            </AnimatePresence>

            <div className="flex">
                {/* Desktop Sidebar */}
                <motion.div
                    initial={false}
                    animate={{ width: sidebarOpen ? 280 : 80 }}
                    className="hidden lg:block bg-white h-screen sticky top-0 shadow-lg"
                >
                    <SidebarContent
                        user={user}
                        onLogout={onLogout}
                        location={location}
                        collapsed={!sidebarOpen}
                        onToggle={() => setSidebarOpen(!sidebarOpen)}
                    />
                </motion.div>

                {/* Main Content */}
                <main className="flex-1 p-4 lg:p-8 min-h-screen">
                    {children}
                </main>
            </div>
        </div>
    );
}

function SidebarContent({ user, onLogout, location, collapsed = false, onToggle, onNavClick }) {
    return (
        <div className="h-full flex flex-col p-4">
            {/* Logo */}
            <div className="flex items-center gap-3 mb-8 px-2">
                <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
                    <GraduationCap className="w-7 h-7 text-white" />
                </div>
                {!collapsed && (
                    <div>
                        <h1 className="font-bold text-xl text-primary-700">SAHAYAK AI</h1>
                        <p className="text-xs text-slate-500">Classroom Coach</p>
                    </div>
                )}
                {onToggle && (
                    <button
                        onClick={onToggle}
                        className="ml-auto p-2 rounded-lg hover:bg-slate-100 hidden lg:block"
                    >
                        <ChevronRight className={`w-5 h-5 transition-transform ${!collapsed ? 'rotate-180' : ''}`} />
                    </button>
                )}
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-2">
                {navItems.map((item) => {
                    const isActive = location.pathname === item.path;
                    const Icon = item.icon;

                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            onClick={onNavClick}
                            className={`sidebar-link ${isActive ? 'active' : ''} ${collapsed ? 'justify-center px-3' : ''}`}
                        >
                            <Icon className={`w-5 h-5 ${collapsed ? '' : ''}`} />
                            {!collapsed && <span>{item.label}</span>}
                        </Link>
                    );
                })}
            </nav>

            {/* User Section */}
            <div className={`border-t pt-4 mt-4 ${collapsed ? 'text-center' : ''}`}>
                {!collapsed && user && (
                    <div className="px-3 mb-4">
                        <p className="font-medium text-slate-800">{user.name}</p>
                        <p className="text-sm text-slate-500 capitalize">{user.role}</p>
                    </div>
                )}
                <button
                    onClick={onLogout}
                    className={`sidebar-link text-red-500 hover:bg-red-50 hover:text-red-600 w-full ${collapsed ? 'justify-center px-3' : ''}`}
                >
                    <LogOut className="w-5 h-5" />
                    {!collapsed && <span>Logout</span>}
                </button>
            </div>
        </div>
    );
}
