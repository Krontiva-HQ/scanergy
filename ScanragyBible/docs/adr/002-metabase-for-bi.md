# ADR-002: Metabase for Business Intelligence Dashboards

**Status**: Accepted  
**Date**: 2026-02-11  
**Deciders**: Solomon (CEO), Engineering Team

## Context

Scarnergy requires business intelligence dashboards for inspection portfolio analytics, measurement quality monitoring, energy performance tracking, and inspector productivity analysis. The KronGage platform uses Apache Superset, but for Scarnergy's use case we need a more accessible tool that non-technical supervisors and managers can use without SQL knowledge.

## Decision

Use **Metabase** as the primary BI dashboard platform for Scarnergy.

## Rationale

- **Accessibility**: Metabase's "Ask a Question" UI allows non-technical users to explore data without SQL
- **Self-hosted**: Open-source (AGPL), full Docker deployment, no cloud dependency
- **PostgreSQL native**: Direct connection to Supabase PostgreSQL with automatic schema discovery
- **Embedded analytics**: iFrame embedding for Supervisor Web App integration
- **Community**: 90,000+ organizations, active development, extensive documentation
- **Setup speed**: Database connection → first dashboard in under 5 minutes

**Why not Superset?** Apache Superset is more powerful for complex data analysis but requires significant SQL expertise and engineering resources to deploy and manage. Scarnergy's primary dashboard users are supervisors and managers, not data analysts. Metabase's intuitive interface matches this user profile better.

**Grafana complements Metabase**: Grafana handles real-time IoT monitoring (live measurements, device status, MQTT throughput) where its time-series visualization excels. Metabase handles the analytical BI layer (portfolio reports, trends, performance metrics).

## Consequences

- Supervisors can build their own reports without engineering support
- Dashboard creation is 3–5x faster than Superset for standard use cases
- Limited compared to Superset for advanced geospatial analysis (mitigated by PostGIS queries)
- Two dashboard tools (Metabase + Grafana) instead of one, but each serves a distinct purpose
