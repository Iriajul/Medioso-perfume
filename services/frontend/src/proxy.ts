import { NextResponse, type NextRequest } from "next/server";

// Optimistic check only: presence of the session cookie. The API still
// authorizes every request with the JWT.
export function proxy(request: NextRequest) {
  const loggedIn = request.cookies.has("refresh");
  const onLogin = request.nextUrl.pathname === "/login";

  if (!loggedIn && !onLogin) return NextResponse.redirect(new URL("/login", request.url));
  if (loggedIn && onLogin) return NextResponse.redirect(new URL("/", request.url));
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|logo.png).*)"],
};
