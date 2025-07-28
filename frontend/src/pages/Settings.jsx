import React, { useState } from 'react';
import './settings.css';

export default function Settings() {
  const [username, setUsername] = useState('User Name');
  const [editingUsername, setEditingUsername] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [email, setEmail] = useState('user@email.com');
  const [editingEmail, setEditingEmail] = useState(false);
  const [newEmail, setNewEmail] = useState('');
  const [showPasswordFields, setShowPasswordFields] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [language, setLanguage] = useState('EN');
  const [theme, setTheme] = useState('light');

  const canSave =
    (editingUsername && newUsername) ||
    (editingEmail && newEmail) ||
    (showPasswordFields && newPassword && newPassword === confirmPassword);

  return (
    <div className="settings-container">
      <div className="settings-title">Settings</div>
      <form onSubmit={e => e.preventDefault()}>
        <div className="settings-section settings-row">
          <label htmlFor="username" style={{ flex: 1 }}>Username</label>
          <input
            type="text"
            id="username"
            value={editingUsername ? newUsername : username}
            onChange={e => setNewUsername(e.target.value)}
            placeholder={username}
            autoComplete="username"
            disabled={!editingUsername}
            style={{ flex: 2, marginRight: 8 }}
          />
          <button
            type="button"
            className="settings-btn secondary"
            style={{ minWidth: 60 }}
            onClick={() => {
              if (!editingUsername) {
                setEditingUsername(true);
                setNewUsername(username);
              } else {
                setEditingUsername(false);
                setNewUsername('');
              }
            }}
          >{editingUsername ? 'Cancel' : 'Edit'}</button>
        </div>
        <div className="settings-section settings-row">
          <label htmlFor="email" style={{ flex: 1 }}>Email</label>
          <input
            type="email"
            id="email"
            value={editingEmail ? newEmail : email}
            onChange={e => setNewEmail(e.target.value)}
            placeholder={email}
            autoComplete="email"
            disabled={!editingEmail}
            style={{ flex: 2, marginRight: 8 }}
          />
          <button
            type="button"
            className="settings-btn secondary"
            style={{ minWidth: 60 }}
            onClick={() => {
              if (!editingEmail) {
                setEditingEmail(true);
                setNewEmail(email);
              } else {
                setEditingEmail(false);
                setNewEmail('');
              }
            }}
          >{editingEmail ? 'Cancel' : 'Edit'}</button>
        </div>
        <div className="settings-section settings-row">
          <label style={{ flex: 1 }}>Password</label>
          <button
            type="button"
            className="settings-btn secondary"
            style={{ minWidth: 140 }}
            onClick={() => setShowPasswordFields(v => !v)}
          >{showPasswordFields ? 'Cancel' : 'Update Password'}</button>
        </div>
        {showPasswordFields && (
          <>
            <div className="settings-section">
              <label htmlFor="password">New Password</label>
              <input
                type="password"
                id="password"
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                placeholder="Enter new password"
                autoComplete="new-password"
              />
            </div>
            <div className="settings-section">
              <label htmlFor="confirmPassword">Confirm New Password</label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                placeholder="Confirm new password"
                autoComplete="new-password"
              />
            </div>
          </>
        )}
        <div className="settings-section settings-row">
          <div style={{ flex: 1 }}>
            <label htmlFor="language">Language</label>
            <select
              id="language"
              className="settings-dropdown"
              value={language}
              onChange={e => setLanguage(e.target.value)}
              style={{ width: '100%', padding: '0.7rem 1rem', borderRadius: 8, border: '1px solid #bcdffb', fontSize: '1rem', background: '#f9f9f9', marginBottom: 0 }}
            >
              <option value="EN">English</option>
              <option value="FR">Français</option>
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label htmlFor="theme">Theme</label>
            <select
              id="theme"
              className="settings-dropdown"
              value={theme}
              onChange={e => setTheme(e.target.value)}
              style={{ width: '100%', padding: '0.7rem 1rem', borderRadius: 8, border: '1px solid #bcdffb', fontSize: '1rem', background: '#f9f9f9', marginBottom: 0 }}
            >
              <option value="light">Light Mode</option>
              <option value="dark">Dark Mode</option>
            </select>
          </div>
        </div>
        <div className="settings-row" style={{ marginTop: 24, justifyContent: 'flex-end' }}>
          <button
            className="settings-btn"
            type="button"
            disabled={!canSave}
            style={{ minWidth: 120 }}
          >
            Save Changes
          </button>
        </div>
      </form>
    </div>
  );
}
