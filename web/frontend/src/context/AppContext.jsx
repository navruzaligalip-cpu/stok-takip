import { createContext, useContext, useState, useCallback } from 'react';
import { categoriesApi } from '../utils/api';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [categories, setCategories] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const loadCategories = useCallback(async () => {
    try {
      const res = await categoriesApi.getAll();
      setCategories(res.data);
    } catch { /* ignore */ }
  }, []);

  return (
    <AppContext.Provider value={{ categories, loadCategories, sidebarOpen, setSidebarOpen }}>
      {children}
    </AppContext.Provider>
  );
}

export const useApp = () => useContext(AppContext);
