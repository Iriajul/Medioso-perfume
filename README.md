# Mad Perfume

Monorepo for the Mad Perfume platform: the Django API + the Next.js admin
dashboard, with infrastructure and CI/CD. The customer mobile app (Android/iOS)
lives in a separate repository and consumes this API.

```
services/
  backend/     Django 6 + DRF API, Django admin, OpenAPI docs   → api.bpmstudio.pt
  frontend/    Next.js admin dashboard                           → admin.bpmstudio.pt
deployment/
  compose/     docker-compose base + local / staging / production overrides
  environments/ per-env .env example files (real ones are gitignored)
  nginx/       reverse-proxy templates (rendered by Ansible)
  scripts/     deploy, server-deploy (run by CI via SSM), rollback, terraform helpers
  monitoring/  Prometheus, Grafana, Loki, Promtail
infrastructure/
  terraform/   bootstrap (state bucket, lock table, ECR, GitHub OIDC) + shared module + envs
  ansible/     server provisioning: docker, nginx, certbot, app-deploy, monitoring
  iam/         least-privilege deployer policies
.github/workflows/
  pr-checks.yml       backend tests, frontend lint/build, compose + terraform validation
  staging-deploy.yml  push to `staging` → build images → deploy staging via SSM
  deploy.yml          push to `main`    → build images → deploy production via SSM
```

## Local development

```bash
make up-local      # postgres + redis + backend (:8000) + frontend (:3000), hot reload
make down
```

- API health: http://localhost:8000/api/v1/health/
- API docs: http://localhost:8000/api/docs/
- Dashboard: http://localhost:3000

Superuser: set `DJANGO_SUPERUSER_EMAIL` / `DJANGO_SUPERUSER_PASSWORD` in
`deployment/environments/.env.local.backend` (copy from the `.example`).

## Environments

| | Branch | API | Dashboard |
|---|---|---|---|
| Production | `main` | `api.bpmstudio.pt` | `admin.bpmstudio.pt` |
| Staging | `staging` | `staging-api.bpmstudio.pt` | `staging-admin.bpmstudio.pt` |

AWS: account `default` CLI profile, region `us-east-1`. See
[docs/DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md) for first-time setup.
