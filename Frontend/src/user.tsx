import { createContext, useContext, useEffect, useState } from "react";
import { Outlet } from "react-router";

const TOKEN_STORAGE_KEY = "stylr-access-token";

interface UserContext {
  token: string | null;
  setToken(token: string | null): void;
}

const UserContext = createContext<UserContext>(null!);

export const useUser = () => useContext(UserContext);

export function UserProvider() {
  const [token, setToken] = useState(sessionStorage.getItem(TOKEN_STORAGE_KEY));

  useEffect(() => {
    if (token !== null)
      sessionStorage.setItem(TOKEN_STORAGE_KEY, token);
    else
      sessionStorage.removeItem(TOKEN_STORAGE_KEY);
  }, [token]);

  return (
    <UserContext value={{ token, setToken }}>
      <Outlet />
    </UserContext>
  );
}
