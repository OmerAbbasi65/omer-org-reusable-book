import React from 'react';
import { useUser } from './UserContext';

const TranslatedContent = ({ children, urduContent }) => {
  const { translationEnabled } = useUser();

  if (translationEnabled) {
    return <div style={{ direction: 'rtl', textAlign: 'right', borderRight: '3px solid #28a745', paddingRight: '10px', marginTop: '10px', backgroundColor: '#e8f5e9' }}>{urduContent}</div>;
  }
  return children;
};

export default TranslatedContent;
