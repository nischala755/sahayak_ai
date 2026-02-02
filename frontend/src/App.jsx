import { Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';

// Pages
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import SOSPage from './pages/SOSPage';
import History from './pages/History';

// Role-Based Dashboards
import TeacherDashboard from './pages/TeacherDashboard';
import CRPDashboard from './pages/CRPDashboard';
import DIETDashboard from './pages/DIETDashboard';

// Layout
import DashboardLayout from './components/layout/DashboardLayout';

// Smart Dashboard Router - shows role-specific dashboard
function SmartDashboard({ user }) {
    const role = user?.role?.toLowerCase();

    switch (role) {
        case 'crp':
            return <CRPDashboard user={user} />;
        case 'diet':
            return <DIETDashboard user={user} />;
        case 'teacher':
        default:
            return <TeacherDashboard user={user} />;
    }
}

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check for existing auth on mount
        const token = localStorage.getItem('token');
        const savedUser = localStorage.getItem('user');

        if (token && savedUser) {
            setIsAuthenticated(true);
            setUser(JSON.parse(savedUser));
        }
        setLoading(false);
    }, []);

    const handleLogin = (userData, token) => {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
        setIsAuthenticated(true);
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
        setIsAuthenticated(false);
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
            </div>
        );
    }

    return (
        <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Landing />} />
            <Route
                path="/login"
                element={
                    isAuthenticated ?
                        <Navigate to="/dashboard" replace /> :
                        <Login onLogin={handleLogin} />
                }
            />
            <Route
                path="/register"
                element={
                    isAuthenticated ?
                        <Navigate to="/dashboard" replace /> :
                        <Register onLogin={handleLogin} />
                }
            />

            {/* Quick SOS (No auth needed for demo) */}
            <Route path="/sos" element={<SOSPage />} />

            {/* Protected Routes - Smart Dashboard */}
            <Route
                path="/dashboard"
                element={
                    isAuthenticated ? (
                        <DashboardLayout user={user} onLogout={handleLogout}>
                            <SmartDashboard user={user} />
                        </DashboardLayout>
                    ) : (
                        <Navigate to="/login" replace />
                    )
                }
            />

            {/* Legacy Dashboard (for backward compatibility) */}
            <Route
                path="/dashboard/legacy"
                element={
                    isAuthenticated ? (
                        <DashboardLayout user={user} onLogout={handleLogout}>
                            <Dashboard user={user} />
                        </DashboardLayout>
                    ) : (
                        <Navigate to="/login" replace />
                    )
                }
            />

            <Route
                path="/history"
                element={
                    isAuthenticated ? (
                        <DashboardLayout user={user} onLogout={handleLogout}>
                            <History />
                        </DashboardLayout>
                    ) : (
                        <Navigate to="/login" replace />
                    )
                }
            />

            {/* Catch all */}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}

export default App;

