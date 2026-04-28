import React from 'react';
import LoginForm from '../components/LoginForm';
import '../styles/LoginForm.css';

const LoginPage: React.FC = () => {
  return (
    <div className="login-page">
      <div className="login-bg">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
      </div>
      <div className="login-container">
        <LoginForm />
      </div>
    </div>
  );
};

export default LoginPage;