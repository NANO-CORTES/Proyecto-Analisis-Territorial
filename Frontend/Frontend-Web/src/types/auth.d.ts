interface AuthContextType {
  isAuthenticated: boolean;
  username: string | null;
  role: 'ADMIN' | 'USER' | null;
  token: string | null;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
}