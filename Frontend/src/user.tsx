import { createContext, useContext, useEffect, useState } from "react";
import { Outlet } from "react-router";

const TOKEN_STORAGE_KEY = "stylr-access-token";

interface UserContext {
  token: string | null;
  setToken(token: string | null): void;
}

interface Preferences {
  gender: number;
  tags: Record<string, number>;
}

interface PreferenceContext extends Preferences {
  update(prefs: Preferences): void;
}

const UserContext = createContext<UserContext>(null!);
const RoleContext = createContext<number>(null!);
const PreferenceContext = createContext<PreferenceContext | null>(null!);

export const useUser = () => useContext(UserContext);
export const useRole = () => useContext(RoleContext);
export const usePreferences = () => useContext(PreferenceContext);

export function UserProvider() {
  const [token, setToken] = useState(sessionStorage.getItem(TOKEN_STORAGE_KEY));
  const [role, setRole] = useState(1);
  const [preferences, setPreferences] = useState<PreferenceContext | null>(null);

  useEffect(() => {
    if (token === null) {
      sessionStorage.removeItem(TOKEN_STORAGE_KEY);
      return;
    }

    sessionStorage.setItem(TOKEN_STORAGE_KEY, token);

    function update(prefs: Preferences) {
      setPreferences({ ...prefs, update });
      fetch(`${__api}/preferences?access_token=${token}`, {
        method: "POST",
        body: JSON.stringify(prefs)
      });
    }

    let cancelled = false;
    (async () => {
      let res: Response;
      try { res = await fetch(`${__api}/user?access_token=${token}`); }
      catch (e) { return; }
      if (cancelled) {
        return;
      }
      if (res.status === 401) {
        return void setToken(null);
      }
      if (res.status !== 200) {
        return;
      }
      const { role, gender, tags } = await res.json();
      setRole(role);
      setPreferences({ gender, tags, update });
    })();
    return () => { cancelled = true; };
  }, [token]);

  return (
    <UserContext value={{ token, setToken }}>
      <RoleContext value={role}>
        <PreferenceContext value={preferences}>
          <Outlet />
        </PreferenceContext>
      </RoleContext>
    </UserContext>
  );
}
