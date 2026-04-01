import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div style={{ display: "flex", minHeight: "100vh" }}>
          <nav style={{ width: "220px", background: "#fff", borderRight: "1px solid #d2d2d7", padding: "1.5rem 0" }}>
            <div style={{ padding: "0 1.25rem 1.5rem", borderBottom: "1px solid #e8e8ed" }}>
              <h1 style={{ fontSize: "1.125rem", fontWeight: 700 }}>ProcureVani</h1>
              <p style={{ fontSize: "0.75rem", color: "#86868b" }}>Compliance Dashboard</p>
            </div>
            <div style={{ padding: "0.75rem" }}>
              {[["/", "Overview"], ["/passports", "Passports"], ["/audit", "Audit Trail"], ["/fraud", "Fraud Flags"], ["/verify", "Verify"]].map(([href, label]) => (
                <a key={href} href={href} style={{ display: "block", padding: "0.5rem 0.75rem", borderRadius: "6px", color: "#1d1d1f", marginBottom: "2px" }}>
                  {label}
                </a>
              ))}
            </div>
          </nav>
          <main style={{ flex: 1, padding: "2rem", maxWidth: "1280px" }}>{children}</main>
        </div>
      </body>
    </html>
  );
}
