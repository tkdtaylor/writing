# One-pager: Ship self-serve 72-hour webhook replay for merchant workspaces

## 1. BLUF / Decision Call

Approve **Option A** (`S3` `72-hour` dead-letter store plus rate-limited `SQS` replay workers, `$190/month` run cost, `8` engineer-days) by **Thursday, October 8 at 17:00 UTC**. The **Director of Merchant Platform** owns this reversible Type 2 call. Launching console and API replay behind `webhooks.self_serve_replay` lets merchant admins recover dropped event windows in under `2` minutes and reclaims `11` on-call engineer-hours per week ahead of the November 1 holiday freeze.

## 2. Problem and Customer/System Baseline

From September 1 to September 30, transient merchant `5xx` timeouts dropped `14,200` webhook batches across production storefronts (`[measured]`). Workspace admins cannot replay failed batches today. Those timeouts generated `68` support tickets (`38%` of weekly Integration Support volume) and a `4.6-hour` median merchant wait while on-call engineers ran `replay-dlq.sh` (`11` hours/week). Onboarding `180` Q4 holiday workspaces before November 1 will scale ticket toil linearly.

## 3. Scope and Explicit Non-Goals

This rollout writes exhausted webhook payloads to an encrypted prefix (`s3://events-dlq-prod/` with `KMS` keys and a `72-hour` lifecycle TTL). Admins trigger window replays in the console or via `POST /v1/webhooks/replays` behind a `50 RPS` per-endpoint token bucket. Three adjacent requests stay out of scope for October. Payload schema mapping is excluded. Retention stops strictly at `72` hours instead of acting as a compliance archive, and primary live retries remain at `5` attempts over `30` minutes.

## 4. Viable Options and Tradeoffs

**Option A (Recommended)** stores failed JSON bodies in `s3://events-dlq-prod/` and drains replay jobs through dedicated `webhook-replay-workers` (`8` engineer-days, `$190/month` in `S3` and `SQS` spend). Merchants recover missed order events in under `2` minutes, while the `50 RPS` token bucket protects recovering partner origins from burst traffic. **Option B** writes `64 KB` failed bodies to a synchronous table on `events_prod` Postgres (`5` engineer-days, `$640/month` in `RDS` storage and `IOPS`). Option B loses because outage spikes raise primary `WAL` replication lag during checkout bursts. **Status Quo** keeps manual `replay-dlq.sh` ticket runs (`$0` new cloud spend, `11` engineer-hours/week toil). That path loses because a `4.6-hour` median blind spot stalls Q4 merchant fulfillment.

## 5. Risks, Kill Switch, and Owned Next Steps

Large concurrent replays could overload a recovering merchant server, so replay jobs run on isolated `webhook-replay-workers` queues rather than live delivery pools. Flipping `webhooks.self_serve_replay=false` halts new replay requests within `15` seconds whenever worker `CPU` exceeds `75%` or live `p95` delivery latency passes `2.0` seconds. Header scrubbing rules still need security sign-off (`[TK: confirm PCI header redaction sign-off with Security Engineering by October 9]`).

1. Provision `s3://events-dlq-prod/` with `KMS` encryption and `72-hour` lifecycle expiration (`Owner: Messaging Infra`, `October 12`).
2. Ship `POST /v1/webhooks/replays` with a `50 RPS` per-endpoint token bucket (`Owner: Merchant API team`, `October 16`).
3. Enable beta replay for `10` partner workspaces and verify live `p95` stays below `2.0` seconds (`Owner: Developer Console team`, `October 20`).
