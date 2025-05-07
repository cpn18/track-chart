import React, { createContext, useContext, useState } from 'react';

// new context for managing theme state
const ThemeContext = createContext();

/**
 * ThemeProvider Component
 * provides a dark mode toggle functionality across PiRail
 * react context API shares theme state
 */

export const ThemeProvider = ({ children }) => {
  // track if dark mode is enabled/not
  const [isDarkMode, setIsDarkMode] = useState(false);

  /**
   * toggles dark mode on/off
   * flips the cur state of isDarkMode.
   */
  const toggleDarkMode = () => setIsDarkMode(!isDarkMode);

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleDarkMode }}>
      {/* dark mode class (if enabled) */}
      <div className={isDarkMode ? 'dark-mode' : ''}>{children}</div>
    </ThemeContext.Provider>
  );
};

/**
 * hook to use the ThemeContext
 * components can access dark mode state + toggle func.
 */
export const useTheme = () => useContext(ThemeContext);