import { createRoot } from "react-dom/client";
import { BrowserRouter, Link, Navigate, Outlet, Routes, Route, useLocation } from "react-router";
import { useUser, UserProvider } from "./user.tsx";
import Login from "./pages/Login.tsx";
import Register from "./pages/Register.tsx";
import Settings from "./pages/Settings.tsx";
import Swipe from "./pages/Swipe.tsx";
import "./main.css";

declare global {
  const __api: string;
}

function Protected() {
  const location = useLocation();
  const { token, setToken } = useUser();
  if (!token) {
    const referer = location.pathname + location.search + location.hash;
    return <Navigate to="/login" replace state={{ referer }} />;
  }
  return (
    <div className="flex flex-col min-h-screen">
      <header className="flex items-center bg-white p-4 border-gray-300 border-b-1">
        <h1 className="text-lg font-bold grow"><Link to="/">Stylr</Link></h1>
        <Link to="/settings" className="mr-4">Settings</Link>
        <button onClick={() => setToken(null)} className="cursor-pointer">Logout</button>
      </header>
      <Outlet />
    </div>
  );
}

function Public() {
  const { token } = useUser();
  if (token) {
    return <Navigate to="/" replace />;
  }
  return (
    <div className="flex flex-col min-h-screen justify-center">
      <Outlet />
    </div>
  );
}

function NotFound() {
  return (
    <div className="grow flex flex-col justify-center text-center">
      <h1 className="text-7xl font-bold mb-4">404</h1>
      <p>Not Found</p>
    </div>
  );
}

const root = document.getElementById("root")!;

createRoot(root).render(
  <BrowserRouter>
    <Routes>
      <Route Component={UserProvider}>
        <Route Component={Protected}>
          <Route path="/" Component={Swipe} />
          <Route path="/settings" Component={Settings} />
          <Route path="*" Component={NotFound} />
        </Route>
        <Route Component={Public}>
          <Route path="/login" Component={Login} />
          <Route path="/register" Component={Register} />
          <Route path="*" Component={NotFound} />
        </Route>
      </Route>
    </Routes>
  </BrowserRouter>
);
