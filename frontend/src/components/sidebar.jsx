import React from 'react';
import { useNavigate } from 'react-router-dom';
import HomeIcon from '../assets/home.svg';
import SignalIcon from '../assets/signal.svg';
import ClipboardIcon from '../assets/clipboard.svg';
import SettingsIcon from '../assets/settings.svg';
import LogoutIcon from '../assets/logout.svg';
import AlertIcon from '../assets/alert.svg';
import logo from '../assets/logo.png'
import UserManagement  from '../assets/userManagement.svg';
const menuItems = [
    { label: 'Dashboard', path: '/', icon: HomeIcon },
    { label: 'Alerts', path: '/alerts', count: 4, icon: AlertIcon },
    { label: 'Patients', path: '/patients', icon: SignalIcon },
    { label: 'Settings', path: '/settings', icon: SettingsIcon },
    { label: 'Logout', path: '/logout', icon: LogoutIcon },
    { label: 'Help', path: '/help', icon: null },
    { label: 'Contact Us', path: '/contact', icon: null },
];

export default function Sidebar() {
    const navigate = useNavigate();
    const role = localStorage.getItem('role');
    return (
        <nav className="sidebar">
            <div className="sidebar-brand">
                <img src={logo} alt="CardioMonitor Logo" />
                <span>CardioMonitor</span>
            </div>
            
            <ul>
                {role === 'admin' && (
                    <li style={{ cursor: 'pointer' }} onClick={() => navigate('/user-management')}>
                        <img src={UserManagement} alt="User Management" style={{ width: 22, height: 22, marginRight: 8, verticalAlign: 'middle', marginBottom: 3 }} />
                        Users
                    </li>
                )}
                {menuItems.map((item) => (
                    <li key={item.label} style={{ cursor: item.path ? 'pointer' : 'default', position: 'relative' }}
                        onClick={() => item.path && navigate(item.path)}>
                        {item.icon && <img src={item.icon} alt="" style={{ width: 22, height: 22, marginRight: 8, verticalAlign: 'middle', marginBottom: 3 }} />}
                        {item.label}
                        {item.count && <span> ({item.count})</span>}
                        {item.label === 'Alerts' && item.count > 0 && (
                          <span style={{
                            position: 'absolute',
                            left: 10,
                            top: 2,
                            width: 12,
                            height: 12,
                            background: '#f44336',
                            borderRadius: '50%',
                            display: 'inline-block',
                            border: '2px solid #fff',
                            boxShadow: '0 0 2px #888',
                          }}></span>
                        )}
                    </li>
                ))}
                
            </ul>
        </nav>
    );
}
