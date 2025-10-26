import { createRoot } from "react-dom/client";
import { BrowserRouter, Link, Navigate, Outlet, Routes, Route, useLocation } from "react-router";
import { useUser, UserProvider } from "./user.tsx";
import App from "./pages/App.tsx";
import Login from "./pages/Login.tsx";
import Register from "./pages/Register.tsx";
import Swipe from "./pages/Swipe.tsx";
import "./main.css";

declare global {
  const __api: string;
}

function Protected() {
  const location = useLocation();
  const { token } = useUser();
  if (!token) {
    const referer = location.pathname + location.search + location.hash;
    return <Navigate to="/login" replace state={{ referer }} />;
  }
  return <Outlet />;
}

function Entry() {
  const { token } = useUser();
  if (token) {
    return <Navigate to="/" replace />;
  }
  return <Outlet />;
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

const root = document.getElementById("root")!;

createRoot(root).render(
  <BrowserRouter>
    <Routes>
      <Route Component={UserProvider}>
        <Route Component={Protected}>
          <Route path="/" Component={App} />
          <Route path="/swipe" Component={Swipe} />
        </Route>
        <Route Component={Entry}>
          <Route path="/login" Component={Login} />
          <Route path="/register" Component={Register} />
        </Route>
        <Route path="*" Component={NotFound} />
      </Route>
    </Routes>
  </BrowserRouter>
);
