"use client";
import { useState } from "react";

const PASSPORTS = [
  { passport_id: "PV-A3F2B1C9", company: "TechCraft Industries", product: "LED Lamps", hs_code: "8539", lcv: 84.2, threshold: 50, status: "ACTIVE", state: "Telangana", issued_at: "2026-02-28" },
  { passport_id: "PV-B4C3D2E8", company: "Sharma Textiles", product: "Cotton Fabric", hs_code: "5208", lcv: 78.5, threshold: 75, status: "ACTIVE", state: "Maharashtra", issued_at: "2026-02-27" },
  { passport_id: "PV-C5D4E3F7", company: "AutoParts Co", product: "Motor Parts", hs_code: "8704", lcv: 45.0, threshold: 50, status: "FLAGGED", state: "Tamil Nadu", issued_at: "2026-02-26" },
  { passport_id: "PV-D6E5F4A3", company: "GreenBrew Coffee", product: "Instant Coffee", hs_code: "0901", lcv: 92.0, threshold: 80, status: "ACTIVE", state: "Karnataka", issued_at: "2026-02-25" },
  { passport_id: "PV-E7F6A5B2", company: "CoolTech HVAC", product: "Split AC", hs_code: "8415", lcv: 55.3, threshold: 50, status: "ACTIVE", state: "Delhi", issued_at: "2026-02-24" },
];

export default function PassportsPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");

  const filtered = PASSPORTS.filter(p => {
    const matchSearch = search === "" || p.passport_id.toLowerCase().includes(search.toLowerCase()) || p.company.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === "ALL" || p.status === statusFilter;
    return matchSearch && matchStatus;
  });

  return (
    <div>
      <h2 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "1.5rem" }}>Passports</h2>
      <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem" }}>
        <input type="search" placeholder="Search..." value={search} onChange={e => setSearch(e.target.value)} style={{ flex: 1, maxWidth: "400px", padding: "0.5rem 0.75rem", border: "1px solid #d2d2d7", borderRadius: "6px", fontSize: "0.875rem" }} />
        {["ALL", "ACTIVE", "FLAGGED", "REVOKED"].map(s => (
          <button key={s} onClick={() => setStatusFilter(s)} style={{ padding: "0.5rem 0.875rem", borderRadius: "6px", border: "1px solid #d2d2d7", background: statusFilter === s ? "#0066cc" : "#fff", color: statusFilter === s ? "#fff" : "#1d1d1f", fontSize: "0.8125rem", fontWeight: 500, cursor: "pointer" }}>
            {s}
          </button>
        ))}
      </div>
      <section style={{ background: "#fff", borderRadius: "10px", border: "1px solid #d2d2d7", overflow: "hidden" }}>
        <table>
          <thead><tr><th>Passport ID</th><th>Company</th><th>Product</th><th>HS Code</th><th>LCV %</th><th>Threshold</th><th>Status</th><th>State</th><th>Issued</th></tr></thead>
          <tbody>
            {filtered.map(p => (
              <tr key={p.passport_id}>
                <td className="mono" style={{ fontSize: "0.8125rem" }}><a href={`/verify?id=${p.passport_id}`}>{p.passport_id}</a></td>
                <td>{p.company}</td><td>{p.product}</td><td className="mono">{p.hs_code}</td>
                <td style={{ fontWeight: 600, color: p.lcv >= p.threshold ? "#34c759" : "#ff3b30" }}>{p.lcv}%</td>
                <td style={{ color: "#6e6e73" }}>{p.threshold}%</td>
                <td><span style={{ padding: "2px 8px", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 600, background: p.status === "ACTIVE" ? "#e8f8ee" : "#ffeeed", color: p.status === "ACTIVE" ? "#1a8d3e" : "#cc1a0f" }}>{p.status}</span></td>
                <td>{p.state}</td>
                <td style={{ color: "#6e6e73", fontSize: "0.8125rem" }}>{p.issued_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && <p style={{ padding: "2rem", textAlign: "center", color: "#6e6e73" }}>No passports found.</p>}
      </section>
    </div>
  );
}
