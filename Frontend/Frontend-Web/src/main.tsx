import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './my-login-app/src/App'
import './my-login-app/src/styles/App.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
