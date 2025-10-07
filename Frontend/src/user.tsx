import { createContext, useState, type PropsWithChildren } from 'react';

const TOKEN_STORAGE_KEY = 'stylr-access-token';

export const UserContext = createContext<{
  token: string | null,
  setToken: (token: string | null) => void
}>(null!);

export function UserProvider({ children }: PropsWithChildren) {
  const [token, rawSetToken] = useState(sessionStorage.getItem(TOKEN_STORAGE_KEY));
  function setToken(newToken: string | null) {
    if (newToken !== null)
      sessionStorage.setItem(TOKEN_STORAGE_KEY, newToken);
    else
      sessionStorage.removeItem(TOKEN_STORAGE_KEY);
    rawSetToken(newToken);
  }
  return (
    <UserContext value={{ token, setToken }}>
      {children}
    </UserContext>
  );
}
