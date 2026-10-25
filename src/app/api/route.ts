import { NextResponse } from "next/server";

// The route returns a constant payload. Marking it force-static keeps the
// GitHub Pages static export build working (see deploy-pages.yml).
export const dynamic = "force-static";

export async function GET() {
  return NextResponse.json({ message: "Hello, world!" });
}