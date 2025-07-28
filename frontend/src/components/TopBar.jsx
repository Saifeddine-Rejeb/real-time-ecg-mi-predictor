import React, { useState, useRef, useEffect } from 'react';
import './TopBar.css';

export default function TopBar({ user, email }) {
  const [showProfile, setShowProfile] = useState(false);
  const profileRef = useRef();

  // Close popup when clicking outside
  useEffect(() => {
    function handleClick(e) {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setShowProfile(false);
      }
    }
    if (showProfile) {
      document.addEventListener('mousedown', handleClick);
    } else {
      document.removeEventListener('mousedown', handleClick);
    }
    return () => document.removeEventListener('mousedown', handleClick);
  }, [showProfile]);

  return (
    <div className="top-bar">
      <div className="top-bar-left"></div>
      <div className="top-bar-right">
        <div style={{ position: 'relative' }}>
          <button
            className="top-bar-profile"
            onClick={() => setShowProfile((v) => !v)}
            title="Profile"
          >
            <span className="profile-avatar">{user?.[0] || 'U'}</span>
          </button>
          {showProfile && (
            <div className="profile-popup" ref={profileRef}>
              <div className="profile-popup-avatar">{user?.[0] || 'U'}</div>
              <div className="profile-popup-name">{user}</div>
              <div className="profile-popup-email">{email}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
