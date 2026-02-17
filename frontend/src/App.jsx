import React, { useState } from 'react';

const BACKEND_URL = "http://localhost:5000";

const App = () => {
  const [logs, setLogs] = useState([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const [stats, setStats] = useState({ version: 1.0, maturity: 45, threats_caught: 0 });

  // 1. NORMAL RANDOM ATTACK (Baseline)
  const triggerAttack = async () => {
    const attackData = { 
      V1: (Math.random() * 10 - 5).toFixed(2), 
      V2: (Math.random() * 10 - 5).toFixed(2), 
      Amount: (Math.random() * 5000).toFixed(2), 
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
      if (result.stats) setStats(result.stats);
    } catch (err) { alert("Backend offline!"); }
  };

  // 2. PATTERN THREAT: VELOCITY ATTACK (Rapid-fire fixed amounts)
  const simulateVelocityAttack = async () => {
    console.log("🔥 Triggering Velocity Pattern...");
    for (let i = 0; i < 5; i++) {
      const attackData = { V1: 7.21, V2: -8.45, Amount: "10.00", Time: Date.now() };
      const res = await fetch(`${BACKEND_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(attackData)
      });
      const result = await res.json();
      setLogs(prev => [result, ...prev]);
      if (result.stats) setStats(result.stats);
    }
  };

  const handleMLOps = async () => {
    setIsSyncing(true);
    try {
      const res = await fetch(`${BACKEND_URL}/trigger-mlops`, { method: 'POST' });
      const data = await res.json();
      if (data.stats) setStats(data.stats);
    } finally { setIsSyncing(false); }
  };

  return (
    <div style={styles.body}>
      {/* VISUAL INTELLIGENCE HEADER */}
      <div style={styles.statsBar}>
        <div style={{fontWeight: 'bold'}}>🤖 AI MODEL: v{stats.version}</div>
        <div style={{flex: 1, margin: '0 30px'}}>
           LEARNING PROGRESS: 
           <div style={styles.progressBg}>
              <div style={{...styles.progressFill, width: `${stats.maturity}%`}} />
           </div>
        </div>
        <div style={{color: '#ff4d4d', fontWeight: 'bold'}}>🎯 THREATS CAUGHT: {stats.threats_caught}</div>
      </div>

      <h1 style={{color: '#00ff88'}}>🛡️ WATCHDOG: LIVE MLOPS TERMINAL</h1>
      
      <div style={{display: 'flex', gap: '10px', marginBottom: '20px'}}>
        <button onClick={triggerAttack} style={styles.btn}>🎲 RANDOM ATTACK</button>
        <button onClick={simulateVelocityAttack} style={{...styles.btn, background: '#ffcc00', color: '#000'}}>🔥 VELOCITY THREAT ($10 x 5)</button>
      </div>

      <div style={{display: 'flex', flexDirection: 'column', gap: '10px'}}>
        {logs.map((log, i) => (
          <div key={i} style={{...styles.card, borderLeftColor: log.status === 'FRAUD' ? '#ff4d4d' : log.status === 'REQUIRES_HUMAN_REVIEW' ? '#ffcc00' : '#00ff88'}}>
            <p><strong>{log.status}</strong> | {log.id} | Amount: ${log.amount}</p>
            <p>AI Confidence: {log.probability} {log.amount === "10.00" ? "(PATTERN DETECTED)" : ""}</p>
            {log.status === 'REQUIRES_HUMAN_REVIEW' && (
              <button onClick={handleMLOps} disabled={isSyncing} style={styles.adaptBtn}>
                {isSyncing ? "SAVING THREAT PATTERN..." : "✅ APPROVE & RETRAIN AI"}
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
  statsBar: { display: 'flex', background: '#111', padding: '20px', borderRadius: '8px', marginBottom: '30px', border: '1px solid #00ff88', alignItems: 'center' },
  progressBg: { background: '#333', height: '12px', borderRadius: '6px', marginTop: '8px', overflow: 'hidden' },
  progressFill: { background: '#00ff88', height: '100%', transition: '0.8s' },
  btn: { padding: '15px 30px', background: '#ff4d4d', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: 'bold' },
  card: { background: '#111', padding: '15px', borderLeft: '8px solid', borderRadius: '4px' },
  adaptBtn: { marginTop: '10px', padding: '8px', background: '#ffcc00', border: 'none', cursor: 'pointer', fontWeight: 'bold', color: '#000' }
};

export default App;