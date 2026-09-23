import React, { createContext, useContext, useState } from 'react';

interface User {
  id: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Stable mock user for Phase 0
  const [user] = useState<User>({ id: 'mock-user-123', name: 'Demo User' });

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};
