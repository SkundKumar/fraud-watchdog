import React, { useState } from 'react';

const BACKEND_URL = "http://localhost:5000";

const App = () => {
  const [logs, setLogs] = useState([]);
  const [isSyncing, setIsSyncing] = useState(false);

  const triggerAttack = async () => {
    // Randomized data to test different AI confidence levels
    const attackData = {
      V1: (Math.random() * 20 - 10).toFixed(2), 
      V2: (Math.random() * 20 - 10).toFixed(2),
      Amount: (Math.random() * 10000).toFixed(2), 
      Time: Date.now()
    };

    try {
      const res = await fetch(`${BACKEND_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(attackData)
      });
      const result = await res.json();
      setLogs(prev => [result, ...prev]);
    } catch (err) {
      alert("Backend error! Run 'python app.py' in the other terminal.");
    }
  };

  const handleMLOps = async () => {
    setIsSyncing(true);
    try {
      const res = await fetch(`${BACKEND_URL}/trigger-mlops`, { method: 'POST' });
      const data = await res.json();
      alert(`SUCCESS: ${data.message}`);
    } catch (err) {
      alert("MLOps Sync failed. Check terminal for Git conflicts.");
    } finally { setIsSyncing(false); }
  };

  return (
    <div style={styles.body}>
      <h1 style={{color: '#00ff88'}}>🛡️ FRAUD WATCHDOG: MLOPS TERMINAL</h1>
      <p style={{color: '#888'}}>B.Tech CSE Project | Adaptive AI Monitoring</p>
      
      <button onClick={triggerAttack} style={styles.btn}>🚨 LAUNCH NEW ATTACK</button>

      <div style={{marginTop: '20px'}}>
        {logs.map((log, i) => (
          <div key={i} style={{
            ...styles.card,
            borderLeftColor: log.status === 'FRAUD' ? '#ff4d4d' : log.status === 'REQUIRES_HUMAN_REVIEW' ? '#ffcc00' : '#00ff88'
          }}>
            <p><strong>{log.status}</strong> | {log.id} | Amount: ${log.amount}</p>
            <p>AI Confidence: {log.probability}</p>
            {log.status === 'REQUIRES_HUMAN_REVIEW' && (
              <button onClick={handleMLOps} disabled={isSyncing} style={styles.adaptBtn}>
                {isSyncing ? "SYNCING TO GITHUB..." : "✅ APPROVE & TRIGGER ADAPTATION"}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const styles = {
  body: { padding: '50px', background: '#050505', color: '#fff', minHeight: '100vh', fontFamily: 'monospace' },
  btn: { padding: '15px 30px', background: '#ff4d4d', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: 'bold' },
  card: { background: '#111', padding: '15px', margin: '10px 0', borderLeft: '8px solid', borderRadius: '4px' },
  adaptBtn: { marginTop: '10px', padding: '8px', background: '#ffcc00', border: 'none', cursor: 'pointer', fontWeight: 'bold' }
};

export default App;