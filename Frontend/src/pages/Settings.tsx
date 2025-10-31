import { useEffect, useState } from "react";
import { useUser } from "../user";

type CategoryPreference = [name: string, value: number];

interface Settings {
  categories: CategoryPreference[]
}

export default function SettingsPage() {
  const { token } = useUser();
  const [settings, setSettings] = useState<Settings | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (settings || error) {
      return;
    }
    let cancelled = false;
    setTimeout(async () => {
      const res = await fetch(`${__api}/settings?access_token=${token}`);
      if (cancelled) {
        return;
      }
      if (res.status !== 200) {
        return void setError((await res.json()).message);
      }
      setSettings(await res.json());
    }, 500);
    return () => { cancelled = true; };
  }, [settings, error]);

  if (error) {
    return (
      <div className="m-8 p-4 text-center bg-red-100 border-1 border-red-400 text-red-600 space-y-4">
        <p>Failed to load settings: {error}</p>
        <p>
          <button className="border-1 border-red-400 px-4 py-1 cursor-pointer"
            onClick={() => setError(null)}>Retry</button>
        </p>
      </div>
    );
  }

  if (!settings) {
    return (
      <p className="p-12 text-center text-gray-600">Loading...</p>
    );
  }

  const { categories } = settings;
  return (
    <main className="w-full max-w-200 mx-auto p-8 bg-white">
      <h1 className="text-xl font-bold">Settings</h1>
      <h2 className="text-lg font-bold">Categories</h2>
      <ol className="flex flex-wrap gap-1">
        {settings.categories.map(([name, value], i) => {
          function click() {
            categories[i][1] = Number(!value);
            setSettings({ categories });
          }
          return <li key={name}>
            {value ?
              <button className="border-1 border-green-500 px-1 bg-green-100" onClick={click}>{name}</button>
              :
              <button className="border-1 border-gray-300 px-1" onClick={click}>{name}</button>
            }
          </li>;
        })}
      </ol>
    </main>
  );
}
