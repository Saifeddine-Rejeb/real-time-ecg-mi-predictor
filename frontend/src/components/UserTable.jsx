import React from 'react';

export default function UserTable({ title, users, onEdit, onRemove, onAdd, setSortKey, isAdminTable }) {
  return (
    <div className="user-table-section">
      <div className="user-table-header">
        <h3>{title}</h3>
        <button className="edit-btn" onClick={onAdd}>{isAdminTable ? 'Add Admin' : 'Add Doctor'}</button>
      </div>
      <table className="user-table">
        <thead>
          <tr>
            <th onClick={() => setSortKey('name')}>Name</th>
            <th onClick={() => setSortKey('email')}>Email</th>
            <th onClick={() => setSortKey('online')}>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id} className={user.online ? 'online' : 'offline'}>
              <td>{user.name}</td>
              <td>{user.email}</td>
              <td>
                <span className={user.online ? 'status-dot online' : 'status-dot offline'}></span>
                {user.online ? 'Online' : 'Offline'}
              </td>
              <td>
                <button className="edit-btn" onClick={() => onEdit(user)}>Edit</button>
                {!isAdminTable && (
                  <button className="remove-btn" onClick={() => onRemove(user.id)}>Remove</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
