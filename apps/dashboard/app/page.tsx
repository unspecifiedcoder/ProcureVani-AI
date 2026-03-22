export default function OverviewPage() {
  return (
    <div>
      <h2 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "1.5rem" }}>Overview</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem", marginBottom: "2rem" }}>
        {[["Total Passports", "1,234"], ["Active", "1,089", "#34c759"], ["Flagged", "12", "#ff3b30"], ["Avg LCV", "72.4%"]].map(([label, value, color]) => (
          <div key={label} style={{ background: "#fff", borderRadius: "10px", border: "1px solid #d2d2d7", padding: "1.25rem", borderLeft: `4px solid ${color || "#1d1d1f"}` }}>
            <p style={{ fontSize: "0.75rem", color: "#6e6e73", textTransform: "uppercase", letterSpacing: "0.04em" }}>{label}</p>
            <p style={{ fontSize: "1.75rem", fontWeight: 700, color: color || "#1d1d1f" }}>{value}</p>
          </div>
        ))}
      </div>
      <section style={{ background: "#fff", borderRadius: "10px", border: "1px solid #d2d2d7", marginBottom: "2rem", overflow: "hidden" }}>
        <div style={{ padding: "1rem 1.25rem", borderBottom: "1px solid #e8e8ed" }}>
          <h3 style={{ fontSize: "0.9375rem", fontWeight: 600 }}>Recent Passports</h3>
        </div>
        <table>
          <thead><tr><th>Passport ID</th><th>Company</th><th>Product</th><th>LCV %</th><th>Status</th><th>Date</th></tr></thead>
          <tbody>
            {[["PV-A3F2B1C9","TechCraft Industries","LED Lamps","84.2%","ACTIVE","28 Feb 2026"],["PV-B4C3D2E8","Sharma Textiles","Cotton Fabric","78.5%","ACTIVE","27 Feb 2026"],["PV-C5D4E3F7","AutoParts Co","Motor Parts","45.0%","FLAGGED","26 Feb 2026"]].map(([id, company, product, lcv, status, date]) => (
              <tr key={id}>
                <td className="mono" style={{ fontSize: "0.8125rem" }}><a href={`/verify?id=${id}`}>{id}</a></td>
                <td>{company}</td><td>{product}</td>
                <td style={{ fontWeight: 600, color: lcv === "45.0%" ? "#ff3b30" : "#34c759" }}>{lcv}</td>
                <td><span style={{ padding: "2px 8px", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 600, background: status === "ACTIVE" ? "#e8f8ee" : "#ffeeed", color: status === "ACTIVE" ? "#1a8d3e" : "#cc1a0f" }}>{status}</span></td>
                <td style={{ color: "#6e6e73" }}>{date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
        <section style={{ background: "#fff", borderRadius: "10px", border: "1px solid #d2d2d7", padding: "1.25rem" }}>
          <h3 style={{ fontSize: "0.9375rem", fontWeight: 600, marginBottom: "1rem" }}>Compliance by Category</h3>
          {[["LED Lamps", 92], ["Textiles", 85], ["Computers", 78], ["Automotive", 65]].map(([cat, rate]) => (
            <div key={cat} style={{ marginBottom: "0.75rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8125rem", marginBottom: "4px" }}>
                <span>{cat}</span><span style={{ color: "#6e6e73" }}>{rate}%</span>
              </div>
              <div style={{ height: "6px", background: "#e8e8ed", borderRadius: "3px", overflow: "hidden" }}>
                <div style={{ width: `${rate}%`, height: "100%", background: rate >= 80 ? "#34c759" : rate >= 60 ? "#ff9500" : "#ff3b30", borderRadius: "3px" }} />
              </div>
            </div>
          ))}
        </section>
        <section style={{ background: "#fff", borderRadius: "10px", border: "1px solid #d2d2d7", padding: "1.25rem" }}>
          <h3 style={{ fontSize: "0.9375rem", fontWeight: 600, marginBottom: "1rem" }}>Quick Actions</h3>
          {[["/passports", "View All Passports"], ["/audit", "Audit Trail"], ["/fraud", "Review Fraud Flags"], ["/verify", "Verify a Passport"]].map(([href, label]) => (
            <a key={href} href={href} style={{ display: "block", padding: "0.625rem 0.875rem", background: "#f5f5f7", borderRadius: "6px", fontSize: "0.875rem", fontWeight: 500, color: "#0066cc", marginBottom: "0.5rem" }}>
              {label}
            </a>
          ))}
        </section>
      </div>
    </div>
  );
}
