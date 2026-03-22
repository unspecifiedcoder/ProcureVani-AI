"use client";
import { useState } from "react";

const FLAGS = [
  { id: 1, passport_id: "PV-C5D4E3F7", company: "AutoParts Co", flag_type: "MARGINAL_COMPLIANCE", confidence: 0.6, detail: "LCV 45.0% below 50% threshold for motor parts.", flagged_at: "2026-02-26 16:42:00", resolved: false },
  { id: 2, passport_id: "PV-H1I2J3K4", company: "QuickBuild Infra", flag_type: "MISSING_GSTIN", confidence: 0.4, detail: "GSTIN not provided.", flagged_at: "2026-02-20 09:15:00", resolved: false },
  { id: 3, passport_id: "PV-L5M6N7O8", company: "PureLocal Ltd", flag_type: "PERFECT_LCV", confidence: 0.5, detail: "100% local content unusual.", flagged_at: "2026-02-18 14:20:00", resolved: false },
];

export default function FraudPage() {
  const [flags, setFlags] = useState(FLAGS);
  const [showResolved, setShowResolved] = useState(false);

  const displayed = flags.filter(f => showResolved || !f.resolved);

  const resolve = (id: number) => setFlags(prev => prev.map(f => f.id === id ? { ...f, resolved: true } : f));

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: 700 }}>Fraud Flags</h2>
        <label style={{ fontSize: "0.8125rem", color: "#6e6e73", display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer" }}>
          <input type="checkbox" checked={showResolved} onChange={e => setShowResolved(e.target.checked)} />
          Show resolved
        </label>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {displayed.map(f => (
          <div key={f.id} style={{ background: "#fff", borderRadius: "10px", border: `1px solid ${f.resolved ? "#d2d2d7" : "#ffccca"}`, padding: "1.25rem", opacity: f.resolved ? 0.6 : 1 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
                  <span style={{ fontSize: "0.6875rem", fontWeight: 600, padding: "2px 8px", borderRadius: "4px", background: "#ffeeed", color: "#cc1a0f", textTransform: "uppercase" }}>{f.flag_type.replace(/_/g, " ")}</span>
                  <span style={{ fontSize: "0.75rem", color: "#6e6e73" }}>Confidence: {(f.confidence * 100).toFixed(0)}%</span>
                </div>
                <p style={{ fontSize: "0.875rem", fontWeight: 500, marginBottom: "0.25rem" }}>{f.company} -- <a href={`/verify?id=${f.passport_id}`} className="mono">{f.passport_id}</a></p>
                <p style={{ fontSize: "0.8125rem", color: "#6e6e73" }}>{f.detail}</p>
                <p style={{ fontSize: "0.75rem", color: "#86868b", marginTop: "0.5rem" }}>Flagged: {f.flagged_at}</p>
              </div>
              {!f.resolved && (
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button onClick={() => resolve(f.id)} style={{ padding: "0.375rem 0.75rem", borderRadius: "6px", border: "1px solid #d2d2d7", background: "#fff", fontSize: "0.8125rem", cursor: "pointer" }}>Dismiss</button>
                  <button style={{ padding: "0.375rem 0.75rem", borderRadius: "6px", border: "none", background: "#ff3b30", color: "#fff", fontSize: "0.8125rem", fontWeight: 500, cursor: "pointer" }}>Escalate</button>
                </div>
              )}
            </div>
          </div>
        ))}
        {displayed.length === 0 && <p style={{ textAlign: "center", color: "#6e6e73", padding: "3rem 0" }}>No fraud flags to review.</p>}
      </div>
    </div>
  );
}
