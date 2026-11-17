# Decision brief: Split EU catalog search shards before October 15 freeze

Approve `$1,480/month` (`Option A`) by **Friday, September 18 at 17:00 UTC** to add two dedicated `r7g.2xlarge` OpenSearch data nodes in `eu-central-1`. The **VP of Commerce Infrastructure** holds this decision. Isolating multi-filter facet shards brings `EU` storefront search `p95` latency back under our `500 ms` `Q4` `SLA` ahead of the October 15 peak-traffic freeze.

## Decision summary

- **Call** - Approve `$1,480/month` in `eu-central-1` node spend (`Option A`) over `Option B` (`60-second` stale facet cache) or status quo by September 18 at `17:00 UTC`.
- **Recommendation** - Fund `Option A` (`$17,760` annualized cloud spend). Doing nothing (`$0` infra cost) leaves `EU` evening search above `1,000 ms` `p95` and risks `$11,000/month` in abandoned filter sessions. `Option B` (`$0` infra cost, `4` engineer-days) displays sold-out sizes for up to `60` seconds during flash sales.
- **Impact** - Shoppers on `EU` storefronts filter `2M-SKU` apparel catalogs in under `320 ms` at `p95` during evening peaks rather than waiting past `1.0` second.
- **Evidence** - Production telemetry and staging replay separate verified measurements from open load limits in the section below.
- **Risk** - Shard relocation adds `15%` disk and network `I/O` for `25` minutes during the `02:00 UTC` window. Flipping `search.eu_dedicated_pool=false` restores shared-pool routing within `10` seconds if error rates pass `0.2%`.

## Vetted evidence and open limits

- **`[measured]` Production tail regression** - `EU` multi-filter `p95` latency hit `1,080 ms` across `1.4M` queries (`September 1-14`) against a `340 ms` `8-week` baseline before August facet expansion. Shared `m6g.xlarge` `CPU` saturates above `650 RPS`.
- **`[measured]` Staging shard isolation** - Dedicated `r7g.2xlarge` facet nodes cut `p95` latency from `1,040 ms` to `295 ms` across `500k` replayed `EU` queries at `900 RPS`. Single-region staging replay may understate cross-zone replication overhead by `10` to `20 ms`.
- **`[inferred]` Shopper filter exits** - Funnel logs link search responses slower than `800 ms` with a `1.8` point rise in mobile exits (`N = 310k` `EU` sessions vs August median). Concurrent back-to-school promos confound direct revenue attribution.
- **`[open]` Black Friday burst ceiling** - Staging tests have not yet validated traffic above `1,400 RPS` (`[TK: run 1,800 RPS burst check with Search SRE owner Nadia Chen by September 22]`).

## Next actions if approved

1. Provision two `r7g.2xlarge` nodes in `eu-central-1` behind `search.eu_dedicated_pool` (`Owner: Search SRE`, `September 21`).
2. Run the `1,800 RPS` burst benchmark and publish `p95` and `p99` numbers (`Owner: Search SRE`, `September 22`).
3. Ramp `10%`, `50%`, and `100%` of `EU` facet traffic across three `02:00 UTC` windows (`Owner: Catalog Search team`, `September 24-28`).
