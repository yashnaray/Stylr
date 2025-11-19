import { useEffect, useState } from "react";
import { usePreferences } from "../user";

function Gender() {
  const { gender, tags, update: updatePreferences } = usePreferences()!;
  return <>
    <h2 className="text-xl font-bold my-4">Gender</h2>
    <ol>
      {["Unisex", "Female", "Male"].map((name, i) => (
      <li key={i} className="my-1">
        {gender === i
          ? <button className="border-1 border-green-500 px-1 bg-green-100">{name}</button>
          : <button className="border-1 border-gray-300 px-1" onClick={() => updatePreferences({ gender: i, tags })}>{name}</button>
        }
      </li>
      ))}
    </ol>
  </>;
}

interface PreferenceProps {
  name: string;
}

function Preference({ name }: PreferenceProps) {
  const { gender, tags, update: updatePreferences } = usePreferences()!;
  const value = tags[name];

  function toggle() {
    updatePreferences({ gender, tags: { ...tags, [name]: Number(!value) } });
  }

  return (
    <li className="my-1 ml-2"> {value ?
      <button className="border-1 border-green-500 px-1 bg-green-100" onClick={toggle}>{name}</button>
      :
      <button className="border-1 border-gray-300 px-1" onClick={toggle}>{name}</button>
    } </li>
  );
}

type SectionSchema = [string, (string | SectionSchema)[]];

interface SectionProps {
  schema: SectionSchema;
}

function Section({ schema: [name, items] }: SectionProps) {
  const [open, setOpen] = useState(false);

  function toggle() {
    setOpen(!open);
  };

  return (
    <li className="my-1">
      <button onClick={toggle}>
        <span className="inline-block text-gray-600 w-4">{open ? "-" : "+"}</span>
        <strong className="font-bold ml-2">{name}</strong>
      </button>
      <ol className="border-l-1 border-gray-300 ml-2 pl-2" style={{ display: open ? "block" : "none" }}>
        {items.map(item => typeof item === "string"
          ? <Preference key={item} name={item} />
          : <Section key={item[0]} schema={item} />
        )}
      </ol>
    </li>
  );
}

function Preferences({ schema }: { schema: SectionSchema[]; }) {
  return <>
    <h2 className="text-xl font-bold my-4">Preferences</h2>
    <ol>{schema.map(section => <Section key={section[0]} schema={section} />)}</ol>
  </>;
}

export default function SettingsPage() {
  const preferences = usePreferences();
  const [schema, setSchema] = useState<SectionSchema[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (schema || error) {
      return;
    }
    let cancelled = false;
    (async () => {
      const res = await fetch(`${__api}/schema`);
      if (cancelled) {
        return;
      }
      if (res.status !== 200) {
        return void setError((await res.json()).message);
      }
      setSchema(await res.json());
    })();
    return () => { cancelled = true; };
  }, [schema, error]);

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

  if (!preferences || !schema) {
    return (
      <p className="p-12 text-center text-gray-600">Loading...</p>
    );
  }

  return (
    <main className="w-full max-w-200 mx-auto p-8 bg-white">
      <h1 className="font-bold text-2xl">Settings</h1>
      <Gender />
      <Preferences schema={schema} />
    </main>
  );
}
