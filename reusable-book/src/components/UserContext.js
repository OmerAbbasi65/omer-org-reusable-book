import React, { createContext, useState, useEffect, useContext } from 'react';

const UserContext = createContext(null);

export const UserProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userData, setUserData] = useState(null);
  const [personalizationEnabled, setPersonalizationEnabled] = useState(false);
  const [translationEnabled, setTranslationEnabled] = useState(false);

  useEffect(() => {
    // Check local storage for login status and user data
    // Only access localStorage on the client side
    if (typeof window !== 'undefined') {
      const loggedInStatus = localStorage.getItem('isLoggedIn') === 'true';
      setIsLoggedIn(loggedInStatus);

      const storedUserData = localStorage.getItem('userData');
      if (storedUserData) {
        setUserData(JSON.parse(storedUserData));
      }
    }
  }, []);

  const login = (username, password) => {
    // In a real app, this would involve API calls
    if (username === 'test' && password === 'test') {
      if (typeof window !== 'undefined') {
        localStorage.setItem('isLoggedIn', 'true');
        const storedUserData = localStorage.getItem('userData');
        if (storedUserData) {
          setUserData(JSON.parse(storedUserData));
        } else {
          // Fallback if no specific userData from signup
          const fallbackData = { username: 'test', softwareBackground: 'unknown', hardwareBackground: 'unknown' };
          localStorage.setItem('userData', JSON.stringify(fallbackData));
          setUserData(fallbackData);
        }
      }
      setIsLoggedIn(true);
      return true;
    }
    return false;
  };

  const signup = (data) => {
    // In a real app, this would involve API calls
    if (typeof window !== 'undefined') {
      localStorage.setItem('userData', JSON.stringify(data));
      localStorage.setItem('isLoggedIn', 'true');
    }
    setUserData(data);
    setIsLoggedIn(true);
    return true;
  };

  const logout = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('isLoggedIn');
      localStorage.removeItem('userData');
    }
    setIsLoggedIn(false);
    setUserData(null);
    setPersonalizationEnabled(false); // Reset personalization on logout
    setTranslationEnabled(false); // Reset translation on logout
  };

  const togglePersonalization = () => {
    setPersonalizationEnabled(prev => !prev);
  };

  const toggleTranslation = () => {
    setTranslationEnabled(prev => !prev);
  };

  return (
    <UserContext.Provider value={{
      isLoggedIn,
      userData,
      login,
      signup,
      logout,
      personalizationEnabled,
      togglePersonalization,
      translationEnabled,
      toggleTranslation
    }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);

  // Return default values during SSR/SSG when context is null
  if (context === null) {
    return {
      isLoggedIn: false,
      userData: null,
      login: () => false,
      signup: () => false,
      logout: () => {},
      personalizationEnabled: false,
      togglePersonalization: () => {},
      translationEnabled: false,
      toggleTranslation: () => {},
    };
  }

  return context;
};
