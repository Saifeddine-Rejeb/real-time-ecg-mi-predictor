import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from '../src/pages/Home';
import Login from '../src/pages/Login';
import Signup from '../src/pages/Signup';
import Patients from '../src/pages/Patients';
import Alerts from '../src/pages/Alerts';
import PatientDashboard from '../src/pages/PatientDashboard';
import StreamingDashboard from '../src/pages/StreamingDashboard';
import AlertDashboard from '../src/pages/AlertDashboard';
import Settings from '../src/pages/Settings';
import Reports from '../src/pages/Reports';
import ReportEditor from '../src/pages/ReportEditor';
import UserManagement from '../src/pages/UserManagement';
import RoleRoute from './RoleRoutes';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/patients" element={<Patients />} />
      <Route path="/patients/stream-test" element={<StreamingDashboard />} />
      <Route path="/patients/:patientId" element={<PatientDashboard />} />
      <Route path="/alerts" element={<Alerts />} />
      <Route path="/alerts/:alertId" element={<AlertDashboard />} />
      <Route path="/reports" element={<Reports />} />
      <Route path="/settings" element={<Settings />} />
      <Route path="/report-editor" element={<ReportEditor />} />
      <Route path="/user-management" element={
        <RoleRoute allowedRoles={['admin']}>
          <UserManagement />
        </RoleRoute>
      } />
      <Route path="/help" element={<div>Help Page</div>} />
      <Route path="/contact" element={<div>Contact Us Page</div>} />
      <Route path="/logout" element={<></>} />
    </Routes>
  );
}
