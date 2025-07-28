import React, { useEffect, useState } from 'react';
import './userManagement.css';
import UserTable from '../components/UserTable';

function UserModal({ show, modalType, modalUser, onChange, onSubmit, onClose }) {
  if (!show) return null;
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h3>{modalType === 'edit' ? 'Edit User' : modalType === 'admin' ? 'Add Admin' : 'Add Doctor'}</h3>
        <input
          type="text"
          placeholder="Name"
          value={modalUser.name}
          onChange={e => onChange({ ...modalUser, name: e.target.value })}
          className="modal-input"
        />
        <input
          type="email"
          placeholder="Email"
          value={modalUser.email}
          onChange={e => onChange({ ...modalUser, email: e.target.value })}
          className="modal-input"
        />
        <div className="modal-btn-row">
          <button className="edit-btn" onClick={onSubmit}>{modalType === 'edit' ? 'Save' : 'Add'}</button>
          <button className="remove-btn" onClick={onClose}>Cancel</button>
        </div>
      </div>
    </div>
  );
}


// API helpers
const API_BASE = 'http://localhost:5000/api/users';

async function fetchAllUsers() {
  // Get all users (admins + doctors)
  const [adminsRes, doctorsRes] = await Promise.all([
    fetch(`${API_BASE}/admins`),
    fetch(`${API_BASE}/doctors`)
  ]);
  const admins = await adminsRes.json();
  const doctors = await doctorsRes.json();
  // Normalize _id to id, type to role, and default online to false if missing
  function normalizeUser(u) {
    return {
      ...u,
      id: u._id || u.id,
      role: u.role || u.type || '',
      online: typeof u.status === 'boolean' ? u.status : false
    };
  }
  return [...admins, ...doctors].map(normalizeUser);
}

async function apiAddUser(user) {
  const res = await fetch(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user)
  });
  return res.json();
}

async function apiEditUser(id, update) {
  const res = await fetch(`${API_BASE}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(update)
  });
  return res.json();
}

async function apiDeleteUser(id) {
  const res = await fetch(`${API_BASE}/${id}`, { method: 'DELETE' });
  return res.json();
}

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [showAddAdmin, setShowAddAdmin] = useState(false);
  const [modalType, setModalType] = useState(null); // 'doctor' | 'admin' | 'edit'
  const [modalUser, setModalUser] = useState({ name: '', email: '', online: false, role: 'doctor' });
  const [editId, setEditId] = useState(null);
  const [sortKey, setSortKey] = useState('name');
  const [sortDir, setSortDir] = useState('asc');
  const [search, setSearch] = useState('');

  useEffect(() => {
    setLoading(true);
    fetchAllUsers()
      .then(data => setUsers(data))
      .finally(() => setLoading(false));
  }, []);

  const handleRemove = async (id) => {
    if (window.confirm('Are you sure you want to remove this user?')) {
      await apiDeleteUser(id);
      setUsers(users.filter(u => u.id !== id));
    }
  };


  const openAddModal = (role) => {
    setModalType(role);
    setModalUser({ name: '', email: '', online: false, role });
    setEditId(null);
    if (role === 'doctor') setShowAdd(true);
    if (role === 'admin') setShowAddAdmin(true);
  };

  const openEditModal = (user) => {
    setModalType('edit');
    setModalUser({ ...user });
    setEditId(user.id);
    setShowAdd(true);
  };

  const closeModal = () => {
    setShowAdd(false);
    setShowAddAdmin(false);
    setModalType(null);
    setModalUser({ name: '', email: '', online: false, role: 'doctor' });
    setEditId(null);
  };

  const handleModalSubmit = async () => {
    if (!modalUser.name.trim() || !modalUser.email.trim()) return;
    if (modalType === 'edit' && editId != null) {
      await apiEditUser(editId, modalUser);
      setUsers(users.map(u => u.id === editId ? { ...modalUser, id: editId } : u));
    } else {
      const res = await apiAddUser(modalUser);
      setUsers([
        ...users,
        { ...modalUser, id: res.inserted_id }
      ]);
    }
    closeModal();
  };

  const sortFn = (a, b) => {
    const getVal = (u, key) => {
      if (key === 'online') return u.status ? 1 : 0;
      return (u[key] || '').toLowerCase();
    };
    let v1 = getVal(a, sortKey), v2 = getVal(b, sortKey);
    if (v1 < v2) return sortDir === 'asc' ? -1 : 1;
    if (v1 > v2) return sortDir === 'asc' ? 1 : -1;
    return 0;
  };
  const filterFn = u => {
    const s = search.toLowerCase();
    return (
      u.name.toLowerCase().includes(s) ||
      u.email.toLowerCase().includes(s) ||
      (u.role && u.role.toLowerCase().includes(s))
    );
  };
  const admins = users.filter(u => (u.role === 'admin' || u.type === 'admin') && filterFn(u)).sort(sortFn);
  const doctors = users.filter(u => (u.role === 'doctor' || u.type === 'doctor') && filterFn(u)).sort(sortFn);

  return (
    <div className="user-management">
      <h2>User Management</h2>
      <div className="user-management-controls">
        <input
          type="text"
          placeholder="Search by name, email, or role..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="search-input"
        />
        <span className="sort-controls">
          <select value={sortKey} onChange={e => setSortKey(e.target.value)} className="sort-select">
            <option value="name">Sort by Name</option>
            <option value="email">Sort by Email</option>
            <option value="online">Sort by Status</option>
          </select>
          <button className="sort-dir-btn" onClick={() => setSortDir(d => d === 'asc' ? 'desc' : 'asc')}>
            {sortDir === 'asc' ? '▲' : '▼'}
          </button>
        </span>
      </div>
      {loading ? <div>Loading users...</div> : (
        <>
          <UserTable
            title="Admins"
            users={admins}
            onEdit={openEditModal}
            onRemove={() => {}}
            onAdd={() => openAddModal('admin')}
            sortKey={sortKey}
            sortDir={sortDir}
            setSortKey={setSortKey}
            isAdminTable={true}
          />
          <UserTable
            title="Doctors"
            users={doctors}
            onEdit={openEditModal}
            onRemove={handleRemove}
            onAdd={() => openAddModal('doctor')}
            sortKey={sortKey}
            sortDir={sortDir}
            setSortKey={setSortKey}
            isAdminTable={false}
          />
          <UserModal
            show={showAdd || showAddAdmin}
            modalType={modalType}
            modalUser={modalUser}
            onChange={setModalUser}
            onSubmit={handleModalSubmit}
            onClose={closeModal}
          />
        </>
      )}
    </div>
  );
}
