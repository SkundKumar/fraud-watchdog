    import React, { useState, useEffect } from 'react';

const WatchdogDashboard = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  // PASTE YOUR LAMBDA URL HERE
  const LAMBDA_URL = "https://9qxzhxb7g6.execute-api.us-east-1.amazonaws.com/default/Watchdog_Inference_Engine";

  const triggerAttack = async () => {
    setLoading(true);
    // This payload simulates a "New Type of Attack" with weird values
    const attackData = {
      V1: (Math.random() * 5).toFixed(2), 
      V2: (Math.random() * -5).toFixed(2),
      Amount: Math.floor(Math.random() * 5000) + 1000, // High amounts trigger uncertainty
      Time: Date.now()
    };

    try {
      const response = await fetch(LAMBDA_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(attackData)
      });
      const result = await response.json();
      
      // Add the new result to the top of our log list
      setLogs(prev => [result, ...prev]);
    } catch (err) {
      console.error("Cloud Connection Failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '40px', backgroundColor: '#0f172a', color: '#f8fafc', minHeight: '100vh', fontFamily: 'sans-serif' }}>
      <header style={{ borderBottom: '2px solid #334155', marginBottom: '30px' }}>
        <h1 style={{ color: '#38bdf8' }}>🛡️ FRAUD WATCHDOG: CLOUD MLOPS TERMINAL</h1>
        <p style={{ color: '#94a3b8' }}>Connected to AWS Lambda & DynamoDB</p>
      </header>

      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={triggerAttack}
          disabled={loading}
          style={{
            backgroundColor: '#ef4444',
            color: 'white',
            padding: '12px 24px',
            border: 'none',
            borderRadius: '4px',
            fontSize: '16px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          {loading ? "COMMUNICATING WITH CLOUD..." : "🚨 SIMULATE NEW ATTACK PATTERN"}
        </button>
      </div>

      <div style={{ display: 'grid', gap: '15px' }}>
        {logs.map((log) => (
          <div key={log.id} style={{
            padding: '20px',
            borderRadius: '8px',
            backgroundColor: '#1e293b',
            borderLeft: `8px solid ${log.status === 'FRAUD' ? '#ef4444' : log.status === 'REQUIRES_HUMAN_REVIEW' ? '#eab308' : '#22c55e'}`
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <strong>ID: {log.id}</strong>
              <span style={{ 
                fontWeight: 'bold', 
                color: log.status === 'FRAUD' ? '#ef4444' : log.status === 'REQUIRES_HUMAN_REVIEW' ? '#eab308' : '#22c55e' 
              }}>
                {log.status}
              </span>
            </div>
            <p style={{ margin: '10px 0 0 0', fontSize: '14px', color: '#94a3b8' }}>
              AI Probability Score: {log.probability} | Amount: ${log.amount}
            </p>
            {log.status === 'REQUIRES_HUMAN_REVIEW' && (
              <button 
                onClick={() => alert("Moving data to training set... GitHub Action will trigger next!")}
                style={{ marginTop: '10px', background: '#eab308', color: 'black', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer' }}
              >
                ✅ Confirm as Fraud
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default WatchdogDashboard;