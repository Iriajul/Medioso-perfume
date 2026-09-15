// Container/deploy health probe (see docker-compose.base.yml and server-deploy.sh).
export const dynamic = "force-dynamic";

export function GET() {
  return Response.json({ status: "ok", service: "madperfume-frontend" });
}
