import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import { useUser } from '../components/UserContext';
import { useHistory } from '@docusaurus/router';

function SignupPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [softwareBackground, setSoftwareBackground] = useState('');
  const [hardwareBackground, setHardwareBackground] = useState('');
  const { signup, isLoggedIn } = useUser();
  const history = useHistory();

  useEffect(() => {
    if (isLoggedIn) {
      history.push('/');
    }
  }, [isLoggedIn, history]);

  const handleSignup = (e) => {
    e.preventDefault();
    const userData = {
      username,
      password, // In a real app, hash this!
      softwareBackground,
      hardwareBackground,
    };
    if (signup(userData)) {
      alert('Signed up and logged in successfully!');
    } else {
      alert('Signup failed. Please try again.');
    }
  };

  return (
    <Layout title="Signup" description="Signup page for the unified book project">
      <main style={{ padding: '2rem' }}>
        <div style={{ maxWidth: '400px', margin: '0 auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h1>Sign Up</h1>
          <form onSubmit={handleSignup}>
            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="username" style={{ display: 'block', marginBottom: '0.5rem' }}>Username:</label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                required
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
                required
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="softwareBackground" style={{ display: 'block', marginBottom: '0.5rem' }}>Software Background:</label>
              <textarea
                id="softwareBackground"
                value={softwareBackground}
                onChange={(e) => setSoftwareBackground(e.target.value)}
                style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                rows="3"
                placeholder="e.g., Python, React, cloud services..."
              ></textarea>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="hardwareBackground" style={{ display: 'block', marginBottom: '0.5rem' }}>Hardware Background:</label>
              <textarea
                id="hardwareBackground"
                value={hardwareBackground}
                onChange={(e) => setHardwareBackground(e.target.value)}
                style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                rows="3"
                placeholder="e.g., Embedded systems, IoT, specific hardware architectures..."
              ></textarea>
            </div>
            <button type="submit" style={{ width: '100%', padding: '10px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Sign Up</button>
          </form>
          <p style={{ marginTop: '1rem', textAlign: 'center' }}>
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </div>
      </main>
    </Layout>
  );
}

export default SignupPage;
