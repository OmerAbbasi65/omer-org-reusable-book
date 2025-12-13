import React from 'react';
import { useUser } from './UserContext';

const PersonalizationToggle = () => {
  const { isLoggedIn, personalizationEnabled, togglePersonalization } = useUser();

  if (!isLoggedIn) {
    return null; // Don't show toggle if not logged in
  }

  return (
    <div style={{ marginBottom: '1rem', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '5px', backgroundColor: '#f0f0f0' }}>
      <label>
        <input
          type="checkbox"
          checked={personalizationEnabled}
          onChange={togglePersonalization}
          style={{ marginRight: '0.5rem' }}
        />
        Enable Personalized Content
      </label>
    </div>
  );
};

export default PersonalizationToggle;
