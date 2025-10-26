import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router';
import { useUser } from "../user";

function InputField(props: React.JSX.IntrinsicElements['input']) {
  return <input className="block w-full border-1 border-gray-400 hover:border-black my-2 p-1" {...props} />
}

export default function Login() {
  const { setToken } = useUser();
  const location = useLocation();
  const navigate = useNavigate();
  const [pending, setPending] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function doSubmit(data: unknown) {
    const response = await fetch(`${__api}/login`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
    if (response.status === 401) {
      const { message } = await response.json();
      return void setMessage(message);
    }
    if (response.status !== 200) {
      return void setMessage(`Error: ${response.status} ${response.statusText}`);
    }
    const { access_token } = await response.json();
    setToken(access_token);
    if (location.state) {
      navigate(location.state.referer);
    } else {
      navigate("/");
    }
  }

  async function submit(ev: React.FormEvent<HTMLFormElement>): Promise<void> {
    ev.preventDefault();
    const data = new FormData(ev.currentTarget);
    const username = data.get('username');
    const password = data.get('password');
    if (!username || !password) {
      return void setMessage('All fields are required.');
    }
    setPending(true);
    try {
      await doSubmit({ username, password });
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="mx-auto max-w-96 text-center bg-white p-4">
      <h1 className="text-3xl font-bold my-4">Stylr</h1>
      <p>No account? <Link to="/register" className="underline text-blue-500">Register</Link></p>
      <form onSubmit={submit}>
        {message !== null && <p className="bg-red-200 border-1 border-red-500 my-2 p-2">{message}</p>}
        <InputField name="username" placeholder="Username" autoComplete="username" />
        <InputField name="password" placeholder="Password" type="password" autoComplete="current-password" />
        <button type="submit" disabled={pending} className="border-1 border-gray-400 bg-gray-100 hover:border-blue-500 px-4 py-2 cursor-pointer disabled:text-gray-500">
          {pending ? 'Please wait...' : 'Login'}
        </button>
      </form>
    </div>
  );
}
