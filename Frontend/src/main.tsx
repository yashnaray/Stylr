import { useContext } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Link, Routes, Route, useLocation, useNavigate } from 'react-router';
import { UserContext, UserProvider } from './user.tsx';
import App from './App.tsx';
import Login from './Login.tsx';
import Register from './Register.tsx';
import './main.css';
import Swipe from './pages/Swipe.tsx';

function Root() {
  const location = useLocation();
  const navigate = useNavigate();
  const { token } = useContext(UserContext);
  if (!token) {
    const url = `/login?to=${encodeURIComponent(location.pathname + location.search + location.hash)}`;
    queueMicrotask(() => navigate(url, { replace: true }));
    return null;
  }
  return <App />;
}

function NotFound() {
  return (
    <div className="text-center">
      <h1 className="text-7xl font-bold my-4">404</h1>
      <p className="my-2">Not Found</p>
      <p><Link to="/" className="text-blue-500 underline">Home</Link></p>
    </div>
  );
}

const root = document.getElementById('root')!;

createRoot(root).render(
  <UserProvider>
    <BrowserRouter>
      <Routes>
        <Route path="/" Component={Root} />
        <Route path="/login" Component={Login} />
        <Route path="/register" Component={Register} />
        <Route path="/swipe" Component={Swipe} />       
        <Route path="*" Component={NotFound} />
      </Routes>
    </BrowserRouter>
  </UserProvider>
);
