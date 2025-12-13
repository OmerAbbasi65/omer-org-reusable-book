import React from 'react';
import { useUser } from './UserContext';

// Custom component to demonstrate personalization
const PersonalizedContent = ({ children, forSoftware, forHardware }) => {
  const { personalizationEnabled, userData } = useUser();

  if (!personalizationEnabled || !userData) {
    return null;
  }

  const userSoftware = userData.softwareBackground.toLowerCase();
  const userHardware = userData.hardwareBackground.toLowerCase();

  const showSoftware = forSoftware && userSoftware.includes(forSoftware.toLowerCase());
  const showHardware = forHardware && userHardware.includes(forHardware.toLowerCase());

  if (showSoftware || showHardware) {
    return <div style={{ borderLeft: '3px solid #0066ff', paddingLeft: '10px', marginTop: '10px', fontStyle: 'italic' }}>{children}</div>;
  }
  return null;
};

export default PersonalizedContent;