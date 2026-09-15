import { NextResponse, type NextRequest } from "next/server";
import { API_URL } from "@/lib/api";

const PUBLIC_PATHS = ["/login", "/forgot-password", "/reset-password"];
const DAY = 60 * 60 * 24;

function claimsExp(token: string | undefined) {
  try {
    return JSON.parse(atob(token!.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"))).exp as number;
  } catch {
    return 0;
  }
}

// Optimistic session check plus silent access-token refresh. The API still
// authorizes every request with the JWT.
export async function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname;
  const refresh = request.cookies.get("refresh")?.value;
  const toLogin = () => {
    const res = NextResponse.redirect(new URL("/login", request.url));
    ["access", "refresh", "remember"].forEach((c) => res.cookies.delete(c));
    return res;
  };

  if (!refresh) return PUBLIC_PATHS.includes(path) ? NextResponse.next() : toLogin();
  if (path === "/login") return NextResponse.redirect(new URL("/", request.url));
  if (PUBLIC_PATHS.includes(path)) return NextResponse.next();

  // Refresh when the access token is missing or expires within a minute.
  if (claimsExp(request.cookies.get("access")?.value) - 60 > Date.now() / 1000) return NextResponse.next();

  const res = await fetch(`${API_URL}/api/v1/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  }).catch(() => null);
  if (!res?.ok) return toLogin();

  const tokens: { access: string; refresh: string } = await res.json();
  // Forward the new tokens to this request's server components...
  request.cookies.set("access", tokens.access);
  request.cookies.set("refresh", tokens.refresh);
  const response = NextResponse.next({ request: { headers: request.headers } });
  // ...and store them in the browser.
  const base = { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", path: "/" } as const;
  const remember = request.cookies.has("remember");
  response.cookies.set("access", tokens.access, { ...base, maxAge: 60 * 60 });
  response.cookies.set("refresh", tokens.refresh, remember ? { ...base, maxAge: 30 * DAY } : base);
  return response;
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|logo.png).*)"],
};
