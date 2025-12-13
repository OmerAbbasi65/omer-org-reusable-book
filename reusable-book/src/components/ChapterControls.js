import React from 'react';
import { useUser } from './UserContext';

const ChapterControls = () => {
  const { isLoggedIn, personalizationEnabled, togglePersonalization, translationEnabled, toggleTranslation } = useUser();

  if (!isLoggedIn) {
    return null; // Don't show controls if not logged in
  }

  return (
    <div style={{ marginBottom: '1rem', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '5px', backgroundColor: '#f0f0f0', display: 'flex', gap: '1rem' }}>
      <label>
        <input
          type="checkbox"
          checked={personalizationEnabled}
          onChange={togglePersonalization}
          style={{ marginRight: '0.5rem' }}
        />
        Enable Personalized Content
      </label>
      <label>
        <input
          type="checkbox"
          checked={translationEnabled}
          onChange={toggleTranslation}
          style={{ marginRight: '0.5rem' }}
        />
        Translate to Urdu
      </label>
    </div>
  );
};

export default ChapterControls;
