import { AuthProvider } from './context/AuthContext';
import { ReducedMotionProvider, ReducedMotionToggle } from './components/ReducedMotionToggle';
import { LegalDisclaimer } from './components/LegalDisclaimer';
import { Dashboard } from './components/Dashboard';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <ReducedMotionProvider>
        <div className="app-container" style={{ minHeight: '100vh', backgroundColor: '#090D16', color: '#F8FAFC' }}>
          <LegalDisclaimer />
          
          <main style={{ padding: '2rem' }}>
            <h1 style={{ fontFamily: 'Plus Jakarta Sans, sans-serif', fontSize: '32px', marginBottom: '2rem', textAlign: 'center' }}>
              Legal Document Intelligence Platform
            </h1>
            <Dashboard />
          </main>

          <ReducedMotionToggle />
        </div>
      </ReducedMotionProvider>
    </AuthProvider>
  );
}

export default App;

