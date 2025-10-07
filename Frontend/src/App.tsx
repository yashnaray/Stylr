import { useContext } from 'react';
import { UserContext } from './user';

export default function App() {
  const { setToken } = useContext(UserContext);
  return (
    <>
      <div className="text-center">
        <button onClick={() => setToken(null)} className="px-4 py-2 bg-white border-1 border-gray-400 hover:border-blue-400 cursor-pointer">Logout</button>
      </div>
    </>
  );
}
