# ADR-001: Supabase over Xano for Backend Platform

**Status**: Accepted  
**Date**: 2026-02-11  
**Deciders**: Solomon (CEO), Engineering Team

## Context

The original Scarnergy build used Xano as a backend-as-a-service (BaaS) for REST endpoints, domain data storage, and event orchestration. While functional for prototyping, Xano presents significant concerns for production deployment: it is proprietary (no self-hosting), uses opaque pricing at scale, lacks native real-time WebSocket support critical for live measurement streaming, and does not provide direct PostgreSQL access needed for TimescaleDB time-series extensions.

## Decision

Replace Xano with **Supabase (self-hosted)** as the backend platform.

## Rationale

| Factor | Xano | Supabase |
|--------|------|----------|
| License | Proprietary | Apache 2.0 / MIT |
| Self-hosting | Not available | Full Docker deployment |
| Real-time | Webhooks only | Native WebSocket (Realtime) |
| Database access | Abstracted | Direct PostgreSQL + extensions |
| Time-series | Not supported | TimescaleDB extension |
| Mobile SDK | Generic REST | First-class @supabase/supabase-js |
| Auth | JWT via API | GoTrue with email, magic link, SSO |
| Storage | Not included | S3-compatible object storage |
| Edge Functions | Visual function stacks | Deno TypeScript functions |
| Cost at scale | Per-request pricing | Infrastructure cost only |

## Consequences

**Positive:**
- Full control over data and infrastructure
- Native real-time subscriptions for measurement streaming
- TimescaleDB hypertables for efficient measurement storage
- Row-Level Security at the database level
- No vendor lock-in; standard PostgreSQL

**Negative:**
- Self-hosting requires DevOps expertise
- More initial setup complexity than Xano's managed service
- Need to build visual logic that Xano's function stacks provided

**Mitigations:**
- Use official Supabase Docker images with documented compose files
- Edge Functions replace Xano function stacks with TypeScript code
- Fallback option: Supabase Cloud for managed hosting if self-hosting proves complex
