import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import { useUser } from '../components/UserContext';
import { useHistory } from '@docusaurus/router';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoggedIn } = useUser();
  const history = useHistory();

  useEffect(() => {
    if (isLoggedIn) {
      history.push('/');
    }
  }, [isLoggedIn, history]);

  const handleLogin = (e) => {
    e.preventDefault();
    if (login(username, password)) {
      alert('Logged in successfully!');
    } else {
      alert('Invalid credentials');
    }
  };

  return (
    <Layout title="Login" description="Login page for the unified book project">
      <main style={{ padding: '2rem' }}>
        <div style={{ maxWidth: '400px', margin: '0 auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h1>Login</h1>
          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="username" style={{ display: 'block', marginBottom: '0.5rem' }}>Username:</label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="password" style={{ display: 'block', marginBottom: '0.5rem' }}>Password:</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>
            <button type="submit" style={{ width: '100%', padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Login</button>
          </form>
          <p style={{ marginTop: '1rem', textAlign: 'center' }}>
            Don't have an account? <Link to="/signup">Sign up</Link>
          </p>
        </div>
      </main>
    </Layout>
  );
}

export default LoginPage;