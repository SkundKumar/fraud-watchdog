import React, { useState } from 'react';

const BACKEND_URL = "http://localhost:5000";

const App = () => {
  const [logs, setLogs] = useState([]);
  const [isPushing, setIsPushing] = useState(false);

  const triggerAttack = async () => {
    // Randomizing values to occasionally trigger different AI statuses
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
      alert("Backend error! Ensure 'python app.py' is running.");
    }
  };

  const handleMLOps = async () => {
    setIsPushing(true);
    try {
      await fetch(`${BACKEND_URL}/trigger-mlops`, { method: 'POST' });
      alert("SUCCESS: MLOps Cycle Started. Watch the terminal for Git logs!");
    } finally { setIsPushing(false); }
  };

  return (
    <div style={styles.body}>
      <h1 style={{color: '#00ff88'}}>🛡️ FRAUD WATCHDOG: LIVE MLOPS TERMINAL</h1>
      <p style={{color: '#888'}}>B.Tech CSE Project | Local-to-Cloud Adaptation Loop</p>
      
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
              <button onClick={handleMLOps} disabled={isPushing} style={styles.adaptBtn}>
                {isPushing ? "SYNCING TO CLOUD..." : "✅ APPROVE & TRIGGER ADAPTATION"}
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