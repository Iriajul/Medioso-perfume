import { NextResponse, type NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login", "/forgot-password", "/reset-password"];

// Optimistic check only: presence of the session cookie. The API still
// authorizes every request with the JWT.
export function proxy(request: NextRequest) {
  const loggedIn = request.cookies.has("refresh");
  const path = request.nextUrl.pathname;

  if (!loggedIn && !PUBLIC_PATHS.includes(path)) return NextResponse.redirect(new URL("/login", request.url));
  if (loggedIn && path === "/login") return NextResponse.redirect(new URL("/", request.url));
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|logo.png).*)"],
};
