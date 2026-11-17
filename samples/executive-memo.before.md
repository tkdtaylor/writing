# Q3 Search Infrastructure Update

Over the past three weeks, the Search Platform team delved into catalog query traces across our European cluster. First, we looked at JVM garbage collection logs on the existing nodes — then we explored query rewrite rules and shard caching behavior.

It is worth noting that our catalog search substrate is a pivotal north star flywheel for shopper discovery. Here's where it gets interesting: multi-filter apparel queries are saturating shared CPU cores during peak evening traffic. The bottleneck is clear: shared nodes cannot keep up with facet aggregations. This initiative isn't just an infrastructure tweak, it's a holistic shift from query ergonomics to revenue resilience.

- **Performance:** Performance improved by 3x when our team spearheaded a dedicated node test in staging.
- **Efficiency:** Efficiency across the search scaffolding was bolstered significantly during synthetic runs.
- 🚀 Seamless query routing will elevate conversion across every European storefront.

At its core, we utilized two new nodes in staging and saw dramatic gains. In conclusion, please let us know by Friday if we can utilize `$1,480/month` in Q3 budget to spin up dedicated nodes before the October freeze.
