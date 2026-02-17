import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ShieldAlert, ShieldCheck, Activity, Database, RefreshCw, Layers } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [status, setStatus] = useState("Connecting...");
  const [feed, setFeed] = useState([]);
  const [stats, setStats] = useState({ total: 0, fraud: 0, uncertain: 0 });
  const [isRetraining, setIsRetraining] = useState(false);

  // Poll Backend for Live Feed every 1 second
  useEffect(() => {
    const fetchData = async () => {
      try {
        await axios.get(API_BASE + "/");
        setStatus("Online");

        const res = await axios.get(API_BASE + "/live-feed");
        
        // Calculate stats based on full history received
        const total = res.data.length;
        const fraud = res.data.filter(tx => tx.prediction === "FRAUD").length;
        const uncertain = res.data.filter(tx => tx.mlops_status === "UNCERTAIN_GREY_ZONE").length;
        
        setStats({ total, fraud, uncertain });
        setFeed([...res.data].reverse()); // Newest at top
      } catch (err) {
        setStatus("Offline");
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleRetrain = async () => {
    setIsRetraining(true);
    try {
      await axios.post(API_BASE + "/retrain");
      alert("Nuclear Retraining Started! Check your terminal.");
    } catch (err) {
      alert("Failed to start retraining.");
    }
    setTimeout(() => setIsRetraining(false), 3000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      {/* Header */}
      <div className="max-w-6xl mx-auto flex justify-between items-center mb-10">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            FRAUD WATCHDOG
          </h1>
          <p className="text-slate-400 text-sm">Real-time MLOps Monitoring Dashboard</p>
        </div>
        <div className={`flex items-center gap-2 px-4 py-2 rounded-full border ${status === "Online" ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-400" : "border-red-500/50 bg-red-500/10 text-red-400"}`}>
          <div className={`w-2 h-2 rounded-full ${status === "Online" ? "bg-emerald-400 animate-pulse" : "bg-red-400"}`} />
          {status}
        </div>
      </div>

      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Sidebar Stats */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
            <h3 className="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-4 flex items-center gap-2">
              <Activity size={14} /> System Analytics
            </h3>
            <div className="space-y-4">
              <div>
                <p className="text-4xl font-bold">{stats.total}</p>
                <p className="text-slate-500 text-xs">Total Swipes Scanned</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-red-500/5 border border-red-500/20 rounded-xl">
                  <p className="text-xl font-bold text-red-400">{stats.fraud}</p>
                  <p className="text-slate-500 text-[10px]">Fraud Blocked</p>
                </div>
                <div className="p-3 bg-yellow-500/5 border border-yellow-500/20 rounded-xl">
                  <p className="text-xl font-bold text-yellow-400">{stats.uncertain}</p>
                  <p className="text-slate-500 text-[10px]">Uncertain (Drift)</p>
                </div>
              </div>
            </div>
          </div>

          <button 
            onClick={handleRetrain}
            disabled={isRetraining}
            className={`w-full py-4 rounded-2xl font-bold flex items-center justify-center gap-2 transition-all shadow-lg ${isRetraining ? "bg-slate-700 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-500 active:scale-95"}`}
          >
            <RefreshCw size={18} className={isRetraining ? "animate-spin" : ""} /> 
            {isRetraining ? "Retraining..." : "Trigger Nuclear Retrain"}
          </button>
          
          
        </div>

        {/* Main Feed */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-[600px]">
          <div className="p-4 border-b border-slate-800 bg-slate-900/50 flex justify-between items-center">
            <h3 className="text-sm font-semibold flex items-center gap-2">
               <Database size={16} className="text-blue-400" /> Live Monitoring
            </h3>
            <span className="text-[10px] text-slate-500 animate-pulse font-mono tracking-widest">LIVE_POLL_READY</span>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
            {feed.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-slate-600 italic">
                <Activity size={48} className="mb-4 opacity-10 animate-pulse" />
                Waiting for simulation traffic...
              </div>
            )}
            <AnimatePresence>
              {feed.map((tx) => (
                <motion.div
                  key={tx.id}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`p-4 rounded-xl border flex items-center justify-between transition-colors ${
                    tx.prediction === "FRAUD" 
                    ? "bg-red-500/10 border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.1)]" 
                    : tx.mlops_status === "UNCERTAIN_GREY_ZONE"
                    ? "bg-yellow-500/10 border-yellow-500/30"
                    : "bg-slate-800/40 border-slate-700/50"
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-full ${tx.prediction === "FRAUD" ? "bg-red-500/20 text-red-500" : "bg-emerald-500/20 text-emerald-500"}`}>
                       {tx.prediction === "FRAUD" ? <ShieldAlert size={20} /> : <ShieldCheck size={20} />}
                    </div>
                    <div>
                      <p className={`font-bold text-sm leading-none mb-1 ${tx.prediction === "FRAUD" ? "text-red-400" : "text-emerald-400"}`}>
                        {tx.prediction}
                      </p>
                      <p className="text-[10px] text-slate-500 font-mono uppercase">
                        Conf: {(tx.confidence_score * 100).toFixed(1)}% | Amt: ${tx.amount.toFixed(2)}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-[10px] font-mono text-slate-500 mb-1">{tx.timestamp} | ID_{tx.id}</p>
                    <span className={`text-[9px] px-2 py-0.5 rounded font-bold ${tx.mlops_status === "UNCERTAIN_GREY_ZONE" ? "bg-yellow-500/20 text-yellow-500" : "bg-slate-700 text-slate-400"}`}>
                      {tx.mlops_status}
                    </span>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;