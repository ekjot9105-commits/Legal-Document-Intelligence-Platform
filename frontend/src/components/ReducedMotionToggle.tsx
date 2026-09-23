import React, { createContext, useContext, useEffect, useState } from 'react';

interface MotionContextType {
  reducedMotion: boolean;
  setReducedMotion: (value: boolean) => void;
}

const MotionContext = createContext<MotionContextType>({
  reducedMotion: false,
  setReducedMotion: () => {},
});

export const useReducedMotion = () => useContext(MotionContext);

export const ReducedMotionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [reducedMotion, setReducedMotion] = useState(() => {
    const saved = localStorage.getItem('reducedMotion');
    if (saved !== null) return JSON.parse(saved);
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  });

  useEffect(() => {
    localStorage.setItem('reducedMotion', JSON.stringify(reducedMotion));
    if (reducedMotion) {
      document.body.classList.add('reduced-motion');
    } else {
      document.body.classList.remove('reduced-motion');
    }
  }, [reducedMotion]);

  return (
    <MotionContext.Provider value={{ reducedMotion, setReducedMotion }}>
      {children}
    </MotionContext.Provider>
  );
};

export const ReducedMotionToggle: React.FC = () => {
  const { reducedMotion, setReducedMotion } = useReducedMotion();

  return (
    <button 
      onClick={() => setReducedMotion(!reducedMotion)}
      aria-pressed={reducedMotion}
      title="Toggle Reduced Motion for 3D and animations"
      style={{
        position: 'fixed',
        bottom: '1rem',
        right: '1rem',
        padding: '0.5rem',
        background: '#333',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer'
      }}
    >
      {reducedMotion ? 'Animations Off 🛑' : 'Animations On 🌟'}
    </button>
  );
};
