import { NextResponse } from "next/server";

const mockPassports = [
  {
    passport_id: "PV-A3F2B1C9",
    company_name: "TechCraft Industries",
    dpiit_no: "DPIIT-2024-001234",
    product_name: "LED Lamps",
    hs_code: "8539",
    lcv_score: 84.2,
    threshold: 50,
    status: "ACTIVE",
    issued_at: "2026-02-28",
    valid_until: "2027-02-28",
  },
  {
    passport_id: "PV-B4C3D2E8",
    company_name: "Sharma Textiles",
    dpiit_no: "DPIIT-2024-005678",
    product_name: "Cotton Fabric",
    hs_code: "5208",
    lcv_score: 78.5,
    threshold: 75,
    status: "ACTIVE",
    issued_at: "2026-02-27",
    valid_until: "2027-02-27",
  },
  {
    passport_id: "PV-C5D4E3F7",
    company_name: "AutoParts Co",
    dpiit_no: "DPIIT-2024-009012",
    product_name: "Motor Vehicle Parts",
    hs_code: "8704",
    lcv_score: 45.0,
    threshold: 50,
    status: "FLAGGED",
    issued_at: "2026-02-26",
    valid_until: "2027-02-26",
  },
];

export async function GET() {
  return NextResponse.json({
    total_passports: 1234,
    active: 1089,
    flagged: 12,
    avg_lcv: 72.4,
    recent: mockPassports,
  });
}
