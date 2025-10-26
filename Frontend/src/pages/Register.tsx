import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { useUser } from "../user";

function InputField(props: React.JSX.IntrinsicElements['input']) {
  return <input className="block w-full border-1 border-gray-400 hover:border-gray-500 my-2 p-1" {...props} />
}

export default function Register() {
  const { setToken } = useUser();
  const navigate = useNavigate();
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function submit(ev: React.FormEvent<HTMLFormElement>): Promise<void> {
    ev.preventDefault();
    const data = new FormData(ev.currentTarget);
    const username = data.get('username');
    const password = data.get('password');
    const password2 = data.get('password2');
    if (!username || !password) {
      return void setMessage('All fields are required.');
    }
    if (password !== password2) {
      return void setMessage('Those passwords don\'t match.');
    }
    setPending(true);
    try {
      const response = await fetch(`${__api}/register`, {
        method: 'POST',
        body: JSON.stringify({ username, password })
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
      navigate('/');
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="mx-auto max-w-96 text-center bg-white p-4">
      <h1 className="text-3xl font-bold my-4">Create an account</h1>
      <p>Or <Link to="/login" className="underline text-blue-500">return to login</Link>.</p>
      <form onSubmit={submit}>
        {message !== null && <p className="bg-red-200 border-1 border-red-500 my-2 p-2">{message}</p>}
        <InputField name="username" placeholder="Username" autoComplete="username" disabled={pending} />
        <InputField name="password" placeholder="Password" type="password" autoComplete="new-password" disabled={pending} />
        <InputField name="password2" placeholder="Retype password" type="password" autoComplete="new-password" disabled={pending} />
        <button type="submit" disabled={pending} className="border-1 border-gray-400 bg-gray-100 hover:border-blue-500 px-4 py-2 cursor-pointer">
          {pending ? 'Please wait...' : 'Register'}
        </button>
      </form>
    </div>
  );
}
