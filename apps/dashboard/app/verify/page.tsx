"use client";

import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useSearchParams } from "next/navigation";

type PassportResult = {
  passport_id: string;
  company_name: string;
  dpiit_no: string;
  gstin: string;
  product_name: string;
  hs_code: string;
  lcv_score: number;
  threshold: number;
  rating: string;
  status: string;
  issued_at: string;
  valid_until: string;
  doc_hash: string;
  ipfs_hash: string;
  blockchain_tx: string;
};

const EXAMPLES = ["PV-A3F2B1C9", "PV-C5D4E3F7"];

export default function VerifyPage() {
  const searchParams = useSearchParams();
  const initialPassportId = useMemo(() => searchParams.get("id") ?? "", [searchParams]);
  const [passportId, setPassportId] = useState(initialPassportId);
  const [result, setResult] = useState<PassportResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (initialPassportId) {
      void verify(initialPassportId);
    }
  }, [initialPassportId]);

  const verify = async (value = passportId) => {
    const trimmed = value.trim().toUpperCase();
    if (!trimmed) {
      setError("Enter a passport ID to continue.");
      setResult(null);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`/api/verify/${trimmed}`);
      if (!response.ok) {
        setResult(null);
        setError(`Passport ${trimmed} not found.`);
        return;
      }

      const data = (await response.json()) as PassportResult;
      setPassportId(trimmed);
      setResult(data);
    } catch {
      setResult(null);
      setError("Verification service is currently unavailable.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: "1.5rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.35rem" }}>Verify Passport</h2>
        <p style={{ color: "#6e6e73", fontSize: "0.875rem" }}>
          Search by passport ID and confirm blockchain-backed compliance details.
        </p>
      </div>

      <div
        style={{
          background: "#fff",
          border: "1px solid #d2d2d7",
          borderRadius: "12px",
          padding: "1rem",
          marginBottom: "1.5rem",
        }}
      >
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "0.75rem" }}>
          <input
            type="text"
            placeholder="Enter Passport ID (e.g. PV-A3F2B1C9)"
            value={passportId}
            onChange={(e) => setPassportId(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && void verify()}
            style={{
              flex: 1,
              minWidth: "260px",
              padding: "0.7rem 0.85rem",
              border: "1px solid #d2d2d7",
              borderRadius: "8px",
              fontSize: "0.9rem",
            }}
          />
          <button
            onClick={() => void verify()}
            disabled={loading}
            style={{
              padding: "0.7rem 1.25rem",
              borderRadius: "8px",
              border: "none",
              background: loading ? "#9dbce1" : "#0066cc",
              color: "#fff",
              fontSize: "0.875rem",
              fontWeight: 600,
              cursor: loading ? "default" : "pointer",
            }}
          >
            {loading ? "Checking..." : "Verify"}
          </button>
        </div>
        <p style={{ color: "#6e6e73", fontSize: "0.8125rem" }}>
          Try: {EXAMPLES.map((id) => (
            <button
              key={id}
              onClick={() => {
                setPassportId(id);
                void verify(id);
              }}
              style={{
                border: "none",
                background: "transparent",
                color: "#0066cc",
                cursor: "pointer",
                marginLeft: "0.4rem",
                fontFamily: "monospace",
              }}
            >
              {id}
            </button>
          ))}
        </p>
      </div>

      {error && <p style={{ color: "#ff3b30", fontSize: "0.875rem", marginBottom: "1rem" }}>{error}</p>}

      {result && (
        <div style={{ background: "#fff", borderRadius: "12px", border: "1px solid #d2d2d7", overflow: "hidden" }}>
          <div
            style={{
              padding: "1.25rem",
              borderBottom: "1px solid #e8e8ed",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "1rem",
              flexWrap: "wrap",
            }}
          >
            <div>
              <h3 className="mono" style={{ fontSize: "1.25rem", fontWeight: 700 }}>{result.passport_id}</h3>
              <p style={{ fontSize: "0.8125rem", color: "#6e6e73", marginTop: "2px" }}>
                Verified against the mocked compliance ledger
              </p>
            </div>
            <span
              style={{
                padding: "4px 12px",
                borderRadius: "999px",
                fontWeight: 600,
                fontSize: "0.8125rem",
                background: result.status === "ACTIVE" ? "#e8f8ee" : "#ffeeed",
                color: result.status === "ACTIVE" ? "#1a8d3e" : "#cc1a0f",
              }}
            >
              {result.status}
            </span>
          </div>

          <div style={{ padding: "1.25rem", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1.25rem" }}>
            <Section title="MSME Details">
              <Field label="Company" value={result.company_name} />
              <Field label="DPIIT No." value={result.dpiit_no} />
              <Field label="GSTIN" value={result.gstin} mono />
            </Section>

            <Section title="Product">
              <Field label="Product" value={result.product_name} />
              <Field label="HS Code" value={result.hs_code} mono />
            </Section>

            <Section title="Compliance">
              <Field label="LCV Score" value={`${result.lcv_score}%`} />
              <Field label="Threshold" value={`${result.threshold}%`} />
              <Field label="Rating" value={result.rating} />
            </Section>

            <Section title="Validity">
              <Field label="Issued" value={result.issued_at} />
              <Field label="Valid Until" value={result.valid_until} />
            </Section>
          </div>

          <div style={{ padding: "1.25rem", borderTop: "1px solid #e8e8ed", background: "#fafafa" }}>
            <Section title="Blockchain">
              <Field label="Doc Hash" value={result.doc_hash} mono />
              <Field label="IPFS" value={result.ipfs_hash} mono />
              <Field label="TX Hash" value={result.blockchain_tx} mono />
            </Section>
          </div>
        </div>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div>
      <h4
        style={{
          fontSize: "0.75rem",
          fontWeight: 700,
          color: "#86868b",
          textTransform: "uppercase",
          letterSpacing: "0.06em",
          marginBottom: "0.6rem",
        }}
      >
        {title}
      </h4>
      {children}
    </div>
  );
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div style={{ marginBottom: "0.4rem", display: "flex", gap: "0.5rem" }}>
      <span style={{ fontSize: "0.8125rem", color: "#6e6e73", minWidth: "96px" }}>{label}:</span>
      <span style={{ fontSize: "0.8125rem", fontFamily: mono ? "monospace" : "inherit", wordBreak: "break-all" }}>
        {value}
      </span>
    </div>
  );
}
