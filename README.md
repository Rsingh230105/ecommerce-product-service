# Product Service

Product Service owns the product catalogue for the e-commerce application. Order Service calls it to verify a product exists and to obtain the current price before calculating an order total.

## Responsibilities

- Create, list, retrieve, update, and delete products under `/products`.
- Provide `/health` and database-backed `/ready` endpoints.
- Persist product data in PostgreSQL using SQLAlchemy.
- Manage schema changes with Alembic.
- Listen on port `8000` in the container.

## API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/products` | Create a product |
| `GET` | `/products` | List products (supports `page` and `limit`) |
| `GET` | `/products/{product_id}` | Retrieve a product |
| `PUT` | `/products/{product_id}` | Update a product |
| `DELETE` | `/products/{product_id}` | Delete a product |
| `GET` | `/health` | Process health check |
| `GET` | `/ready` | Database readiness check |

Open `/docs` on the service URL for interactive API documentation.

## Run locally with Docker Compose

1. Copy `.env.example` to `.env` and set a local-only password.
2. From this directory, run:

   ```powershell
   docker compose up --build
   ```

3. Open `http://localhost:8000/docs`.

Compose maps the PostgreSQL container's port 5432 to host port 5433. The API uses the Compose service hostname `postgres` and port 5432 from inside Docker. Do not use the host port from another container.

The Compose file expects an external Docker network named `ecommerce-network`; create it before startup if it does not already exist:

```powershell
docker network create ecommerce-network
```

If that network already exists, Docker will report the name conflict; in that case, keep using the existing network.

## Configuration

See `.env.example` for the local settings:

- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`
- `PRODUCT_SERVICE_URL` is present in the example for callers but is not required by Product Service itself.

Never commit `.env` or put credentials in source control.

## Database migrations

The image entrypoint runs Alembic before starting Uvicorn. For local/manual migration work, use the service's configured environment and run:

```powershell
alembic upgrade head
```

Product and Order share the deployed RDS instance but use different Alembic version-table names to keep their migration histories separate.

## Tests

From this directory, with the service dependencies installed and a reachable PostgreSQL database configured:

```powershell
python -m pytest
```

Tests that exercise CRUD endpoints use the configured database; they are not all isolated unit tests. Ensure the test database is disposable and available before running them.

## How it connects to the application

- Public clients reach Product Service through ALB path routing for `/products` and `/products/*`.
- Order Service uses `http://product-service:8000` over ECS Service Connect in AWS.
- Product data and product price are owned by this service. Order Service stores the price snapshot used for each order.

## Next improvement

Add deterministic test database setup and teardown, plus pagination and database readiness tests. The current CI workflow uses a disposable PostgreSQL database and applies migrations before running tests. Coordinate changes to the shared ECS database migration strategy with the Order Service and Terraform projects.

## CI and development deployment

The `CI and deploy (dev)` GitHub Actions workflow runs on pull requests and pushes to `dev`, and can be manually dispatched for an initial deployment or redeployment. It starts a disposable PostgreSQL 16 test database, runs the test suite, and verifies the Docker image builds.

On pushes or a manual run on branch `dev`, the AWS deploy job runs only when the repository Actions variable `AWS_ECR_ECS_DEPLOY_ENABLED` is set to the string `true`. Before enabling it:

1. Apply the development infrastructure so the ECR repository and ECS service exist.
2. Configure GitHub repository variables `AWS_REGION` (`ap-south-1`) and `AWS_DEPLOY_ROLE_ARN`.
3. Configure a dedicated AWS role to trust `token.actions.githubusercontent.com`, with audience `sts.amazonaws.com` and subject `repo:Rsingh230105/ecommerce-product-service:ref:refs/heads/dev`.
4. Limit that role to ECR push operations for `ecommerce-dev-product-service`, ECS describe/register/update operations for the dev cluster/service, and `iam:PassRole` only for the existing ECS task roles (condition `iam:PassedToService=ecs-tasks.amazonaws.com`). `ecr:GetAuthorizationToken` and task-definition registration may require `Resource: "*"`.
5. Set `AWS_ECR_ECS_DEPLOY_ENABLED=true`.

Each deployment publishes an immutable image tagged with the Git commit SHA, applies it to the latest Terraform task-definition family revision, and waits for the Product ECS service to become stable. Terraform ignores only the deployed task-definition revision so a later apply does not roll back a CI deployment; Terraform still owns the task-definition template and the service's other settings. If the job is not enabled, CI still runs but no AWS access or deployment is attempted. This workflow targets development only; it does not deploy production.