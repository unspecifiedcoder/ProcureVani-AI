export default function AuditPage() {
  const events = [
    { id: 1, timestamp: "2026-02-28 14:32:00", msme: "TechCraft Industries", action: "PASSPORT_ISSUED", details: "Passport PV-A3F2B1C9 issued. LCV: 84.2%.", passport_id: "PV-A3F2B1C9" },
    { id: 2, timestamp: "2026-02-28 14:31:45", msme: "TechCraft Industries", action: "COMPLIANCE_CHECK", details: "PPP-MII check passed. HS 8539.", passport_id: "PV-A3F2B1C9" },
    { id: 3, timestamp: "2026-02-27 10:15:00", msme: "Sharma Textiles", action: "PASSPORT_ISSUED", details: "Passport PV-B4C3D2E8 issued.", passport_id: "PV-B4C3D2E8" },
    { id: 4, timestamp: "2026-02-26 16:42:00", msme: "AutoParts Co", action: "FRAUD_FLAG", details: "LCV below threshold. Flagged for review.", passport_id: "PV-C5D4E3F7" },
    { id: 5, timestamp: "2026-02-25 09:20:00", msme: "GreenBrew Coffee", action: "PASSPORT_ISSUED", details: "Passport PV-D6E5F4A3 issued.", passport_id: "PV-D6E5F4A3" },
  ];

  const actionStyle: Record<string, { color: string; bg: string }> = {
    PASSPORT_ISSUED: { color: "#1a8d3e", bg: "#e8f8ee" },
    COMPLIANCE_CHECK: { color: "#0066cc", bg: "#e5f0ff" },
    FRAUD_FLAG: { color: "#cc1a0f", bg: "#ffeeed" },
  };

  return (
    <div>
      <h2 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "1.5rem" }}>Audit Trail</h2>
      <section style={{ background: "#fff", borderRadius: "10px", border: "1px solid #d2d2d7", overflow: "hidden" }}>
        <table>
          <thead><tr><th>Timestamp</th><th>MSME</th><th>Action</th><th>Details</th><th>Passport</th></tr></thead>
          <tbody>
            {events.map(e => {
              const style = actionStyle[e.action] || { color: "#6e6e73", bg: "#f5f5f7" };
              return (
                <tr key={e.id}>
                  <td className="mono" style={{ fontSize: "0.8125rem", color: "#6e6e73", whiteSpace: "nowrap" }}>{e.timestamp}</td>
                  <td style={{ fontWeight: 500 }}>{e.msme}</td>
                  <td><span style={{ padding: "2px 8px", borderRadius: "4px", fontSize: "0.6875rem", fontWeight: 600, background: style.bg, color: style.color, textTransform: "uppercase" }}>{e.action.replace("_", " ")}</span></td>
                  <td style={{ fontSize: "0.8125rem", color: "#6e6e73", maxWidth: "400px" }}>{e.details}</td>
                  <td className="mono" style={{ fontSize: "0.8125rem" }}><a href={`/verify?id=${e.passport_id}`}>{e.passport_id}</a></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </section>
    </div>
  );
}
