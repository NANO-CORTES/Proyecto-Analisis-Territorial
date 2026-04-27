import React from 'react';
import RegisterForm from '../components/RegisterForm';
import '../styles/LoginForm.css';

const RegisterPage: React.FC = () => {
  return (
    <div className="login-page">
      <div className="login-bg">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
      </div>
      <div className="login-container">
        <RegisterForm />
      </div>
    </div>
  );
};

export default RegisterPage;
