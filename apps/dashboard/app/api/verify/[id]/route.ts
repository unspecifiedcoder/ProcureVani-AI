import { NextResponse } from "next/server";

const mockPassports: Record<string, any> = {
  "PV-A3F2B1C9": {
    passport_id: "PV-A3F2B1C9",
    msme_id: "MSME-001",
    company_name: "TechCraft Industries",
    dpiit_no: "DPIIT-2024-001234",
    gstin: "36AABCT1234A1Z5",
    product_name: "LED Lamps",
    hs_code: "8539",
    lcv_score: 84.2,
    threshold: 50,
    rating: "GREEN",
    status: "ACTIVE",
    issued_at: "2026-02-28",
    valid_until: "2027-02-28",
    doc_hash: "0x1234...abcd",
    ipfs_hash: "QmHash...",
    blockchain_tx: "0xabcdef123456",
  },
  "PV-C5D4E3F7": {
    passport_id: "PV-C5D4E3F7",
    msme_id: "MSME-014",
    company_name: "AutoParts Co",
    dpiit_no: "DPIIT-2024-009012",
    gstin: "27AACCA7788F1Z4",
    product_name: "Motor Vehicle Parts",
    hs_code: "8704",
    lcv_score: 45.0,
    threshold: 50,
    rating: "RED",
    status: "FLAGGED",
    issued_at: "2026-02-26",
    valid_until: "2027-02-26",
    doc_hash: "0x99ef...bead",
    ipfs_hash: "QmFlagged...",
    blockchain_tx: "0xflag12345",
  },
};

export async function GET(
  _request: Request,
  { params }: { params: { id: string } },
) {
  const passportId = params.id.toUpperCase();
  const passport = mockPassports[passportId];

  if (!passport) {
    return NextResponse.json({ error: "Passport not found" }, { status: 404 });
  }

  return NextResponse.json(passport);
}
