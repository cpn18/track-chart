import React, { createContext, useContext, useState } from 'react';

// create the context
const PoiContext = createContext();

// custom hook to use the context
export const usePoi = () => {
  const context = useContext(PoiContext);
  if (!context) {
    throw new Error("usePoi must be used within a PoiProvider");
  }
  return context; // return the context (pois and setPois)
};

// provide the context
export const PoiProvider = ({ children }) => {
  const [pois, setPois] = useState([]); // init as an empty array for POIs

  return (
    <PoiContext.Provider value={[pois, setPois]}>
      {children}
    </PoiContext.Provider>
  );
};
