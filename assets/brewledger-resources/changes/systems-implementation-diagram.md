# Systems and Implementation Diagram – Feature Analysis

## Overview

A single markdown document was added that provides a full systems and implementation diagram for BrewLedger as a **layered tree** (big to small): system context → repository/platforms → technology stack → subsystems → key flows → UI and API map, plus a mapping of `changes/*` and BUGS-AND-FIXES-LOG to diagram nodes.

**Deliverable:** [docs/SYSTEMS-AND-IMPLEMENTATION-DIAGRAM.md](../docs/SYSTEMS-AND-IMPLEMENTATION-DIAGRAM.md)

**Sources:** analysis.md, changes/, ttb-beer-ledger-design.md, TTB-BEER-LEDGER-IMPLEMENTATION-LOG.md, BUGS-AND-FIXES-LOG.md, and codebase (server routes, mobile/console routers and views).

## Structure of the diagram document

- **How to read** and **Master tree** at the top for navigation.
- **Level 0:** System context (users, mobile/console apps, backend, Stripe, TTB).
- **Level 1:** Repository layout (server/, brewledger-app/, console/) and connections.
- **Level 2:** Technology stack and data stores (Vue, Vite, Capacitor, Express, SQLite, IndexedDB, sync boundary).
- **Level 3:** Subsystems with one diagram each: Auth, Sync, Billing, Inventory/Ledger, Batch/Recipe, TTB Form 5130.9.
- **Level 4:** Key flows: Sync–Ledger–cache, TTB data flow, Billing–sync–UI.
- **Level 5:** UI and API map: mobile view tree, console view tree, server API tree.
- **Changes and bugs mapping:** Table linking change docs and BUGS-AND-FIXES-LOG entries to diagram nodes/subsystems.

All diagrams use Mermaid (flowchart/subgraph) with valid syntax (no spaces in node IDs, camelCase/PascalCase, no reserved IDs).

## First-iteration review: potential weak points

1. **Staleness:** New routes, views, or API endpoints added later will not appear until the diagram doc is updated. Recommendation: when adding significant routes/views/APIs, update the Level 5 section and the master tree if needed.
2. **Detail depth:** Level 3/4 intentionally omit low-level details (e.g. exact entity table names, Dexie store names). For that, analysis.md and database_schema.dbml remain the source. No change needed.
3. **Mermaid render limits:** Each diagram is scoped to one concern to avoid oversized single charts. If a subsection grows (e.g. many more API routes), consider splitting into sub-subsections.
4. **Console routes:** All console routes from router/index.js are represented in Level 5.2; Blog and CSV search are included. No gaps identified.
5. **Server routes:** All API routes from server.js are represented in Level 5.3; webhook is under Billing. No gaps identified.

No code or behavior changes were required; the deliverable is additive documentation.

## Second-iteration review

- **Cross-references:** Each section has "Above" / "Next" links to adjacent levels; master tree links to Level 0–5 and Changes mapping. Navigation is consistent.
- **TTB flow:** Level 3.6 and Level 4.2 align with ttb-beer-ledger-design.md and TTB-BEER-LEDGER-IMPLEMENTATION-LOG.md (beer-as-items, RECEIVE, forced milestone, location stage, TTBFormService, TTBPDFExportService).
- **Billing flow:** Level 3.3 and Level 4.3 align with single-tier billing, webhook, sync propagation, and router guard; portal-return and success-redirect are in Level 5.3.
- **Changes mapping:** Entries cover vessel-split, batch-detail, billing, TTB, milestone duplicate fix, brewery name, gap detection, removal purpose, production-readiness pass, par-levels, landing, blog, sync. Any new change doc that touches architecture can be added to the table.

No further implementation changes; documentation is complete.

## Integration with analysis.md

analysis.md has been updated to reference the new diagram document under documentation/architecture so future readers know where to find the full systems and implementation diagram.
