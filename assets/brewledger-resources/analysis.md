# BrewLedger - Systems Engineering Analysis

## Executive Summary

BrewLedger (formerly Brewster) is a local-first brewery inventory management application designed for offline operation with multi-device synchronization capabilities. The repository is organized into two main sections: **server** (backend API) and **platforms** (client applications). The **platforms** directory contains a Capacitor mobile app (iOS/Android) and a desktop web application, both sharing the same backend. The system implements a sophisticated architecture that balances client-side autonomy with server-side coordination, featuring comprehensive inventory tracking, batch management, billing integration, and real-time sync across devices.

## Repository Structure

The BrewLedger repository is organized into two main directories:

```
brewledger/
├── blogrip/                    # Standalone blog software (generic, not connected to main app)
│   ├── server.js               # Express entry point
│   ├── config.js               # Site name, base URL, sections
│   ├── content/blog/           # Markdown posts
│   ├── routes/blog.js          # /blog, /blog/section/:key, /blog/:slug, /sitemap.xml
│   ├── services/blog.js       # Post loading, markdown rendering
│   └── templates/blog-layout.js
│
├── server/                     # Backend API
│   ├── server.js               # Express.js application
│   ├── init_db.js              # Database initialization
│   ├── migrate_*.js            # Schema migration scripts
│   └── ...                     # Utilities, Stripe config, etc.
│
└── platforms/                  # Client applications
    ├── brewledger-app/         # Capacitor 6 mobile app (iOS/Android)
    │   ├── src/                # Vue.js 3 app with repositories, views, services
    │   ├── android/            # Android native project
    │   ├── ios/                # iOS native project
    │   └── capacitor.config.json
    │
    └── console/                # Desktop web application
        ├── src/                # Vue.js 3 SPA with desktop-optimized UI
        └── ...
```

Both `platforms/brewledger-app/` and `platforms/console/` share the same backend API in `server/`, the same sync protocol, authentication, and business logic.

#### Blogrip (Standalone Blog Software):
- **Purpose**: Generic, self-contained server-side blog—replica of BrewLedger's blog server logic, not connected to the main application.
- **Location**: `blogrip/` at repository root
- **Technology**: Express.js + marked; no database, no SPA
- **Content**: Markdown files in `content/blog/` with YAML frontmatter
- **Routes**: `/` (→/blog), `/blog`, `/blog/section/:key`, `/blog/:slug`, `/sitemap.xml`
- **Configuration**: `config.js` or env vars (`PORT`, `BASE_URL`, `SITE_NAME`, `SITE_TAGLINE`, `sections`)
- **Features**: Sections, cover story, popular/in-focus sidebars, dynamic sitemap
- **Usage**: `cd blogrip && npm install && npm start`; default port 3080

## System Architecture Overview

### Technology Stack
- **Mobile App** (`platforms/brewledger-app/`): Vue.js 3 + Vite + Tailwind CSS + Dexie.js (IndexedDB) + Capacitor 6 (iOS/Android)
- **Desktop App** (`platforms/console/`): Vue.js 3 SPA (desktop-optimized) + shared backend API
- **Backend** (`server/`): Express.js + SQLite + Stripe API (shared between mobile and desktop platforms)
- **Database**: SQLite (server) + IndexedDB (client)
- **Authentication**: JWT-like token-based auth with bcrypt password hashing
- **Sync Protocol**: Operation-based sync with optimistic locking
- **Testing**: Vitest + Supertest (backend) + Vue Test Utils (frontend)

### Core Design Philosophy
- **Local-First Architecture**: Client as source of truth with offline capability
- **Operation-Based Sync**: Append-only operation log for conflict resolution
- **Server Authoritative**: Final consistency with server as conflict resolver
- **Multi-Platform Strategy**: Capacitor mobile app (iOS/Android) + desktop web app sharing single backend
- **Shared Backend Architecture**: Single backend server (`server/`) serving both mobile and desktop platforms

## System Components Analysis

### 0. Multi-Platform Architecture & Repository Structure

#### Repository Layout:
- **`server/`**: Express.js backend API (SQLite, Stripe, auth, sync)
- **`platforms/brewledger-app/`**: Capacitor 6 mobile app (Vue.js 3, iOS/Android)
- **`platforms/console/`**: Desktop web application (Vue.js 3 SPA)

#### Console App Overview:
- **Purpose**: Desktop-optimized management interface for brewery operations
- **Technology**: Vue.js 3 SPA with desktop-optimized UI components
- **Location**: `platforms/console/`
- **Backend Integration**: Shares `server/` backend with mobile app
- **Deployment**: Separate Vite build on port 5174 (mobile app on 5173)

#### Migration Strategy:
- **Single Backend Approach**: Both platforms share the backend in `server/`
- **Shared API Configuration**: Both apps use same API_BASE_URL (`http://localhost:3000/api`)
- **Component Architecture**: Desktop-optimized components with sidebar navigation
- **Feature Parity**: Console app provides enhanced desktop features while sharing core business logic

#### Console App Features:
- **Desktop-Optimized UI**: Sidebar navigation, data tables, multi-column layouts
- **Advanced Reporting**: Comprehensive analytics and report generation
- **Bulk Operations**: Mass inventory updates and batch processing
- **Real-time Monitoring**: Enhanced dashboard with live metrics
- **Shared Authentication**: Single sign-on across mobile and console apps
 - **AI Assistant (hands-on helper)**: Console AI view uses `/api/ai/chat` with OpenRouter; server parses JSON action payloads (intents: `set_par_level`, `adjust_onhand`, `record_batch_reading`, `adjust_batch_volume`, `forecast_item`). Frontend renders action cards and executes via `AssistantActionExecutor` using ParLevelRepository, LedgerRepository, BatchReadingRepository, BatchVolumeAdjustmentRepository, BatchLocationRepository, BatchRepository; sync guard via SyncService. Forecast uses recent negative ledger quantities (including CONSUME/TRANSFER_OUT) over a clamped 1–180 day window (30-day default) to project depletion against on-hand cache.
 - **AI Assistant UI (widescreen)**: Desktop assistant page uses a wide interactive layout within the console chrome (header/sidebar intact), taller viewport (`calc(100vh - 180px)`), compact padding, and tool badges. Input footer is separated with subtle background; message cards have light borders/shadows for tool-like affordance.
 - **AI Assistant inline inputs**: When the executor returns a “need_*” that requires user-entered text or numbers, the action card shows inline form fields instead of only a message. Per-card form state is stored in `actionStatuses[index].form` and merged into the action params on “Approve & run”. Supported: **need_item_name** (text input for name, category dropdown, plus optional “pick existing item” buttons), **need_location_name** (text input for location name), **need_quantity** / **need_volume** / **need_packaging_volume** (number inputs). This ensures the chat prompts and gives the user a chance to input before proceeding.

#### Desktop UI Design System (2026):
- **Refined Visual Design**: Polished desktop interface with enhanced typography, spacing, shadows, and visual hierarchy
- **Global Styles**: Enhanced `style.css` with desktop-optimized components including `.card`, `.stat-card`, `.data-table`, `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-success`, `.input`, `.badge` classes
- **Sidebar Navigation**: Refined 280px sidebar with improved logo presentation and navigation items with hover states. User/brewery name, dark mode toggle, and logout moved: user/brewery displayed on Dashboard only (near top, subtle); logout and dark mode in Settings (General tab). Sidebar footer removed.
- **Header Bar**: Sticky header with backdrop blur, refined typography, and sync status indicator
- **Console toolbar & pills (2026-02-11 refresh)**: Added shared `.console-toolbar`, filter pills, stat trend/meta chips, and compact list/table utilities to keep the existing palette while improving hierarchy, density, and clarity across Dashboard and Analytics views.
- **Removals UI refresh (2026-02-11)**: Beer Removals now uses a toolbar with TTB context, paired grid layouts for removal and in-bond forms, available-quantity meta pill, and a capped recent removals table in a card to avoid full-width scrolling.
- **Items list card refresh (2026-02-11)**: Items view now uses responsive card grids for Ingredients and Finished Beer with on-hand totals (aggregated via `LedgerRepository.getAllOnhand`), estimated value when `default_unit_cost` is set, unit/category pills, and in-card edit CTAs to reduce scrolling and match modern card aesthetic.
- **Vendor item-centric flow (2026-02-23)**: Vendor is set on items via ItemForm (console + mobile) and derived per line in Receive. No per-receipt vendor input; each RECEIVE ledger entry gets vendor from its item. Inventory view already shows item.vendor. **init_db**: Removed legacy `item_templates` CREATE/ALTER—no UI uses it; new DBs won't create the table. Feature analysis: `changes/vendor-item-centric-flow.md`.
- **Mobile registration no seed (2026-02-23)**: Mobile `Register.vue` no longer calls `seedData()` after organization registration. New orgs start empty (sync fetches server-side categories, milestone template). Aligns with desktop console. Demo mode (`Login.vue` demoMode) still uses seed. Feature analysis: `changes/mobile-registration-no-seed.md`.
- **Items list sorting, view mode, and category color (2026-02-13)**: Console Items view (`ItemsList.vue`) adds a toolbar with search, sort dropdown (Name A–Z/Z–A, On hand high/low, Value high/low, Category), and list/grid view toggle. **List view** (default): single compressed data table (Name, Category, Unit, On hand, Est. value, Edit) for all items with category-colored pills and icon backgrounds. **Grid view**: existing card layout with category-colored left border and pills (same palette as Inventory.vue: Finished Beer, Hops, Grains, Yeast, Chemicals, Packaging, Clarifiers, Other). Feature analysis: `changes/items-list-sorting-view-category.md`.
- **Batches page refresh (2026-02-11)**: Batches list now has a toolbar with search, count context, richer cards (metadata pills for date/volume/vessels, capped vessel pills) and inline relative-updated hints; legacy status badges/progress were removed to avoid implying workflow states no longer used.
- **Batches list: Finished section (2026-02-16)**: Once a batch is marked production complete (RECEIVE with `data.source === 'production_complete'`), it appears in a separate **Finished** section on the Batches list (console and mobile). Console: "In progress" and "Finished" sections with count; finished cards use success/green styling and a "Production complete" pill. Mobile: same two sections with "In progress" and "Finished" headings; finished batches show green left border and "Complete" badge. `LedgerRepository.getProductionCompleteBatchIds()` returns batch IDs that have a production-complete RECEIVE entry.
- **Dashboard View**: Enhanced stat cards with gradient backgrounds, improved grid layouts, refined inventory and low stock sections with better scrolling, and polished batch visualization cards
- **Dashboard additions (2026-02-12)**: Quick Actions card (receive, consume, transfer, removals, losses, ledger), vessel overview (active batch locations only, status/volume, default unit `bbl`), serving summary (server-backed with local fallback), TTB compliance card with current-month window, recent activity feed, and Top Inventory estimated value (uses `default_unit_cost`). Removed unused location scope pills; date range pills now power serving/activity windows. Racking removed (2026-03-01) — packaging now via Mark Production Complete. **Active Batches milestone progress section removed (2026-03)**: The bottom card with batch tiles and MilestonePieChart per batch was removed; the stat card "Active Batches" count at top remains.
- **Dashboard recent activity styling (2026-02-16)**: Recent activity (ledger preview) on the dashboard now matches the Ledger page UI: transaction type badges (green/orange/blue/neutral by RECEIVE, CONSUME, TRANSFER, etc.) and signed quantity coloring (green for positive, red for negative). Feature analysis: `changes/dashboard-serving-batch-fixes.md`.
- **Dashboard trial banner (console, 2026-02-19)**: When the user is in a trial phase, the console Dashboard shows an alert with days remaining (same as mobile). The entire banner is a single link to Settings → Billing (`/settings?tab=billing`); clicking anywhere on the alert navigates to the Billing tab. Upgrade button is present for visual affordance but the whole card is clickable.
- **Serving page feedback and Set empty (2026-02-16)**: Serving view uses the global modal system for success messages after Set volume and Record removal. New **Set empty** action per tank (when a batch is assigned): reconciles Finished Beer ledger at the tank location to 0 bbl, soft-deletes the batch_location so the tank is available, then refreshes and syncs. Feature analysis: `changes/dashboard-serving-batch-fixes.md`.
- **Serving: one beer per location (2026-02-16)**: Console and mobile enforce **one beer item per serving location** at a time. Occupancy is derived from ledger on-hand (which Finished Beer item has quantity at that location), not from batch_link. **ServingOccupancyService** (`getCurrentBeerAtLocation`, `getBeerItemForServingLocation`) in both console and mobile resolves current beer per location and detects conflicts (multiple beer items with on-hand > 0 at same location). **Production complete**: Serving locations list shows current beer name per location (or "Empty", or "Multiple beers – resolve on Serving page" when conflict); selecting an occupied location opens a confirmation dialog: "Same beer – add on top" (RECEIVE to existing item), "Remove first" (prompt to zero on Serving page), or "Cancel". Conflict locations are disabled. **Serving page**: Set volume, Record removal, and Set empty use the current beer item for that tank's location; actions disabled when no beer or conflict. Set empty zeros the current beer item at the location (no batch_location delete). Mobile has full parity (ServingOccupancyService, BatchDetail confirm dialog, Serving.vue per-tank beer and Set empty). **Console Batch Detail** tank flows (Adjust volume tank, Set volume tank) use per-location beer resolution and conflict/empty handling (review: `changes/serving-finished-beer-review.md`). Feature analysis: `changes/serving-one-beer-per-location.md`.
- **Serving tank & Finished Beer cleanup (2026-02-19)**: **Default Finished Beer item**: New orgs no longer receive a default "Finished Beer" item at registration; the Finished Beer category is still created. Beer items are created per-recipe/per-batch when needed (e.g. Mark Production Complete). **New batches and serving tanks**: New batches cannot be assigned to serving tanks. Console and mobile BatchForm vessel dropdowns exclude serving tanks (vessels with `location_id`); BatchDetail Split/Combine use the same filtered vessel list. Server already rejected batch_location for vessels with a linked location. **Log Reading**: "Overall batch" option removed; a vessel must be selected for each reading (default: first batch location). **Serving tank view**: Console Vessels and mobile VesselsList show ledger-based inventory (beer name + on-hand) for serving tanks via `getCurrentBeerAtLocation`, so when a batch is completed to a tank the view reflects inventory at the location, not the batch. Serving.vue and Vessels.vue use `onActivated` to refresh when returning to the page. Feature analysis: `changes/serving-tank-finished-beer-cleanup.md`.
- **Batch detail not-found (2026-02-16)**: When opening a batch from the Batches list (or direct URL) that does not exist locally, Batch Detail now sets `batchNotFound` and shows the “Batch not found” card instead of a blank page. Route param watch ensures reload when navigating between batch IDs. Feature analysis: `changes/dashboard-serving-batch-fixes.md`.
- **Inventory View**: Sophisticated data table with sticky headers, improved sorting, refined search input, and enhanced expandable rows for location details
- **Ledger View**: Professional transaction table with proper column layout, badge styling for transaction types, and improved readability
- **Batches List**: Refined card-based grid layout with hover effects, better status badges, and improved progress indicators
- **Batch Detail View**: Desktop-optimized layout: hero (batch name, date, volume, status badge), actions toolbar (primary “Log Reading”, secondary Update Status / Add Ingredient / Add Water / Mark Production Complete with `btn-success`), two-column grid (Vessels data table with Split/Transfer; Timeline & History tabs in a card with ARIA tablist/tab/tabpanel). Vessels shown in `.data-table` (Vessel, Volume, Gravity, Temp, pH, Actions); History as table (Date, Event, Details). Uses `.card`, `.data-table`, `.btn`, `.badge`, `.heading-refined`; `btn-success` in `style.css` for milestone actions. Record Packaging button removed (2026-03-01) — packaging now via Mark Production Complete. Feature analysis: `changes/batch-detail-redesign.md`.
- **Par Levels View**: Enhanced form layout with better input controls, improved scope selector, item search (filters by name and category), and refined item list presentation. Search input visible when scope is selected; result count ("Showing X of Y items") when filtering; empty state for no matches; aria-label for accessibility. Feature analysis: `changes/par-levels-item-search.md`.
- **Locations Management (console)**: Desktop console now exposes `/locations` (list/add/edit) with shared `LocationRepository` create/update/delete, stage selection derived from the shared TTB stage set (`cellar`, `serving`, `racking_keg`, `bottling_bulk`, `case`), delete flow clears on-hand via CONSUME like mobile. Navigation entry added under Inventory; SEO titles/descriptions wired; forms guard loading/validation and reuse shared stage labels. **Location form revision (2026-02-27)**: Both console and mobile LocationForm add intro copy ("A location is just a spot in your facility where things are kept"), Yes/No question "Will this location hold any finished beer products?", and conditional TTB stage—only shown when Yes; when No, stage defaults to cellar (bulk). Feature analysis: `changes/location-form-holds-beer-revision.md`.
- **Hide non-serving tank locations in forms (2026-03-04)**: Locations bound to non-serving vessels (fermenters, brites, unitanks) are auto-created for record-keeping (e.g., packaging flow) but should not be user-selectable in forms. Only standalone locations and serving locations (bound to SERVING vessels) appear in location dropdowns. Filter logic: `nonServingTankLocationIds = vessels where location_id AND type !== 'SERVING'`; display `locations.filter(l => !nonServingTankLocationIds.has(l.id))`. **Views updated**: Transfer, Consume, BatchDetail (Add Ingredient From Location, Supply lines), BatchRecipeConsume, Losses, Removals, RemoveBeer, SalesOrder, ItemForm (default location), Count. **Unchanged**: Receive, Par Levels, BatchDetail transfer destination (continue excluding all tank locations). Feature analysis: `changes/hide-non-serving-tank-locations.md`.
- **Standalone Consume and Transfer (console, 2026-02-27)**: Desktop console adds `/consume` and `/transfer` pages, matching mobile app flows. **ConsumeRepository** (`recordConsume`, `getRecentConsumes`) and **TransferRepository** (`recordTransfer`, `getRecentTransfers`) wrap LedgerRepository. Consume: batch + location + item lines with on-hand validation; Transfer: item + from/to locations + quantity + operation type (TTB), with insufficient-stock confirm. Both in Inventory nav and Dashboard Quick Actions. Feature analysis: `changes/standalone-consume-transfer-desktop.md`.
- **Receive Inventory (console)**: New `/receive` view lets desktop users post RECEIVE ledger entries with multiple line items, vendor/invoice/note metadata, undo support, and sync trigger. Form blocks while dependencies load, includes retry on load failure, coerces numeric inputs, and refreshes item/location lists when starting a new receipt. Desktop UI refreshed with console toolbar meta pills (location, lines, estimated total, vendor/invoice), stacked cards for metadata and line items, gated line editing until a location is chosen, and a sticky summary/action card that surfaces vendor/invoice context alongside totals.
- **Receive copy cleanup (2026-02-12)**: Trimmed desktop receive copy (shorter toolbar subtitle and line-item helper, removed low-value helper blurbs, condensed sidebar note) so the form reads faster while keeping vendor/invoice context.
- **Receive desktop fixes (2026-02-12)**: Hides the receive form after confirmation so only the receipt card remains, surfaces vendor/invoice/location in the confirmation summary, and forces an on-hand cache recompute after saving to avoid inventory drift.
- **Receive validation**: Server ledger validation now accepts optional vendor/invoice/unit_cost/total_cost/QBO bill ID fields when they are null or omitted, preventing RECEIVE sync failures from desktop submissions that exclude cost or invoice metadata.
- **Analytics View**: Polished stat cards, refined chart placeholders, and improved KPI cards with better visual hierarchy
- **Reports View (2026-02)**: Placeholder report cards (Inventory, Production, Financial), Custom Report Configuration, Recent Reports table, and Advanced Reporting promo removed. Page shows: TTB Form 5130.9, Beer Removals, Losses (links); Serving & Inventory Rollup (server-backed with local fallback). Racking link removed (2026-03-01) — packaging now via Mark Production Complete. Removals by purpose & tax status and Production volume by batch & location reports were removed (2026-02-19). See `changes/reports-cleanup-implementation.md`, `changes/reports-removals-production-removal.md`.
- **Design Principles**: Consistent use of shadows, rounded corners (xl), refined spacing (gap-5, gap-6), improved typography with `heading-refined` class, and smooth transitions throughout
- **Color System (2026-02-23 warm brewing accent)**: Console primary palette uses amber (`#f59e0b`, `#d97706`, etc.) for accents—buttons, sidebar active, filter pills, focus rings—aligning with the landing page. **No blue**: Blue removed from Settings (tabs, inputs, buttons), Dashboard (stats, quick actions, links), Inventory (table headers, badges), Locations, Items (view toggle), and semantic badges (Transfer, Yeast, batch statuses use slate). Quick actions use `btn-warm` (amber-tinted). Org name and form inputs use `dark:bg-stone-800`. Semantic palettes: success (green), warning (amber), danger (red). **Dark theme**: Beerish warm tones using Tailwind stone; root and main use `dark:bg-stone-950`; avatar, meta-pill, stat-card-icon-neutral use warm vars. Form controls: `dark:bg-stone-800`, `dark:border-stone-600`. Feature analysis: `changes/warm-brewing-accent-beerish-dark-theme.md`.
- **Responsive Design**: Maintains desktop-first approach while ensuring usability across screen sizes
- **Removed unlaunched QuickBooks UI (2026-02-12)**: Accounting/QBO settings tab and QuickBooks marketing claims were removed from `platforms/console` (Landing variants A/B/C) to avoid advertising an integration that is not active; backend endpoints remain but the UI stays hidden until ready.
- **Distribution section and QuickBooks Sales Order (2026-02-28)**: New **Distribution** sidebar group with **Integrations** (`/integrations`) and **Sales Order** (`/sales-order`) views. Integrations: QuickBooks connection (connect, disconnect, manual code/realmId exchange). Sales Order: form to create a Removal Event (CONSUME with `removal_purpose: 'sale'`) with Customer picker (QBO), Finished Beer inventory, location, quantity, wholesale price, and "Create Invoice in QuickBooks?" toggle. Server: `GET /api/integrations/qbo/customers`, `POST /api/integrations/qbo/push/invoice`. QBOService wraps QBO API calls. Ledger entries support `qbo_customer_id`, `qbo_invoice_id`. **Context-aware inventory (2026-02-28)**: When product is selected first, location dropdown shows available quantity per location (e.g. "Cold Storage – 12.00 bbl"); when both product and location are selected, toolbar meta pill and quantity helper show available at that location. `LedgerRepository.getOnhandByItem(itemId)` returns per-location on-hand for dropdown population. **Item mapping (2026-02-28)**: Integrations QuickBooks Online section adds Item Mapping table when connected—map BrewLedger beer items to QuickBooks items (dropdown of existing QBO items or "Create in QuickBooks"). Server: `GET /api/integrations/qbo/items`, `GET/POST /api/integrations/qbo/mappings`, `POST /api/integrations/qbo/items/:id/push`. QBOService: `getMappings`, `getItems`, `saveMapping`, `pushItem`. Sales Order: when Create Invoice checked and selected beer has no mapping, shows hint and disables submit. Feature analysis: `changes/quickbooks-sales-order-implementation.md`, `changes/sales-order-context-aware-inventory.md`, `changes/quickbooks-item-mapping-integrations.md`.

#### Technical Implementation:
- **Project Structure**: `platforms/console/` with Vue 3 SPA architecture
- **Configuration**: Shared `config.js` pointing to backend in `server/`
- **Routing**: Desktop-optimized navigation with persistent sidebar
- **State Management**: Planned Pinia integration for shared state with mobile app
- **Build System**: Separate Vite configuration with desktop-specific optimizations

#### Promotional Landing Page (Default View):
- **Purpose**: Marketing home page for BrewLedger; first experience for new visitors
- **Route**: `/` (default, public); single-page with anchor links
- **Source**: `platforms/console/src/views/Landing.vue`
- **Layout**: Full-width promotional content; no sidebar or app chrome; beer-y, brownish-gold (amber/stone) inviting style
- **Messaging (2026-02-13 refresh)**: Platform-focused—"The operations platform breweries actually want." One place for production, inventory, compliance, and taproom; powerful and versatile; mobile + desktop. Savings/ROI downplayed to a compact Benefits section; no "ERP" in copy; "more affordable" OK, not "cheap." Brewpubs/taprooms and serving costs woven into platform and Workflows copy.
- **Content order**: Hero (minimal: headline, subline, CTAs, “See the platform in action below”) → **See it in action** (#screenshots: large mobile + desktop mockups with carousels) → Platform (#platform) → Benefits (#benefits) → Workflows (#workflows) → Offline → Features / Built for → Pricing (#pricing) → FAQ → Footer CTA
- **Auth Flow**: Authenticated users visiting `/` are redirected to `/dashboard`; unauthenticated users see landing
- **Navigation**: Screens (#screenshots), Platform (#platform), Workflows (#workflows), Pricing (#pricing), Tools (→/tools), Newsletter (→/blog), Login (coming-soon popup)
- **Hero**: Minimal hero—text, CTAs (Book a demo, See the platform → #screenshots), and short pill line; no device mockups in hero. Single centered column; beer-y amber/stone.
- **Screenshots**: **See it in action** (first section below hero): **Mobile** 7 slides `sc1.png`–`sc7.png` in phone mockup (~320px) with prev/next and dots; **Desktop** 3 slides `dc1.png`–`dc3.png` in browser mockup (~600px) with dot indicators. Both in one section; error fallbacks "Screenshot N" / "Desktop N". Placeholder PNGs in `public/screenshots/` and `public/screenshots/desktop/`; replace with real app screenshots as needed.
- **SEO**: Schema.org JSON-LD, canonical URL, Inter font; meta title "BrewLedger – Operations Platform for Breweries" and description in `index.html` and router
- **Analytics**: Ahrefs Web Analytics script loaded on every page (async): `platforms/console/index.html` for SPA routes (landing, dashboard, subscribe, etc.); `server/templates/blog-layout.js` for server-rendered blog routes (`/blog`, `/blog/about`, `/blog/section/:key`, `/blog/:slug`)
- **Landing variants (2026-02-11 power/versatility/ease)**: Three review variants: `Landing_A.vue`, `Landing_B.vue`, `Landing_C.vue` (not used as default; see above for current default content).

#### The Ledger (Console App – News-Site / Publication):
- **Purpose**: Brewing industry and beer news publication—positioned as a trade publication ("The Ledger") rather than a blog, with a focus on operations; supports credibility (e.g. "Featured in The Ledger" badge for breweries).
- **Location**: `platforms/console/` only (mobile app does not include blog)
- **Routes**: `/blog` (front page), `/blog/about`, `/blog/subscribe`, `/blog/section/:sectionKey` (section index), `/blog/:slug` (article); all public (no auth). URLs remain `/blog` for SEO; visible branding is "The Ledger". **About page (server-rendered, 2026-03-08)**: `GET /blog/about` is served by `server/routes/blog.js` with full HTML (newsletter overview, About BrewLedger, Preserving History, Contact, Featured badge). Preserving History section states BrewLedger maintains brewery/winery histories and domains; revived vineyard48winery.com; links to Vineyard 48 blog post. No longer SPA fallthrough; `about` removed from SPA_SLUGS.
- **Layout**: News-site layout—no dashboard sidebar; header with logo + "The Ledger", nav (Home, Operations, Trends, Industry, Best Practices, About, Subscribe), theme toggle, "BrewLedger →"; main + right sidebar (Sections, Popular, Weekly insights, About, Featured badge); **footer** with section links, About, Subscribe, Featured badge, BrewLedger, © year.
- **Content Source**: Markdown files in `platforms/console/src/blog/posts/*.md` with YAML frontmatter.
- **Frontmatter Fields**: `title`, `slug`, `date`, `author`, `excerpt`, `popular` (optional boolean for sidebar), `section` (optional: Operations, Trends, Industry, Best Practices—normalized to URL key), `sandboxCsvUrl` (optional); **Ledger-specific**: `coverStory`, `coverImage`, `coverHeadline`, `authorImage`, `listImage`, `leadImage`, `leadCaption`, `figureImage`, `figureCaption`, `takeaways`, `featured`, `faq` (optional: JSON array of `{question, answer}` or `{q, a}` for FAQ schema; when omitted, auto-derived from H2 headings).
- **Loader**: `src/utils/blogLoader.js`—uses `import.meta.glob`; parses frontmatter; exports `loadAllPosts()`, `loadPost(slug)`, `loadPopularPosts()`, `loadSections()`, `loadPostsBySection(sectionKey)`, `SECTION_LABELS`. Section derived from frontmatter or slug keyword mapping when missing. **Author display**: `author` and `authorImage` taken from frontmatter; when `authorImage` is missing, loader uses `AUTHOR_HEADSHOTS` map (Jack Jusko, Michael Stroener, Kyle Flaci → `/headshots/...`) so byline headshots still show. Frontmatter parsing uses `\r?\n` and skips empty lines for robustness. **Asset URLs**: BlogPost and BlogList use `resolveAssetUrl(path)` so author/cover/list/lead/figure images and logo resolve correctly when the app is served from a non-root base (e.g. subpath deployment). Feature fix: `changes/blog-author-names-pictures-fix.md`.
- **Typography**: Serif font (Merriweather) for headlines in blog layout only (`.ledger-headline`, article h1/h2/h3 in post body); Inter remains for body. Loaded in `index.html`; scoped via `.blog-layout :deep(.ledger-headline)` in App.vue.
- **Front page (BlogList.vue)**: Masthead "The Ledger" with "Brewing industry & beer news · Industry, beer, operations"; **Section quick links** (Operations, Trends, Industry, Best Practices → `/blog/section/:key`); **Cover Story**—one prominent post (first with `coverStory: true` or else latest) with optional `coverImage`, overlay headline, meta (date · author · read time); **In focus**—image strip (grid): posts with `listImage` or `coverImage` (excluding cover) as cards; **Newsletter strip**—full-width CTA "Weekly insights" with "Subscribe →" to `/blog/subscribe`; **Latest**—multi-column TOC list (date | title | author · min). Long titles truncate with full text on hover.
- **Article (BlogPost.vue)**: Compact header: date · read time · author; title; compact byline bar with small headshot (`authorImage`) and author name; **Lead image** slot below header when `leadImage` or `coverImage` is set (full-width, aspect 21/9 or 3/1, optional `leadCaption`); optional **Key Takeaways** box when `takeaways` is set; duplicate h1 stripped; **Prose + figure layout**: MarkdownRenderer with denser body typography; when `figureImage` is set, two-column layout (prose + aside with figure image and optional `figureCaption`; on mobile figure below prose); when post has `sandboxCsvUrl`, renders `CsvSearch` below; when `featured: true`, shows "Featured in The Ledger" badge in header.
- **Markdown rendering**: `MarkdownRenderer.vue` parses post body; supports headers, lists, code blocks, **blockquotes** `> ...` (pull-quote styling in BlogPost), **links** `[text](url)` (open in new tab), and **images** `![alt](url)` (http/https/relative URLs only; lazy-loaded, responsive; URL sanitization prevents XSS).
- **Pull quotes**: `.blog-post-content blockquote` styled as pull quote (Merriweather, larger font, left border, italic) in BlogPost.vue.
<｜tool▁sep｜>path
z:\brewledger\analysis.md
- **Sidebar**: `BlogSidebar.vue`—**Sections** (Operations, Trends, Industry, Best Practices → `/blog/section/:key`), **Popular** (from `popular: true`), **Weekly insights** ("Subscribe →" to `/blog/subscribe`), **About** (blurb + "About The Ledger →" to `/blog/about`, "BrewLedger →" to `/`), "Featured in The Ledger" badge (links to /blog). Sticky on desktop; below main on mobile.
- **Newsletter URL**: `LEDGER_NEWSLETTER_URL` in `config.js` (default `https://getbrewledger.com/#subscribe`) for The Ledger's own newsletter/signup; update to your list or signup page.
- **Featured badge**: Reusable "Featured in The Ledger" badge—inline in sidebar and on article when `featured: true`; asset at `public/featured-in-the-ledger.svg` for external use (breweries can link to their article or The Ledger).
- **SEO**: Per-page canonical URLs via `@vueuse/head`; meta descriptions and titles reference "The Ledger"; `SITE_BASE_URL` in config.js (https://getbrewledger.com); each post has unique canonical. **Meta description**: from frontmatter `excerpt` or auto-derived from first paragraph via `excerptFromBody`. **Article JSON-LD**: `BlogPosting` schema injected for every article (headline, author, datePublished, dateModified, publisher, image, description, url). **FAQ JSON-LD**: When `faq` in frontmatter (JSON array of `{question, answer}`) or when omitted, auto-derived from H2 headings (each ## becomes a question, following content the answer); schema.org FAQPage injected via useHead script. **Post titles** are optimized for CTR and SEO: primary keywords near the front, benefit/outcome clarity, year where relevant (e.g. "2025"), and "How to" / guide-style phrasing; H1 in each post body matches frontmatter `title`.
- **Sitemap**: GET `/sitemap.xml` generated dynamically by server (`server/routes/blog.js`). Includes /, /blog, /blog/about, /blog/subscribe, /blog/section/*, /tools, /tools/bbl-to-case, /tools/csv-search, and all blog posts from `server/content/blog/`. Base URL from `APP_BASE_URL` or `RESET_BASE_URL`. Static `platforms/console/public/sitemap.xml` exists as fallback when server not used.
- **Server blog Article JSON-LD**: When serving a single post (`GET /blog/:slug`), `server/templates/blog-layout.js` injects `BlogPosting` schema (headline, author, datePublished, dateModified, publisher, image, description, url) via `options.articleSchema` from `server/routes/blog.js`. WebSite schema remains for all pages; article pages get both.
- **Navigation**: The Ledger link on Landing nav (→/blog); Tools link on Landing and blog header; no blog link in authenticated dashboard sidebar.
- **Auth**: Blog routes use `requiresAuth: false`; router guard allows authenticated users to view blog without redirect.
- **Feature Analysis**: `changes/blog-system-analysis.md`, `changes/the-ledger-rebrand.md`, `changes/blog-layout-dense-wsj-style.md`, `changes/ledger-news-site-redesign.md`, `changes/ledger-theme-brewing-industry-beer-news.md`, `changes/murree-brewery-pakistan-export-blog-post.md`, `changes/beer-guys-carolinas-blog-post.md`, `changes/guinness-st-patricks-day-2026-blog-post.md`, `changes/steelhead-brewing-eugene-closing-legacy-blog-post.md`, `changes/city-brewing-50-million-loan-blog-post.md`, `changes/unfused-brew-hall-canton-blog-post.md`, `changes/brewery-management-software-comparison-2026-blog-post.md`, `changes/vineyard-48-blog-post.md`, `changes/dangerous-man-headflyer-taproom-takeover-blog-post.md`, `changes/nc-beer-march-2026-blog-post.md`, `changes/george-clooney-crazy-mountain-blog-post.md`, `changes/best-irish-beers-st-patricks-day-2026-blog-post.md`, `changes/upland-brewing-company-indiana-blog-post.md`, `changes/olfactory-brewing-bankruptcy-blog-post.md`, `changes/heineken-6000-jobs-blog-post.md`, `changes/beer-cooler-packaging-decisions-meta-analysis-blog-post.md`
- **Dual content locations**: Blog posts exist in both `server/content/blog/` (server sitemap, SSR) and `platforms/console/src/blog/posts/` (console SPA, Vite glob). Edits must be applied to both. Examples: HeadFlyer taproom closure, Purpose Brew Works Ohio opening, best breweries to watch 2026 (2026-02-27), Murree Brewery Pakistan export (2026-02-01, server-only), Beer Guys Carolinas (2026-03-04), Guinness St. Patrick's Day 2026 PopUp Bagels (2026-03-04), Steelhead Brewing Eugene closing (2026-03-04), City Brewing $50M loan (2026-03-04), Unfused Brew Hall Canton (2026-03-04), best breweries Chesterland Ohio (2026-03-05, server-only), brewery management software comparison 2026 (2026-03-05), Vineyard 48 winery history (2026-03-08, server-only), Dangerous Man / HeadFlyer taproom takeover (2026-03-09), NC Beer March 2026 spring events (2026-03-09), George Clooney Crazy Mountain NA beer (2026-03-09), best Irish beers St. Patrick's Day 2026 (2026-03-09), shandy guide (2026-03-09), porter beer guide (2026-03-09), Olfactory Brewing Chapter 7 bankruptcy (2026-03-11), Heineken 6,000 jobs weak beer demand (2026-03-11), whiskey ginger ale guide (2026-03-09), Upland Brewing Company Indiana history/sours/Champagne Velvet (2026-03-09, server-only), beer cooler packaging decisions meta-analysis 2026 (2026-05-17; BA + Quad + trade synthesis, backlinks New School Beer); feature analyses in `changes/`.
- **User guide posts (server-only, 2026-03-05)**: Onboarding posts in `server/content/blog/`: **What is BrewLedger?** (`what-is-brewledger`)—index/overview of the platform, Ledger, interconnected design, mobile app; links to Brewer's Quick Start and Batch Tracking Quick Start. **Brewer's Quick Start** (`brewers-quick-start`)—setup guide for Locations, Items, Receive, Beers, Transfer, Par Levels; links to What is BrewLedger and Batch Tracking Quick Start. **Batch Tracking Quick Start** (`batch-tracking-quick-start`)—batches as primary brewing-process tracker; starting batches (manual/template), milestone templates, ingredient additions, tank readings, split/transfer, Mark Production Complete (serving, keg, can/bottle). All use `section: best-practices`; Brewer's Quick Start has `popular: true`. Server-only per design; no console SPA copies. Feature analysis: `changes/brewledger-user-guide-blog-posts.md`, `changes/batch-tracking-quick-start-blog-post.md`.
- **Vineyard 48 downfall (server-only, 2026-03-08)**: Industry post `vineyard-48-winery-history` in `server/content/blog/`—cautionary B2B case study: "The Downfall of Vineyard 48: Why Compliance, Sales Tracking, and Crowd Management Matter for Wineries." Uses Vineyard 48's 2017 closure (SLA license suspension, 400 disorderly patrons, over-serving) as object lesson. Pitches BrewLedger: removal tracking for sales velocity/over-serving visibility, TTB-ready paper trail, inventory discipline. Cover image: Cutchogue vineyard (Wikimedia Commons, CC BY 2.0). Linked from About page Preserving History section. Feature analysis: `changes/vineyard-48-blog-post.md`.

#### Brewery Tools (Console App – Standalone Section):
- **Purpose**: Free utilities for production managers and brewery operators; separate from the blog and main app; no login required.
- **Location**: `platforms/console/src/views/tools/`; routes under `/tools/`.
- **Layout**: Dedicated `isTools` layout in App.vue—header (logo + "Tools", nav: All tools, BBL to Case, CSV Search; theme toggle; The Ledger →, BrewLedger →), main content, footer (Tools, The Ledger, BrewLedger, © year). Uses `ledger-beer` theme for visual consistency.
- **Routes**: `/tools` (index listing all tools), `/tools/bbl-to-case`, `/tools/csv-search`; all `meta: { requiresAuth: false, isTools: true }`.
- **Auth**: Router guard allows authenticated users to access tools without redirect (same as blog).
- **BBL to Case Converter** (`BblToCase.vue`): Production pack-out calculator with (1) **loss & yield**—yield % slider (default 95%), theoretical max vs realistic pack-out; (2) **expanded formats**—24-pack, 6-pack, 16oz 4-pack, 19.2oz stovepipe (6-pack), 750ml bottle, 1/2 BBL keg, 1/6 BBL sixtel; (3) **split batch**—allocate BBL to multiple formats; (4) **materials estimator**—cans, lids, flats/carriers (and bottles for 750ml); (5) **revenue estimator**—wholesale price per case/keg, total potential revenue; (6) **comparison table**—what-if matrix of theoretical vs realistic by format.
- **CSV Search** (`CsvSearch.vue`): Minimal CSV viewer. Load CSV from URL or file upload; delimiter auto-detect (comma, semicolon, tab). Searchable table display. Supports `?url=...` and `?q=...` query params for direct links (e.g. from blog posts). Blog posts link to `/tools/csv-search?url=/bsg-inventory.csv` or `/sample-cellar-log.csv` instead of embedding.
- **Tools Index** (`ToolsIndex.vue`): Grid of tool cards linking to each utility.
- **Navigation**: Tools link on Landing nav; Tools link in blog header. Tools footer links to The Ledger and BrewLedger.
- **Sitemap**: `/tools`, `/tools/bbl-to-case`, `/tools/csv-search` included in dynamic sitemap (see above).
- **Prerender**: `vite-plugin-prerender-esm-fix` in `vite.config.js` prerenders `/tools`, `/tools/bbl-to-case`, `/tools/csv-search` (10s wait; no blog routes—blog is server-rendered).
- **Tools SEO**: App.vue `useHead` sets meta description and og:title/og:description for tools paths from `seoDescriptions` map (same pattern as blog excerpt—auto-generated/curated per page).

### 1. Error Handling & Resilience System

#### Error Handling Patterns:
- **Frontend Error Handling**: Try-catch blocks in async operations with modal notifications
- **Backend Error Handling**: HTTP status codes with JSON error responses; global error middleware in `server/server.js` catches unhandled errors passed via `next(err)` and returns 500 with a generic message; route-level try/catch used throughout
- **Sync Error Recovery**: Failed syncs retry on next interval with error logging
- **Database Error Handling**: SQLite error catching with graceful degradation
- **Auth Middleware**: Catch block returns `res.status(500).json(...)` to avoid double-send; all error paths use `return` where applicable

#### Error Recovery Mechanisms:
- **Token Expiration**: Automatic logout and redirect to login page
- **Sync Failures**: Queue preservation with exponential backoff (planned)
- **Database Corruption**: IndexedDB reset capability via `resetDatabase()` function
- **Network Errors**: Offline operation with pending changes queue

#### User Feedback System:
- **Modal Dialogs**: `useModal()` composable for alerts and confirmations
- **Toast Notifications**: Not implemented (potential enhancement)
- **Form Validation**: Inline error messages with field highlighting
- **Loading States**: Sync status indicators and button disabling

#### Server Error Handling & Billing Hardening:
- **Overview**: `changes/server-error-handling-billing-overview.md` documents error-handling patterns and billing fixes in `server/server.js`
- **Global error handler**: Four-argument middleware at end of chain logs and returns generic 500 response
- **Billing**: cancel-subscription validates org exists (404 if not); create-portal-session uses Stripe default portal; invoice.payment_failed webhook sets org to `past_due` and logs; billing routes return generic user-facing error messages and log details server-side

### 2. Configuration & Environment Management

#### Configuration Layers:
- **Frontend Configuration**: `config.js` with API base URL
- **Backend Configuration**: Environment variables loaded from root `.env` via `dotenv` (see Secret Management). Server and scripts resolve `.env` from repo root (`path.resolve(__dirname, '..', '.env')`).
- **Build Configuration**: Vite config with Vue plugin and test setup
- **Test Configuration**: Separate configs for frontend (`vitest.config.js`) and backend (`vitest.backend.config.js`)

#### Environment-Specific Settings:
- **Development**: Localhost URLs, test Stripe keys (set in `.env`)
- **Production**: Domain-based API URLs, live Stripe keys in `.env`
- **Testing**: Mocked localStorage, fake IndexedDB, test database files

#### Secret Management:
- **Source of truth**: All server secrets and keys are read from environment variables; no plaintext secrets in code. Root `.env` (gitignored) holds values; server and standalone scripts (`create_portal_config.cjs`, `check_stripe.cjs`, `process_csv_items.js`) load it via `require('dotenv').config({ path: ... })`.
- **Stripe**: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID`. If `STRIPE_SECRET_KEY` is unset, Stripe client is null and billing/webhook routes return 503.
- **OpenRouter (AI)**: `OPENROUTER_API_KEY`, `OPENROUTER_PRESET` (console chat), `OPENROUTER_PRESET_CSV` (CSV processor), optional `OPENROUTER_HTTP_REFERER`, `OPENROUTER_X_TITLE`.
- **Brave Search**: `BRAVE_SEARCH_API_KEY`, `ENABLE_WEB_SEARCH` (process_csv_items.js).
- **App / URLs**: `APP_DEEP_LINK_SCHEME`, `BILLING_RETURN_BASE_URL`, `RESET_BASE_URL`; optional `PORT`, `DB_PATH`.
- **Master Password (testing)**: `MASTER_PASSWORD` — when set, login accepts this value instead of the user's real password for any account. Use for admin testing only; do not set in production.
- **AWS SES**: `AWS_SES_REGION`, `AWS_SES_ACCESS_KEY_ID`, `AWS_SES_SECRET_ACCESS_KEY`, `AWS_SES_FROM_EMAIL` (see mailer.js).
- **QBO**: `QBO_CLIENT_ID`, `QBO_CLIENT_SECRET`, `QBO_REDIRECT_URI`, `QBO_AUTH_URL`, `QBO_TOKEN_URL`, `QBO_API_BASE_URL` (optional).
- **Feature analysis**: `changes/env-secret-extraction.md`.

### 3. Testing & Quality Assurance Architecture

#### Test Strategy:
- **Unit Tests**: Repository methods with mocked dependencies
- **Integration Tests**: API endpoints with test database
- **Component Tests**: Vue components with test utilities
- **Schema Tests**: Database structure validation

#### Test Infrastructure:
- **Frontend Test Setup**: JSDOM environment with fake IndexedDB
- **Backend Test Setup**: Node environment with test SQLite files
- **Mock System**: Comprehensive mocking of external services (Stripe, AuthService)
- **Test Data Management**: Isolated test databases with cleanup

#### Test Coverage Areas:
- **Data Integrity**: Ledger calculations and cache consistency
- **Business Logic**: Location limits, subscription enforcement
- **API Contracts**: Request/response validation and error cases
- **Sync Logic**: Conflict resolution and offline operation

### 4. Development Tools & Utilities

#### Code Quality Tools:
- **ESLint**: Not configured (potential enhancement)
- **Prettier**: Not configured (potential enhancement)
- **TypeScript**: Not used (JavaScript with JSDoc comments)
- **Editor Config**: `.vscode/extensions.json` for recommended VS Code extensions

#### Development Utilities:
- **Database Migration Scripts**: `migrate_billing.js`, `migrate_location_limit.js`, `migrate_ledger.js`, `migrate_max_locations_100.js` (single-tier billing: set all orgs max_locations to 100)
- **Seed Test Account**: `server/seed_test_account.js` creates a test org (test2@brewledger.local / Jack0990) with workflow-realistic seed data: 16 ingredient items across locations, 3 per-batch beer items (House IPA, Pale Ale, Stout), 6 locations, 7 vessels, 5 batches (3 finished with production complete RECEIVEs at Taproom/Keg Storage/Brewery Cellar, 2 active in FV-2/FV-3), batch_readings, batch_additions with CONSUME-ledger inventory reduction. Does not create the default "Finished Beer" item; beer items are per-batch. Use `--force` to clear and re-seed. Feature analysis: `changes/seed-test-account-enhancement.md`.
- **Backfill Scripts**: `backfill_trials.js` for trial period management; `migrate_backfill_vessel_locations.js` to (1) create and link locations for vessels without `location_id` (legacy fermenters, brites, serving tanks), (2) create default packaging items ("Empty 1/6th bbl keg", "Empty 1/2 bbl keg") for all existing orgs. Idempotent; supports `DRY_RUN=1`. New orgs receive these items at registration (server.js register-org). Feature analysis: `changes/vessel-location-backfill-migration.md`.
- **Stripe Utilities**: `check_stripe.cjs`, `create_portal_config.cjs` for Stripe configuration
- **Theme Migration**: `add-dark-mode.cjs`, `add-dark-mode.js` for dark mode class conversion

#### Debugging & Monitoring:
- **Console Logging**: Extensive console.log and console.error throughout codebase
- **Error Tracking**: Basic error logging without centralized error tracking
- **Performance Monitoring**: No application performance monitoring implemented
- **User Analytics**: No user behavior tracking or analytics

#### Documentation:
- **Code Comments**: Moderate commenting with some detailed explanations
- **API Documentation**: No OpenAPI/Swagger documentation
- **Architecture Documentation**: Basic README with setup instructions; full systems and implementation diagram (layered tree from system context to UI/API map) in `docs/SYSTEMS-AND-IMPLEMENTATION-DIAGRAM.md`; feature analysis in `changes/systems-implementation-diagram.md`.
- **Database Schema**: `database_schema.dbml` for visual schema representation

### 5. Build & Deployment System

#### Build Pipeline:
- **Frontend Build**: Vite with Vue plugin, Tailwind CSS processing
- **Backend Preparation**: No compilation, direct Node.js execution
- **Asset Optimization**: CSS minification, JavaScript bundling
- **Environment Injection**: Static configuration at build time

#### Deployment Considerations:
- **Static Frontend**: Can be served from any web server (NGINX, Apache, CDN)
- **Backend Server**: Requires Node.js runtime with SQLite write permissions
- **Database Management**: SQLite file persistence with backup requirements
- **Reverse Proxy**: Recommended for production (Caddy, NGINX)
- **SPA Fallback (Express)**: When serving the console app from an Express public folder, add a fallback route *after* API routes and `express.static` so client-side routes (e.g. `/blog`, `/blog/:slug`) work on refresh/direct visit. Use `app.get('/{*path}', (req, res) => res.sendFile(path.join(__dirname, 'public', 'index.html')))` or regex `app.get(/^\/(?!api)/, ...)`. Express 5+ rejects `'*'` (PathError); use `/{*path}` or regex instead.

#### Operational Requirements:
- **Runtime Dependencies**: Node.js, modern browser with IndexedDB support
- **Storage Requirements**: SQLite file storage, browser IndexedDB quota
- **Network Requirements**: HTTPS for Stripe webhooks, CORS configuration
- **Monitoring**: Basic console logging (enhancement needed for production)

### 6. Authentication & Authorization System

#### Components:
- **AuthService.js**: Client-side session management with localStorage
- **server.js auth routes**: Registration, login, token validation
- **Session Management**: 7-day token expiration with automatic cleanup
- **Role-Based Access**: Admin/user roles with organization-level permissions

#### Key Features:
- Organization registration with admin user creation
- Multi-user invitation system (admin-only)
- Token-based authentication with middleware protection
- Subscription status validation in router guards
- **Master password (testing)**: When `MASTER_PASSWORD` env var is set, login accepts it in place of any user's password. For admin testing only; do not set in production.

#### Data Flow:
1. User credentials → bcrypt hash → SQLite storage
2. Successful auth → token generation → localStorage + SQLite sessions table
3. Subsequent requests → token validation → session lookup → org/user context

#### AWS SES transactional email (welcome, invite, password reset):
- **Mailer**: `server/email/mailer.js` uses AWS SDK v3 (`@aws-sdk/client-ses`). Env: `AWS_SES_REGION`, `AWS_SES_ACCESS_KEY_ID`, `AWS_SES_SECRET_ACCESS_KEY`, `AWS_SES_FROM_EMAIL`. Email failures are logged only; auth responses are never blocked.
- **Templates**: `server/email/templates.js` provides welcome, invite, and reset-password (text + HTML).
- **Welcome**: After successful `/api/auth/register-org`, a welcome email is sent to the registering user (name, org name).
- **Invite**: After successful `/api/auth/invite`, an email is sent to the invited user with org name, temporary password, and login URL. Login URL derived from `RESET_BASE_URL` (base without `/reset`) or placeholder.
- **Password reset**: Table `password_resets` in `server/init_db.js` (id, user_id, token, expires_at, used_at, created_at). `server/auth/resetService.js`: createResetTokenForUser (1h expiry), validateResetToken, markTokenUsed.
  - `POST /api/auth/request-password-reset` (rate-limited): body `{ email }`. Always returns 200 with generic message; if user exists, creates token and sends email with link. Reset link base: env `RESET_BASE_URL` (server reads it once into a module-level constant); fallback `https://app.example.com/reset`; link format `{base}?token=...`.
  - `POST /api/auth/reset-password` (rate-limited): body `{ token, newPassword }`. Validates token (exists, not used, not expired), updates user password, marks token used; 400 generic on invalid/expired.
- **Console UX**: Login has "Forgot password?" → `/forgot-password` (request reset form). `/reset?token=...` shows new-password + confirm form; AuthService.requestPasswordReset(email), AuthService.resetPassword(token, newPassword). Success redirects to login.
- **Delete Account (Compliance)**: Soft delete for user accounts to meet compliance requirements.
  - **Database**: `users.deleted` column (`INTEGER DEFAULT 0`), added via idempotent `ALTER` in `init_db.js` (no migration script).
  - **Endpoint**: `POST /api/auth/delete-account` (auth required). Sets `users.deleted = 1` for current user, deletes all sessions for that user, returns `200 { message: 'Account deleted' }`.
  - **Login rejection**: When `user.deleted` is set, login returns 401 "Invalid credentials" (same as wrong password).
  - **Auth middleware**: Validates user is not deleted on each request; deleted users receive 401 "Invalid or expired token".
  - **Exclusions**: GET /api/users excludes deleted users; request-password-reset skips deleted accounts; reset-password rejects when user is deleted.
  - **Desktop**: Settings → General tab has "Delete account" section with confirmation modal; on success clears session and redirects to /login.
  - **Mobile**: Settings page has "Delete account" section with confirmation modal; on success clears session and redirects to /login.

### 7. Data Storage & Persistence System

#### Dual Database Architecture:
- **Client-side (IndexedDB via Dexie.js)**:
  - Versioned schema (v12; v10 base, v11 adds batch_locations, v12 adds batch_volume_adjustments)
  - 19 entity tables with sync_status tracking (includes batch_locations, batch_volume_adjustments)
  - On-hand cache for performance optimization
  - Transaction support for data integrity

- **Server-side (SQLite)**:
  - Similar table structure with JSON blob storage
  - Server-side onhand_cache for aggregate queries
  - Optimistic locking via version columns
  - Foreign key constraints for referential integrity

#### JSON Blob Storage Pattern:
- Core entity data stored in `data` column as JSON
- Metadata (id, org_id, timestamps, version) as separate columns
- Enables schema flexibility while maintaining relational integrity

### 8. Sync & Replication System

#### Sync Protocol Design:
- **Operation-Based**: Track individual entity changes
- **Bidirectional**: Push local changes, pull server updates
- **Idempotent**: Deduplication by operation ID
- **Optimistic**: Local changes immediately visible

#### Sync Process:
1. **Gather Dirty Records**: Query all tables where `sync_status = 'pending'`
2. **Push to Server**: Send changes batch to `/api/sync` endpoint
3. **Server Processing**:
   - Validation against schema and business rules
   - Optimistic locking conflict resolution
   - Location limit enforcement
   - Cache updates
4. **Pull Updates**: Receive server changes since last sync
5. **Apply Updates**: Merge server changes into local DB
6. **Mark Synced**: Update `sync_status = 'synced'` for sent records

#### Conflict Resolution:
- **Last-Write-Wins**: Based on `updated_at` timestamps
- **Version-Based**: Optimistic locking with version numbers
- **Server Authoritative**: Server wins in case of unresolved conflicts

### 9. Inventory Management System

#### Core Entities:
- **Items**: Brewing ingredients (malt, hops, yeast, etc.)
- **Locations**: Storage areas (grain room, walk-in, etc.)
- **Batches**: Brewing batches with status tracking
- **Vessels**: Brewing equipment (fermenters, brite tanks)

#### Transaction Types:
- **RECEIVE**: Add inventory to location
- **CONSUME**: Remove inventory for batch usage
- **TRANSFER_IN/OUT**: Move inventory between locations
- **COUNT_ADJUST**: Physical count corrections
- **REVERSAL**: Undo previous transactions
- **CORRECTION**: Manual adjustments

#### Ledger System:
- **Append-Only**: Immutable transaction history
- **Double-Entry**: TRANSFER_IN/OUT pairs for moves
- **Snapshot Preservation**: Item/location/batch names stored with entries
- **Cache Optimization**: Real-time on-hand calculations

#### Par Levels (Individual & Global):
- **Individual (Per-Location)**: Minimum quantity for an item at a specific location; breach when `onhand` at that location < `min_qty`
- **Global**: Minimum for total on-hand across all locations; `location_id: null`; breach when `LedgerRepository.getTotalOnhand(itemId)` < `min_qty`
- **Storage**: Same `par_levels` table; global uses `location_id: null`; server `validateEntity` allows null for par_level
- **ParLevelRepository**: `setParLevel`, `setGlobalParLevel`, `getGlobalPars`, `getByItem`, `isGlobalParLevel`
- **Low Stock Logic**: Distinct item count—item breaching both types counts once; uses `LedgerRepository.getOnhand` (individual) and `getTotalOnhand` (global)
- **Mobile**: ReorderList.vue—location selector includes "Global (total across all locations)"; low stock list shows both; LowStock.vue refactored to use ParLevelRepository
- **Console**: Dashboard low stock, Inventory "Manage Par Levels" modal with scope selector; low stock badge on table rows
- **Legacy**: `item.reorder_threshold` deprecated; all views use ParLevelRepository exclusively
- **Sync**: Par levels with `location_id: null` validated and synced like individual pars; no schema migration required
- **Feature Analysis**: `changes/individual-global-par-levels-analysis.md`

#### Vessel Split / Batch Locations (One-to-Many by Volume):
- **Purpose**: One batch’s volume can be split across multiple vessels (one tank → many tanks). Same batch_id; each vessel holds a portion of the total volume.
- **Schema**: New `batch_locations` table/store (server init_db + Dexie v11): id, parent_batch_id, vessel_id, current_volume, created_at; metrics current_gravity, current_ph, current_temp; state status (Fermenting, Crash, Conditioning, Carbonating). Batches: remove single-vessel coupling from create flow; add total_theoretical_volume (sum of all splits); keep planned_volume_unit for display. Legacy vessel_id/planned_volume retained for backfill and list display.
- **BatchRepository**: create() accepts either splits array or legacy vessel_id + planned_volume; creates batch then batch_locations; sets total_theoretical_volume. update() no longer triggers TRANSFERRED milestone on vessel_id change.
- **BatchLocationRepository**: getById, getByBatchId, create, update, delete, setSplitsForBatch (upsert by vessel_id), transferSplit({ sourceBatchLocationId, destinations })—destination volumes are resulting volumes (volume in ≠ volume out allowed); source reduced by sum(destinations.volume), min 0; applyRemoteUpsert. Sync: batch_locations included in SyncService gather/mark/apply and server processChange/fetchUpdates/validateEntity('batch_location').
- **Readings**: batch_readings have optional batch_location_id. Readings can be batch-level or per-vessel; per-vessel readings update that batch_location’s current_gravity/current_ph/current_temp. BatchReadingRepository: getByBatchLocationId, add() accepts batch_location_id.
- **Mobile UI**: BatchForm—vessel splits: default one row (vessel + volume), “+ Add another vessel”, total = sum; save requires at least one vessel with volume. BatchDetail—header shows total volume; vessel cards per batch_location (vessel name, volume, status, gravity/temp/pH); “Log Reading” per card (sets batch_location_id); “Split / Transfer” modal: source batch_location, multiple destination rows (vessel + resulting volume per destination; volumes can differ due to loss or addition; no sum ≤ source check). Legacy backfill: when loading a batch with vessel_id and no batch_locations, create one batch_location and set total_theoretical_volume.
- **BatchesList / BatchRecipeConsume**: Volume display uses total_theoretical_volume ?? planned_volume; scale factor uses same. BatchesList shows which vessels each batch is in and their volumes: loads batch_locations via BatchLocationRepository.getByBatchIds(batchIds), maps vessel names from VesselRepository, and displays a horizontal tree per batch—total volume as root pill, right-chevron connector, then each vessel as a leaf pill (e.g. [75 L] → [FV-1 50 L] [BBT-2 25 L]). BatchLocationRepository.getByBatchIds(batchIds) added for list-view bulk fetch.
- **Volume Adjustments**: New `batch_volume_adjustments` table/store (Dexie v12): logs volume changes per vessel (serving, loss, trub); fields: id, batch_location_id, volume_change (negative for loss), reason, created_at. BatchVolumeAdjustmentRepository: create, getById, getByBatchLocationId, applyRemoteUpsert. Server: validateEntity, processChange, fetchUpdates. UI: "Adjust" button on vessel cards; modal validates new volume ≥ 0; saves adjustment and updates batch_location.current_volume.
- **Serving tanks, setpoints, transfers (2026-02-11)**: Added `serving` location stage (maps to TTB cellar) across server validation, settings/location forms (console/mobile), and TTB column mapping. New `batch_volume_snapshots` table (set-volume snapshots with method/note/recorded_by) auto-derives deltas into `batch_volume_adjustments` (chronological rebuild; rejects negative volume). New `batch_location_transfers` table logs vessel→location/vessel moves with sync. Console & mobile Batch Detail add per-vessel "Set volume" + "Transfer" modals, last-set summary, and sync-backed storage.
- **Serving reports (2026-02-11)**: `ServingReportsService` computes brewed volume by location, monthly inventory deltas (by batch and brand), bulk on-hand by vessel, and packaged on-hand by storage using local ledger/on-hand caches.
- **Serving reports (server-backed UI refresh 2026-02-12)**: Console Reports view prefers the server `/api/reports/serving` endpoint with local fallback, date-range controls with auto-refresh, source badges, and bulk on-hand grouping by inferred vessel location when available. New Vessels view lists vessel → batch → volume with last set-point.
- **Reports cleanup and data-backed reports (2026-02)**: Removed non-functional report cards and Custom Report Configuration from Reports view. Feature analysis: `changes/reports-cleanup-implementation.md`. **Removals and production reports removed (2026-02-19)**: The "Removals by purpose & tax status" and "Production volume by batch & location" report cards, their frontend services (RemovalsReportService, ProductionReportService), and server routes `GET /api/reports/removals` and `GET /api/reports/production` were removed. See `changes/reports-removals-production-removal.md`.
- **Vessel exclusivity guard (2026-02-12)**: Server `validateEntity('batch_location')` rejects assigning a vessel already used by another batch (org-scoped, ignores deleted). Client repositories (mobile + console) enforce the same rule on create/split/transfer/combine via `assertVesselAvailable`, surfacing errors early. Delete sync for `batch_locations` is still absent, so freeing a vessel via delete stays local-only.
- **Vessel occupancy visual (console)**: Vessels view now shows an occupancy card grid listing every vessel (including empty) with batch, status, volume, last set point, and location; the table also includes empty vessels for a full inventory snapshot. The page now supports creating/editing vessels inline via a modal.
- **Vessel actions guard (2026-02-12)**: Desktop Vessels table hides vessel IDs and only renders “Open batch” / “Set volume” when a batch is present (`hasBatch` flag). Empty/unassigned rows surface “No batch assigned” and clear volume/snapshot details to avoid null navigation. Feature analysis: `changes/vessel-actions-no-batch-analysis.md`.
- **Serving tank auto-location (2026-02)**: When **adding** a new serving tank (console and mobile), the location dropdown is removed. A new location is created automatically with `stage: 'serving'` and `name` equal to the tank name, and the new vessel is bound to that location. This ensures one location per serving tank by design and prevents multiple tanks from sharing one location (which caused identical/mirrored data on the Serving page). When **editing** an existing serving tank, the bound location is shown read-only; no new location is created. Feature analysis: `changes/serving-tank-auto-location.md`.
- **Serving tab vessel type filter and display (2026-03)**: Serving tab uses **location-first** logic: one card per serving-stage location. Vessels (type SERVING with `location_id`) are looked up by location; no duplication when tank and auto-created location share the same location. Fermenters and brites with `location_id` are excluded. Feature analysis: `changes/serving-tab-vessel-type-filter.md`.
- **Mark Production Complete location filters (2026-03)**: Serving destination shows only locations with `stage === 'serving'`; fermenters/brites no longer add cellar locations. Packaged (keg/case) destination excludes serving locations (`stage !== 'serving'`). Feature analysis: `changes/production-complete-location-filters.md`.
- **Locations list tank filter (2026-03)**: Locations page hides locations bound to non-serving tanks (fermenters, brites, unitanks). Standalone locations and serving locations (bound to SERVING vessels) remain visible. Feature analysis: `changes/locations-list-tank-filter.md`.
- **Batch location deletes propagate (2026-02-12)**: `batch_locations` tombstones (`deleted_at` + pending sync) now round-trip through sync; server includes them in updates, and client `applyRemoteUpsert` removes local rows so vessel availability frees across devices.
- **Risk fixes (2026-02-11)**: Batch Detail history now surfaces transfers and volume snapshots (console & mobile); transfers can optionally log a Finished Beer RECEIVE ledger entry for packaged pulls. Added server-side `/api/reports/serving` endpoint for long-range brewed/stock rollups (batch/brand/location/vessel) using full server data.
- **Serving, production complete, and TTB Option A (2026-02-12)**: Full implementation per `SERVING_TTB_IMPLEMENTATION_PLAN.md`. **consumption_form**: CONSUME entries support optional `data.consumption_form` ('cellar' | 'keg' | 'case') for TTB Line 21 column (b/d/f). **Line 21**: Includes `removal_purpose === 'serving'` and `'on_premise'`; column breakdown uses consumption_form when present, else location stage. **Removals**: “Served from” dropdown (Cellar/Keg/Case) for Consumption and On-premise. **Vessel location_id**: Only serving vessels have `location_id` (Dexie v15, server validation, Vessels.vue Serving location for type SERVING). **Production complete**: Two-step flow (Serving vs Storage); Serving list = stage serving + tank locations (excluding occupied); Storage = generic locations only; one RECEIVE; one batch per tank enforced. **Transfer**: Destination vessel and location exclude serving tanks (beer only via Mark Production Complete). **Serving-tank exclusivity**: Batches cannot be assigned to serving tanks except via Production Complete — `BatchLocationRepository.create` and server `batch_location` validation reject vessel_id when vessel has location_id. **Production complete clears source**: On success, the source batch_location (vessel completed from) is soft-deleted so that vessel goes back to empty with no batch. **Set Volume (tank)**: Reconcile via delta CONSUME/RECEIVE; display from ledger. **Adjust Volume (tank)**: Negative/positive change posts CONSUME/RECEIVE at vessel location; no batch_location update for tanks. **Serving page**: `/serving` lists tanks with ledger on-hand, Set volume and Record removal. **Rollback**: “Log serving removal” removed from Adjust/Set Volume (non-tank); tank CONSUME only via tank path or Serving page. **Receive and Par levels**: Location lists exclude tank locations (generic use only). **UX (iterations 3–4)**: Production complete empty-state helper and "Vessel (in this batch)" label; Serving Record removal blocked when quantity > on-hand; Set volume null→0 display and prefill; Batch Detail Set/Adjust tank copy. Feature analysis: `changes/serving-ttb-implementation-analysis.md`.
- **Many-to-One Combine**: BatchLocationRepository.combineSplits({ sourceBatchLocationIds, destinationVesselId, destinationVolume? }) combines multiple source splits into one destination; optional destinationVolume sets resulting volume at destination (can differ from sum of sources); else sums volumes, creates/updates destination, deletes sources. UI: Split/Transfer modal has "Split (1 → Many)" and "Combine (Many → 1)" modes; combine uses checkboxes for sources, dropdown for destination, optional "Resulting volume at destination" field.
- **UI Redesign**: Quick actions at top: prominent "Log Reading" and "Add Ingredient" buttons. Tabs simplified: "Timeline" (milestones) and "History" (all events: readings, additions, packaging in one chronological list with icons). Vessel cards: cleaner metrics grid, "Adjust" link, "Log Reading" button per card.
- **Additions per vessel**: batch_additions now supports optional batch_location_id. "Add Ingredient" modal: Category defaults to "Any" (shows all items); From Location dropdown shows availability amounts for each location (e.g. "Cooler (15 available)"); "Add To" dropdown for vessel selection ("All vessels" or specific vessel). History tab shows vessel name for additions ("Added X · 5 · Hops · FV-1" or "· All vessels").
- **Console batch tracking (parity with mobile)**: Desktop console has full batch workflow: BatchesList (list with vessel summaries, progress, links), BatchForm (new batch with vessel splits, recipe checklist, milestone template), BatchDetail (vessels, readings, additions, packaging, split/transfer/combine, adjust volume, status, timeline and history), BatchRecipeConsume (consume recipe for batch). Console uses same repositories and SyncService (batch_locations, batch_volume_adjustments included). UI: ModalDialog and useModal (composable); App.vue provides global modal (alert/confirm) via provide('modal', { confirm, alert }) and a single ModalDialog bound to modal when not on landing/blog. BatchDetail uses syncTrigger for refresh and migrateBatchIfNeeded from console migrateMilestoneTemplates.js for legacy batch/milestone migration. Batch Detail view was redesigned for desktop (hero, actions toolbar, vessels table, Timeline/History tabs in two-column layout; see Desktop UI Design System—Batch Detail View). Feature analysis: `changes/batch-tracking-console-migration.md`, `changes/batch-detail-redesign.md`.
- **Packaging run modal clarification (2026-02-12)**: Packaging modal now includes a “logging only” banner, labels source/destination as reference-only, and reminds users to use Transfer or Set Volume for actual beer movement; intent is to reduce confusion since packaging runs do not move beer or adjust volumes. Feature analysis: `changes/packaging-run-ui-clarity-analysis.md`.
- **Limitations**: Milestones remain batch-level (per-split milestones deferred). No sync of batch_location deletes (remove-vessel and combine delete sources locally only; other devices keep old splits until delete sync added). Milestone templates system (see below) replaced preset milestones with hide; org-level templates assign to batches at creation.
- **Feature Analysis**: `changes/vessel-split-batch-locations-analysis.md`, `changes/batch-tracking-console-migration.md`, `changes/split-transfer-resulting-volumes.md`

### 10. Billing & Subscription System

Billing uses a **single-tier subscription model**: one Stripe price ($49.99/mo), one stored plan name (`subscription`), and a fixed location limit of 100 per org. There is no plan selection or plan switching in the Customer Portal.

#### Single-Tier Billing (Current Model)
- **Description**: One subscription product at $49.99/month. All subscribers receive the same plan (`subscription`) and the same location limit (100). Checkout does not accept a plan parameter; the server uses a single Stripe price ID. The Customer Portal allows cancel, invoice history, and payment method update only; plan switching is disabled.
- **Functionality**: (1) User clicks "Get Started" on landing or billing → create-checkout-session (no plan body) → Stripe Checkout with fixed price. (2) After payment, webhook or confirm-subscription sets `subscription_plan = 'subscription'`, `subscription_status = 'active'`. (3) Location enforcement uses `orgs.max_locations` (default and migrated value 100). (4) Portal sessions use Stripe default portal (no per-request configuration; configure plan switching/cancel options in Stripe Dashboard if needed). (5) cancel-subscription returns 404 if org not found; billing API errors return generic user-facing messages (details logged server-side). (6) invoice.payment_failed webhook sets org `subscription_status` to `past_due`.
- **Constraints / Assumptions**: Stripe price `price_1SwR4oPzAOv62FoydSUATwxQ` must exist and be $49.99/mo in the environment (test/live). Existing orgs must run `migrate_max_locations_100.js` once to set all `max_locations` to 100. Orgs with legacy Stripe subscriptions (old price IDs) will not have plan updated by webhook; they retain existing `subscription_plan` in DB; UI displays stored plan name (or "Subscription" when value is `subscription`). Backfill and migration scripts use `subscription_plan = 'subscription'` for consistency.

#### Stripe Integration:
- **Checkout Sessions**: Single price subscription via `STRIPE_PRICE_ID` (one constant in server used by checkout and webhook); confirm-subscription retrieves session with `expand: ['customer', 'subscription']`
- **Customer Portal**: Self-service cancel, invoice history, payment method update; plan switching disabled (default portal). `create-portal-session` accepts optional `inAppBrowser`; when true, `return_url` is set to the API origin + `/api/billing/portal-return` (redirect to `brewledger://settings`) for native in-app browser deeplink return.
- **Webhook Handling**: Reject when secret set but `stripe-signature` header missing; normalize customer/subscription/invoice customer to string IDs; map Stripe `past_due`/`unpaid` to our `past_due`; validate org exists before updating on checkout.session.completed; single price ID constant; support price/plan as object or string when matching
- **Plan Management**: Single plan stored as `subscription` in `orgs.subscription_plan`
- **Stripe Integration Review**: `changes/server-error-handling-billing-overview.md` (§0)

#### Subscription States:
- **trialing**: 30-day free trial period
- **active**: Paid subscription active
- **cancelled**: Subscription terminated
- **past_due**: Payment failed (handled by Stripe)

#### Feature Gating:
- **Location Limits**: Single limit of 100 locations per org (`orgs.max_locations`; default 100 in init_db and register; migration `migrate_max_locations_100.js` sets existing orgs to 100)
- **Trial Enforcement**: Router guard redirects expired/cancelled users to billing: on console to `/settings?tab=billing`; on mobile to `/settings`.
- **Pricing**: $49.99/mo; landing and console Settings → Billing show one price and Subscribe / Get Started CTA; copy: "Includes full access to all BrewLedger features, including batch tracking, inventory management, and full access to the desktop management console."
- **Feature Analysis**: `changes/single-tier-billing-migration.md`

#### Console Billing UI (platforms/console)
- **Billing tab**: Settings → Billing tab in `platforms/console/src/views/Settings.vue`. Status card (plan, status pill, trial info), Subscribe button (create-checkout-session → Stripe Checkout), Manage subscription / Billing history button (create-portal-session → Stripe Customer Portal when org has Stripe customer). Error/success banners; loading states. After checkout, Stripe redirects to `origin/billing/success?session_id=...`; console route `/billing/success` and `/billing/cancel` use `BillingRedirect.vue` to redirect to `/settings?tab=billing` (success preserves `session_id`). Settings billing tab detects `session_id`, calls confirm-subscription, updates session and syncs, then replaces query.
- **Router guard**: Expired/cancelled users are redirected to `/settings?tab=billing`; paths under `/billing/` are allowed so return from Stripe checkout works.
- **Portal return**: For console, `inAppBrowser: false`; portal return URL is `${returnUrl}/settings` (server default when not in-app browser), so user returns to same origin and can open Settings → Billing if needed.

#### Mobile – Billing Deprecated (brewledger-app)
- **No billing UI**: Billing has been migrated to the desktop console. Mobile has no Billing route or view; `Billing.vue` was removed.
- **Settings**: Subscription section shows plan/status/trial info and a single card: "Billing is managed on the desktop app" with link to the console URL (e.g. https://getbrewledger.com). No checkout, portal, or cancel actions on mobile.
- **Router guard**: Expired/cancelled users are redirected to `/settings` (not `/billing`).
- **Dashboard**: Trial banner "Upgrade" link goes to `/settings`.
- **Server**: `GET /api/billing/portal-return` and `GET /api/billing/success-redirect` remain for backward compatibility (e.g. native in-app browser flows if ever re-used); `inAppBrowser: true` is no longer sent from mobile.
- **Feature Analysis**: `changes/billing-desktop-migration.md`, `changes/billing-mobile-cleanup.md`, `changes/billing-portal-deeplink-return.md`

### Monetary Tracking & QuickBooks Integration
- **Item cost fields**: Items store `default_unit_cost` and `currency` (default USD) across mobile and console forms; values sync in JSON payloads.
- **Receiving with costs**: Mobile Receive flow captures invoice/bill number, unit cost per line (prefilled from item defaults), and writes `unit_cost`/`total_cost` to ledger entries for audit/export. **Vendor** is derived from each item (set on ItemForm); no per-receipt vendor input.
- **Batch cost rollups**: Batch cost is computed by `BatchCostService` and stored as `cost_summary` on batches (materials/packaging/other); Batch Detail shows a cost card. **Materials** come from ledger CONSUME entries for the batch (recipe consumption and manual "Add Ingredient" both create CONSUME; cost from entry total_cost/unit_cost or item default_unit_cost) and from batch_additions only for water/liquid (`WATER_ADDITION`, `LIQUID_ADDITION`), to avoid double-counting. Packaging comes from ledger entries with `operation_type: 'packaging_supply'` and from CONSUME when item category is Packaging. **Cost Recalculation**: Batch costs are always recalculated when viewing a batch (`loadData()` and `refreshCostSummary()` in both console and mobile apps) to ensure costs are current and fix stale costs from previous manual ingredient additions. Error handling with fallback to existing cost_summary if calculation fails. Feature analysis: `changes/batch-cost-recalculation-analysis.md`.
- **QBO backend**: New server tables (`qbo_connections`, `qbo_mappings`), OAuth helpers (auth URL, code exchange, refresh), mapping CRUD, item push, RECEIVE→Bill push, and CONSUME→Invoice push; HTML callback echoes code/realmId for manual exchange. `GET /api/integrations/qbo/customers` fetches QBO Customer list; `POST /api/integrations/qbo/push/invoice` creates Invoice from Sales Order CONSUME entry.
- **QBO console UI**: Distribution → Integrations fetches auth URL, exchanges code/realmId, connect/disconnect. **Item mapping** (Integrations, when QBO connected): table of BrewLedger beer items with QBO item dropdown (map to existing or Create in QuickBooks). Distribution → Sales Order creates removal with optional Invoice sync (Customer picker from QBO, Finished Beer items, quantity, wholesale price). Submit disabled when Create Invoice checked and selected beer has no mapping; hint links to Integrations.

### 11. Batch & Recipe Management

#### Batch Lifecycle:
1. **Creation**: Name, date, vessel assignment
2. **Additions**: Ingredient additions with timing
3. **Readings**: Gravity, temperature, pH measurements
4. **Milestones**: Brewing stage completions
5. **Packaging**: Bottling/canning runs
6. **Consumption**: Recipe-based ingredient usage

#### Recipe System:
- **Recipes**: Named ingredient lists (name, base_volume, base_volume_unit, description)
- **Recipe Items**: Ingredients with quantities and units
- **Batch Consumption**: Apply recipe to batch with automatic ledger entries (BatchRecipeConsume). After recipe consume, batch cost is recomputed and stored (`BatchCostService.computeAndStore`). Batch Detail **History** tab shows CONSUME events for that batch (ledger entries with `batch_id` and `type === 'CONSUME'`), so recipe and manual addition consumption appear in the batch timeline. Feature analysis: `changes/recipe-consume-batch-history-and-cost.md`.
- **Console UI**: Recipe list (`/recipes`) and recipe form (`/recipes/add`, `/recipes/:id/edit`) ported from mobile—list, create, edit, delete recipes; ingredients added via modal. Recipes sync with mobile. See `changes/recipes-console-port.md`.

### 12. UI/UX System

#### Component Architecture:
- **Views**: Page-level components with business logic
- **Repositories**: Data access layer with sync integration
- **Composables**: Reactive state management (useSession, useSync, useModal, useTutorial)
- **Services**: Business logic coordination (AuthService, SyncService); tutorial step definitions in `services/tutorial/tutorialSteps.js`

#### Design System:
- **Tailwind CSS**: Custom theme with extended color palette
- **Mobile-First**: Bottom navigation, touch-optimized controls
- **Dark Mode**: Class-based theme switching
- **Animations**: Fade, slide, and scale transitions

#### Routing System:
- **Vue Router**: Nested routes with authentication guards
- **Route Guards**: Subscription status validation
- **Layout Management**: Auth vs. app layout separation

#### In-App Tutorial (Brewer-Focused):
- **Purpose**: Page-by-page interactive tour for brewers new to BrewLedger (console-first, with mobile callouts). One plain-language action per screen; "Why brewers care" blurbs; optional "Got it" / "Skip for now" gating.
- **Flow**: Ten steps: Welcome (dashboard) → Locations → Inventory items → Receiving → Counts & variance → Batches → Recipes & beers → Removals & tax status → TTB Form 5130.9 → Milestone templates (Settings tab) → You're all set (final step; "Close" ends and resets the tutorial).
- **Implementation**: Step config in `platforms/console/src/services/tutorial/tutorialSteps.js`; state and progress in `composables/useTutorial.js` (persisted to localStorage by org+user); components `TutorialProgressBar`, `TutorialStepCard`, `TutorialShell` in `components/tutorial/`. Entry: "Take the tour" on Dashboard; tutorial shell fixed top-right when active; step shown for current route; completed/skipped steps show "Continue tour" link to next route. Safety: no destructive ops on protected items; system check (localStorage) gates Welcome "Start". When the user completes or skips the last step (TTB Form), the tour ends and progress is reset (finishTour: reset then exit) so the next "Take the tour" starts from step 1. **Route guard**: When trial is expired or subscription cancelled, users with an active tutorial (localStorage `startedAt`) are allowed to reach tutorial routes (dashboard, locations, items, receive, inventory, batches, recipes, removals, reports/ttb-form) to avoid redirect loops at the TTB Form step.
- **Documentation**: `changes/tutorial-implementation.md`.

### 13. TTB Form 5130.9 Reporting (Implemented)

#### Overview:
TTB Form 5130.9 is the Monthly/Quarterly Report of Operations required by the Alcohol and Tobacco Tax and Trade Bureau (TTB) for brewery reporting. The form tracks beer production, inventory movements, and removals across different operational stages (Operations, Cellar Bulk, Racking Keg, Bottling Bulk, Case).

#### Implementation Status:
- **Implemented (Console app)**: Full TTB Form 5130.9 integration across 7 phases. See `changes/ttb-form-implementation-log.md` for phase-by-phase log.
- **Implemented (Mobile app)**: TTB data collection in mobile app across 6 phases. See `changes/ttb-mobile-app-implementation-plan.md` for implementation plan and `changes/ttb-mobile-app-implementation-feature-analysis.md` for feature analysis.
- **Code review**: `changes/ttb-integration-code-review.md` documents integration verification, the Settings tab query-param fix, and recommended next steps.
- **Data gap analysis**: `changes/ttb-form-data-gap-analysis.md` – analysis of TTB form fields and data requirements.

#### Implemented Components:
- **Database**: `orgs` table extended with brewery_ein, ttb_brewery_number, brewery_address_* , brewery_phone (`server/init_db.js`, migration `server/migrate_ttb_brewery_info.js`). Brewery name for TTB form comes from `orgs.name` (set at registration).
- **API**: `GET/PUT /api/orgs/:orgId/brewery-info` (auth, TTB number validation BR-XXXXX). GET and PUT response include `brewery_name` (from `orgs.name`). PUT accepts optional `brewery_name` and updates `orgs.name`; all header fields (brewery name, EIN, TTB number, address including county, phone) are editable in Settings.
- **Console UI**: Settings → Brewery Information tab (BreweryInfoForm; editable Brewery Name, EIN, TTB number, full address including county, phone); Reports → TTB Form 5130.9 card; TTBForm view (period selection, gap detection, generate, validate, PDF export); Removals, Losses views (Racking removed 2026-03-01); **Beers** view (`/beers`) for managing finished beer products (items in Finished Beer category), with “Sync from recipes” to create a beer item per recipe; sidebar/breadcrumb links.
- **Bug/fix log**: Root-level `BUGS-AND-FIXES-LOG.md` records noticed bugs, fixes, and systemic follow-ups (brewery-info mapping; gap detection name/county; editable brewery name; form-vs-collected removal_purpose mapping; production-readiness pass: mobile RemoveBeer beer items + empty state, detectDataGaps no-beer-items gap, formatBarrels clamp, mobile LocationForm TTB stage, server reject category delete for Finished Beer; Finished Beer item delete protection: server reject item delete in sync, client repositories throw, ItemForm hide Delete for Finished Beer item). TTB beer racked: Line 25 (removals) set to 0 so "beer racked" appears only in additions (Line 9); removal side is Line 22 (beer transferred for racking). See `changes/ttb-beer-racked-additions-only.md`. TTB reporting diagnostic and fixes: `changes/ttb-reporting-diagnostic.md` — units (beer ledger/variance in barrels, no gallonsToBarrels); Line 4/24/6 mutual exclusivity; Line 14/21 and 20/28 double-count removed; Line 26 = 0 (beer bottled removals); period end set to end-of-day.
- **Services**: BreweryInfoService, TTBFormService (calculation engine for all 34 lines), TTBPDFExportService (pdf-lib; ttb.pdf in `platforms/console/public/` — if template has no form fields, a data-only PDF is generated so export still shows all numbers).
- **Column breakdowns (b–g)**: `columnsByLine` now covers Lines 2–32 in addition to Lines 1 and 33. Location stage (`locations.stage`) drives per-line column totals (cellar→b, racking keg→d, bottling bulk→e, case→f). Stage breakdowns feed preview and PDF, with reconciliation warning if Line 33 columns don’t match totals.
- **PDF/export and preview**: `ttb-final.pdf` field mapping fills per-line columns (2b/2g, 3b/3g, 4b/4g, 5b/5d/5f/5g, 6c/6e/6g, 7b/7d/7f/7g, 8b/8d/8f/8g, 9d/9g, 10f/10g, 11b–11g, 12/13b–g, 14d/14f/14g, 15/16b/15/16d/15/16f/15/16g, 17d/17f/17g, 18b/18d/18f/18g, 19b/19d/19f/19g, 20b/20g, 21b/21d/21f/21g, 22b/22g, 23b/23g, 24c/24e/24g, 25c/25g, 26e/26g, 27–31 b–g, 33 b–g, 34 b–g). Preview tables now display columns a–g per line when present.
- **In-bond receipt capture**: Removals page adds an “In-Bond Receipt” card that records RECEIVE entries (operation_type `in_bond`, `data.in_bond = true`, optional related brewery). Line 5 calculations and PDF fill now use these classified receipts. Gap detection warns when in-bond receipts are absent for a period.
- **Ledger/Repositories**: LedgerRepository addEntry/transfer include TTB fields (removal_purpose, tax_status, operation_type, etc.); VarianceEventRepository classification; BatchMilestoneRepository (production complete); BatchAdditionRepository (water/liquid); PackagingRunRepository (volume_bottled, format_type). Mobile app LedgerRepository and VarianceEventRepository updated for consistency.
- **Integration fix (review)**: Settings view honors `?tab=brewery` so TTB Form “Update Brewery Information” link opens the Brewery tab.

- **Operation-driven TTB stage (2026-03-01)**: TTB column assignment for movement lines (2, 4–8, 22–24, 27–31) derives from `operation_type` instead of location stage: `production_complete`→cellar, `racking`→racking_keg, `bottling`/`canning`→case. Lines 1 and 33 (inventory at rest) keep location stage. TTBFormService `getStageForEntry(entry, stageMap, isDestination)` implements this. LedgerRepository merges `operation_type` and `ttb_stage` into `data` for sync. Production complete RECEIVE sets `operation_type: 'production_complete'`. Vessels (fermenters, brites) now get `location_id` like serving tanks; batch assignment rejects only SERVING vessels. Packaged beer items support `volume_per_unit` (bbl per ea) for TTB conversion; ItemRepository `getOrCreatePackagedBeerItem`; Line 9/10 include ledger RECEIVE with operation_type racking/bottling/canning. Racking view and Record Packaging modal removed; packaging now via Mark Production Complete. LocationForm helper: stage for at-rest inventory; operation type for movements. Feature analysis: `changes/operation-driven-ttb-packaging-implementation.md`. Two-pass systems analysis: `changes/operation-driven-ttb-systems-analysis.md`.
- **Mark Production Complete packaging flow (2026-03-01)**: Production complete modal adds **Packaged (keg)** and **Packaged (case)** destination options alongside Serving. **Storage option commented out (2026-03)**: The Storage (cellar bulk) destination option is currently commented out (UI hidden) in both console and mobile BatchDetail; code is retained for potential future use. See `changes/storage-option-commented-out.md`. **Packaging volume vs vessel validation (2026-03)**: Before save, packaging volume (kegs/cases × format size) is compared to vessel `current_volume`; if it exceeds, a confirmation dialog offers Override or Cancel. See `changes/vessels-packaging-bug-hunt-fixes.md`. **Packaged keg**: User selects format (1/6 bbl, 1/2 bbl), number of kegs, destination location (keg storage), and supply lines (empty kegs, etc.). Volume = kegs × format size. **Packaged case**: Format (12pk, 6pk), number of cases, destination, supply lines (cans, caps, carriers). **Supply lines**: Each line = Packaging item + quantity + location; on-hand validated before save. **Ledger flow** (packaged_keg): (1) RECEIVE bulk at vessel location (Line 2), (2) TRANSFER bulk vessel→destination (operation_type racking), (3) CONSUME bulk at destination, (4) RECEIVE packaged at destination (Line 9), (5) CONSUME supplies (operation_type packaging_supply). Packaged_case uses operation_type bottling. Vessel must have `location_id`; batch locations filtered to vessels with locations for packaging. Console and mobile parity. ItemRepository `getPackagingItems`, `getOrCreatePackagedBeerItem`; LedgerRepository.transfer accepts `created_at`. **Packaged beer visibility (2026-03-01)**: After packaging, BatchDetail refreshes `items` so the new packaged beer item (e.g. "House IPA 1/6 bbl") appears in the batch ledger; console calls `incrementSyncTrigger()` so Inventory/Beers reload immediately. `cleanupBeerItemsAtZero` excludes packaged beer items (`data.base_beer_item_id`) so keg/case SKUs persist when sold out. Feature analysis: `changes/packaged-beer-visibility-fix.md`.

#### TTB Beer Ledger (Beer-as-Items, Full Form Population):
- **Design**: `ttb-beer-ledger-design.md` – beer as items on same ledger, batch linkage, location staging for columns b–e.
- **Implementation log**: `TTB-BEER-LEDGER-IMPLEMENTATION-LOG.md` (root) – systems/integrations overview and task tree.
- **Beer item identification**: Default "Finished Beer" category (system, undeletable) is created at org registration; a default "Finished Beer" **item** is no longer created for new orgs (as of 2026-02-19) but may exist for orgs created earlier or via `server/migrate_ttb_beer_category.js` / `migrate_restore_finished_beer_item.js`. Beer items are created per-recipe/per-batch when needed (e.g. Mark Production Complete). Additional beer items (category "Finished Beer") can be created and managed on the console **Beers** page (`/beers`); any recipe can be turned into a finished beer item via “Sync from recipes” (optional `recipe_id` on item links to recipe). TTBFormService and beginning/ending inventory filter by beer category. Items page shows beers in a separate "Finished Beer" section (mobile ItemsList, console Inventory). Only the **default** "Finished Beer" item (name and category both "Finished Beer"), when present, cannot be deleted: server sync and client `ItemRepository.delete()` reject/throw only for that item; console ItemForm hides Delete only for that default item; other beer items can be deleted. Non-default Finished Beer items are automatically soft-deleted when their total on-hand reaches zero (see Production complete per-batch beer items). See `changes/beers-management-console.md`, `changes/serving-tank-finished-beer-cleanup.md`.
- **Production complete**: "Mark Production Complete" always creates a RECEIVE ledger entry (beer item, cellar, volume in barrels, `batch_id`, `data.source = 'production_complete'`). TTB Line 2 is computed from RECEIVE only (no FG_CONFIRMED / milestone type). Forced last "Production Complete" milestone is system-appended on milestone template create/update (MilestoneTemplateRepository); BatchDetail completes the last milestone for timeline/audit. **Per-batch beer items (2026-02-16)**: The beer item for the RECEIVE is resolved or created per beer identity: if the batch has `recipe_id`, the beer item linked to that recipe is used (same product as other batches from that recipe); else the beer item with the same normalized batch name (trim, collapse spaces, case-insensitive) is used; if none exists, a new Finished Beer item is created (name = batch name, unit bbl, optional recipe_id). Batches created from BatchForm (console/mobile) with a recipe store `recipe_id` for resolution. When total on-hand for a Finished Beer item (except the default and packaged beer SKUs) reaches zero across all locations, the item is soft-deleted automatically (LedgerRepository.cleanupBeerItemsAtZero after addEntry, transfer, reverseEntry, and applyRemoteEntry when the entry’s item is beer). Packaged beer items (with data.base_beer_item_id) are excluded from cleanup so keg/case SKUs persist when sold out. Beers/Items lists already filter by `deleted_at`. Feature analysis: `changes/finished-beer-per-batch-items.md`.
- **Batch on ledger**: Racking (LedgerRepository.transfer with `batchId`), Removals (optional `batch_id` on addEntry). Packaging supplies CONSUME already use `run.batch_id`.
- **Location stage**: `locations.stage` (cellar | racking_keg | bottling_bulk | case); default 'cellar'. LocationRepository getAll/create/update; Settings → Locations & TTB stage tab to set stage per location. Settings copy (2026-02-16): section title "Location stages for TTB reporting" and description explain that each location is assigned to a TTB category so Form 5130.9 columns b–e are filled correctly for TTB reporting. **Location form (2026-02-27)**: Add/edit form asks "Will this location hold any finished beer products?"; if No, stage defaults to cellar and TTB dropdown is hidden; if Yes, user picks best TTB stage match.
- **TTBFormService column breakdown**: `getBeerOnhandByStage(asOfDate, opts)`; `columnsByLine.line1` and `line33` with a, b, c, d, e for PDF columns. Line 1 uses `inclusiveEnd: false` (entries strictly before period start); Line 33 uses inclusive period end. Entries without `location_id` are excluded from stage aggregation. Movement lines (2–12, 14–32) per-column deferred; implementation plan for tracking and computing those breakdowns: `changes/ttb-column-breakdowns-tracking-plan.md`.
- **Calculation/IO audit**: `changes/ttb-form-calculation-audit.md` documents a full pass over TTB calculations and PDF export. Fixes applied: beginning inventory uses entries with `created_at < periodStart` only; getBeerOnhandByStage supports exclusive end for Line 1; validateFormData is defensive against missing/invalid keys; PDF export guards `formData.header` and formatPeriod; COUNT_ADJUST/other entry types included in beginning inventory and stage delta.
- **PDF export**: TTBPDFExportService fills `line_1_b/c/d/e` and `line_33_b/c/d/e` from `formData.columnsByLine` when present. If the template has no fillable form fields (e.g. flat ttb.pdf), export generates a data-only PDF with all line values and header so the preview numbers appear on the downloaded PDF. Fillable templates support field name variants (e.g. `line_1_a`, `1a`, `Line1a`) for compatibility. See `changes/ttb-pdf-export-fix.md`.
- **Form preview columns b–e**: TTBFormPreview.vue shows column breakdown for Lines 1 and 33 when `formData.columnsByLine.line1` or `formData.columnsByLine.line33` exists. Additions table (Line 1) and Removals table (Line 33) display extra columns: Amount (a), Cellar (b), Racking Keg (c), Bottling Bulk (d), Case (e), with same barrel formatting (`toFixed(2)`). Other lines keep a single Amount (Barrels) column. Column (a) for line 1/33 comes from `columnsByLine` when present, otherwise falls back to `formData.additions.line1` / `formData.removals.line33`. See `changes/ttb-preview-columns-b-e.md`.
- **Line 21 and consumption_form (2026-02-12)**: Line 21 (beer consumed on premises) includes CONSUME with `removal_purpose === 'consumption'` (note premises/on-site), `removal_purpose === 'serving'`, and `removal_purpose === 'on_premise'`. Column breakdown (b, d, f, g) uses `entry.data.consumption_form` when present: cellar→b, keg→d, case→f; otherwise uses location stage. Removals and Batch Detail/Serving can set consumption_form for accurate column mapping.

- **Orphaned code audit (2026-03)**: Systematic audit of unused imports, orphaned components, unreachable routes, dead code, and stale references. Findings documented in `changes/orphaned-code-audit.md` (MilestonePieChart orphaned after Dashboard removal, HelloWorld, alternate Landings, ItemTemplateRepository, etc.).

#### Optional / Future Enhancements (from implementation log):
- Historical data classification / bulk update for existing entries.
- In-bond and DSP transfer classifications (Lines 5 and 29); movement lines column breakdown (e.g. 9, 10, 22, 23, 25, 26) for b–e.
- Taproom UX: optional org or template type for label/UX refinement.

#### Legacy / Original Data Requirements (for reference):

**Critical Missing Features:**
1. **Beer Production Tracking**: Mark batch completion/fermentation completion with volume and location
2. **Removal Purpose Classification**: Add removal purpose/reason to ledger entries (sale, consumption, export, R&D, supplies, inter-brewery transfer, unfit, on-premise consumption, samples, destruction, DSP transfer)
3. **Water/Liquid Additions**: Track water additions separately from other ingredients, track other liquid additions post-fermentation
4. **Racking Operations**: Track racking as separate operation from packaging, record quantity racked, date, source/destination, keg fills
5. **Packaging Detail**: Distinguish bottling from other packaging, track volume bottled (not just unit count), track returns from packaging operations
6. **Inter-Brewery Operations**: Track beer received in bond from other breweries, track transfers to related breweries, track returns from related breweries
7. **Tax Status Tracking**: Track tax-determined removals, track tax-free removals (export, R&D, supplies, inter-brewery), associate tax status with removals
8. **Return Tracking**: Track beer returned after removal, track returns from packaging operations, associate returns with original removal
9. **Variance Classification**: Distinguish overages from shortages, classify loss types (theft, spoilage, breakage), track physical inventory adjustments
10. **Cereal Beverage Tracking**: Distinguish products < 0.5% ABV, track production, removals, receipts, losses separately
11. **Brewery Information**: Store brewery EIN, TTB brewery number, full brewery address, contact phone

**Partially Tracked Features:**
- Beer transferred for racking/bottling (have transfers but don't classify purpose)
- Beer returned to cellars (have transfers but don't classify as returns)
- Physical inventory variances (have variance_events but need to distinguish overages/shortages)
- Losses (have variance_events but need to classify loss types)

**Can Calculate (No Additional Data Needed):**
- On hand beginning of period (from previous period's ending inventory)
- Total additions to inventory (sum of addition lines)
- Total amount of beer on hand at end of period (from ledger)
- Total beer (sum of all beer)

#### Implementation Phases (Planned):

**Phase 1: Core Data Structures**
- Add brewery information fields to `orgs` table (EIN, TTB number, address, phone)
- Extend `ledger_entries` with removal purpose/reason field
- Add batch completion/production tracking
- Add water/liquid addition tracking

**Phase 2: Operational Tracking**
- Add racking operations tracking
- Enhance packaging runs with volume and return tracking
- Add removal purpose classification system
- Add return tracking mechanism

**Phase 3: Advanced Features**
- Add inter-brewery transfer tracking
- Add tax status tracking
- Add cereal beverage classification
- Build TTB form generation/reporting

**Phase 4: Reporting**
- Build TTB form auto-population logic
- Add period-based reporting (monthly/quarterly)
- Add form validation and submission tracking

#### Feature Analysis:
- **Documentation**: `changes/ttb-form-data-gap-analysis.md` - Comprehensive analysis of all TTB form fields and missing data requirements

## Cross-System Interactions Analysis

### 1. Billing ↔ Sync ↔ UI Integration Flow

#### Subscription Lifecycle Integration:
```
Stripe Webhook → Server DB Update → Next Sync → Client Session Update → Router Guard Enforcement
    ↓
User Action → Billing UI → Stripe Checkout → Webhook Processing → Sync Propagation
```

#### Key Integration Points:
- **Webhook Handler**: Processes Stripe events, updates org subscription status
- **Sync Propagation**: Subscription changes flow to clients via normal sync
- **Session Management**: Client updates localStorage session on sync completion
- **Router Guards**: Enforce subscription requirements before route access

#### Edge Case Handling:
- **Trial Expiry**: Router guard redirects to billing page when trial ends
- **Cancelled Subscriptions**: Users redirected to billing unless within trial period
- **Payment Failures**: Stripe handles retries, webhook updates status to 'past_due'
- **Single Plan**: No plan switching; subscription status propagates via sync

### 2. Sync ↔ Ledger ↔ Cache Coherence

#### Transaction Consistency Chain:
```
User Action → Ledger Entry → Cache Update → Sync Status Pending
    ↓
Sync Process → Server Validation → Server Cache Update → Sync Status Synced
    ↓
Other Devices → Pull Updates → Apply Ledger Entries → Update Local Cache
```

#### Data Integrity Guarantees:
- **Atomic Operations**: Ledger entries and cache updates in same transaction
- **Idempotent Sync**: Duplicate operations ignored via unique IDs
- **Conflict Resolution**: Server authoritative for ledger consistency
- **Cache Recovery**: Full recomputation available for corruption recovery

#### Performance Trade-offs:
- **Immediate UI Feedback**: Cache updates provide instant visual feedback
- **Delayed Consistency**: Multi-device consistency achieved on next sync
- **Memory vs. Compute**: Cache trades memory for computation speed
- **Network Efficiency**: Only changed data transmitted during sync

### 3. Authentication ↔ Session ↔ State Management

#### Authentication Flow Integration:
```
Login/Register → Token Generation → Session Storage → Router Access
    ↓
API Requests → Token Validation → Org Context → Data Access
    ↓
Sync Operations → Token Authentication → Org Filtering → Data Isolation
```

#### State Management Patterns:
- **Reactive Session**: `useSession()` composable provides reactive session state
- **LocalStorage Persistence**: Session survives page reloads
- **Token Refresh**: No automatic refresh, requires re-authentication
- **Multi-Tab Support**: localStorage changes propagate across tabs

#### Security Integration:
- **Route Protection**: Router guards prevent unauthorized access
- **API Authorization**: All endpoints validate token and org access
- **Data Scoping**: All queries filtered by `org_id`
- **Rate Limiting**: Auth endpoints protected against brute force

### 4. UI ↔ Repository ↔ Service Layer

#### Data Access Architecture:
```
UI Components → Repository Methods → Dexie.js Operations → IndexedDB
    ↓
Service Layer → API Calls → Server Processing → SQLite
    ↓
Sync Service → Bidirectional Sync → Data Consistency
```

#### Error Handling Chain:
```
UI Error → Modal Display → User Feedback
    ↓
Repository Error → Exception Propagation → Service Layer
    ↓
Sync Error → Retry Logic → Error Logging
    ↓
Network Error → Offline Queue → Automatic Retry
```

#### State Update Patterns:
- **Optimistic Updates**: UI updates immediately, sync handles consistency
- **Reactive Data**: Vue reactivity triggers UI updates on data changes
- **Loading States**: UI shows loading indicators during async operations
- **Error Recovery**: User can retry failed operations

### 5. Testing ↔ Development ↔ Production

#### Environment Integration:
```
Development → Localhost URLs → Test Stripe Keys → Manual Testing
    ↓
Testing → Mocked Services → Test Databases → Automated Tests
    ↓
Production → Domain URLs → Live Stripe Keys → Real Users
```

#### Configuration Management:
- **Build-Time Configuration**: Vite injects environment-specific settings
- **Runtime Configuration**: Server reads environment variables from root `.env` (dotenv)
- **Test Configuration**: Separate configs for frontend/backend testing
- **Secret Management**: All server secrets in `.env` (gitignored); no keys in code. See §2 Secret Management.

## Data Flow Analysis

### Primary User Flows:

#### 1. Inventory Receiving:
```
User Input → Location Selection → Item Selection → Quantity Entry
    ↓
LedgerRepository.addEntry(RECEIVE)
    ↓
Update onhand_cache → Mark sync_status pending
    ↓
Next Sync → Push to Server → Update server cache
```

#### 2. Multi-Device Sync:
```
Device A: Local Change → sync_status = 'pending'
    ↓
Sync Trigger → Gather pending changes → Push to Server
    ↓
Server: Validate → Update DB → Generate updates
    ↓
Device B: Pull Updates → Apply to local DB → Update cache
```

#### 3. Subscription Management:
```
User: Get Started → Create Stripe Checkout Session (single price)
    ↓
Stripe: Payment Processing → Webhook to Server
    ↓
Server: Update org subscription_status and subscription_plan ('subscription') → Next sync propagates
    ↓
Client: Router guard allows access to features
```

## Deep Dive: Critical System Analysis

### 1. Sync System Complexities & Edge Cases

#### Conflict Resolution Scenarios:
- **Simultaneous Edits**: Two users edit same item offline → Last-write-wins based on `updated_at`
- **Delete vs Update**: User A deletes item, User B updates same item → Delete wins (soft delete preserved). **Protected items**: Item delete is rejected by server when item has `category === 'Finished Beer'` (TTB-required); clients throw in repository and hide Delete in ItemForm for that item.
- **Location Limit Conflicts**: Attempt to create location when at limit → Transaction rejected with error
- **Version Drift**: Client with stale version attempts update → Optimistic locking rejects stale update

#### Sync Failure Modes:
- **Network Interruption**: Partial sync leaves some changes pending, retries on next interval
- **Server Validation Failure**: Invalid entity rejected, client retains pending status
- **Database Corruption**: SQLite/IndexedDB errors trigger cleanup and recomputation
- **Clock Skew**: Future timestamps clamped to server time to prevent time travel issues

#### Performance Optimizations:
- **Batch Processing**: Multiple entities processed in single transaction
- **Selective Fetch**: Only changed data transmitted via `lastSyncTimestamp`
- **Cache Coherence**: Server-side cache ensures consistent inventory calculations
- **Pagination Strategy**: Ledger limited to 100 entries to prevent sync bloat

### 2. Ledger System Integrity Guarantees

#### Transaction Atomicity:
- **Double-Entry Bookkeeping**: TRANSFER_IN/OUT pairs created atomically
- **Snapshot Preservation**: Item/location/batch names stored at transaction time
- **Immutable History**: Ledger entries never modified, only reversed with new entries
- **Referential Integrity**: Foreign key validation before ledger entry acceptance

#### Cache Consistency Mechanisms:
- **Incremental Updates**: Cache updated transactionally with ledger entries
- **Full Recalculation**: `recomputeCache()` for recovery from corruption
- **Server Snapshot**: Periodic cache synchronization for multi-device consistency
- **Conflict Detection**: Duplicate entry prevention via unique ID checking

#### Business Rule Enforcement:
- **Negative Inventory Prevention**: CONSUME transactions fail if insufficient stock
- **Item Deletion Cleanup**: Automatic CONSUME entries zero out inventory
- **Transfer Grouping**: Paired entries linked by `transfer_group_id`
- **Reversal Tracking**: `reversed_of_ledger_id` maintains audit trail

### 3. Business Logic & Validation Rules

#### Entity Validation Hierarchy:
- **Required Fields**: Each entity type has mandatory attributes defined in `validateEntity()`
- **Batch Additions (Water/Liquid)**: For `batch_addition`, `item_id` is required only when `event_type` is not `WATER_ADDITION` or `LIQUID_ADDITION`; water/liquid additions may have `item_id` and `location_id` null (no ledger CONSUME). For `WATER_ADDITION` and `LIQUID_ADDITION`, `quantity` must be a positive number.
- **Type Checking**: String, number, and array type validation
- **Referential Integrity**: Foreign key existence checks for related entities
- **Domain Constraints**: Brewery-specific rules (batch status transitions, etc.)

#### Subscription Enforcement:
- **Trial Period**: 30-day automatic trial with hard expiration
- **Plan Limits**: Single location limit of 100 per org (`max_locations`)
- **Grace Periods**: Cancelled subscriptions with active trial retain access
- **Payment Failure**: Stripe webhook updates subscription status

#### Inventory Management Rules:
- **Unit Consistency**: Quantity operations respect item unit types
- **Batch Allocation**: Ingredients allocated to specific batches
- **Par Level Alerts**: Minimum quantity thresholds trigger low stock warnings
- **Count Session Integrity**: Physical counts generate COUNT_ADJUST entries

### 4. Security & Data Protection Analysis

#### Authentication Flows:
- **Token Lifecycle**: 7-day expiration with automatic cleanup
- **Password Security**: bcrypt with salt rounds for hash generation
- **Session Management**: Server-side session storage with token validation
- **Rate Limiting**: 20 attempts per 15 minutes for auth endpoints

#### Data Isolation:
- **Organization Scoping**: All queries filtered by `org_id`
- **User Role Separation**: Admin vs. regular user permissions
- **Client-Side Segregation**: IndexedDB data partitioned by organization
- **API Authorization**: Middleware validates token and org access

#### Vulnerability Considerations:
- **SQL Injection**: Parameterized queries prevent injection attacks
- **XSS Protection**: Vue.js templating provides automatic escaping
- **CSRF Mitigation**: Token-based auth reduces CSRF risk
- **Data Exposure**: JSON blobs may contain sensitive metadata

## System Interactions & Dependencies

### Critical Dependencies:
1. **Stripe API**: Billing and subscription management
2. **Dexie.js**: Client-side IndexedDB abstraction
3. **SQLite3**: Server-side data persistence
4. **bcryptjs**: Password hashing security
5. **Express Rate Limit**: API abuse prevention

### Integration Points:
- **Stripe Webhooks**: Real-time subscription updates
- **Sync API**: Bidirectional data replication
- **Auth Middleware**: Protected route access
- **Router Guards**: Feature access control

## Performance Considerations

### Optimization Strategies:
1. **Client-Side Cache**: On-hand quantities pre-computed
2. **Server-Side Cache**: Aggregate queries optimized
3. **Pagination**: Ledger limited to 100 entries per sync
4. **Batch Operations**: Multiple changes in single sync
5. **Selective Sync**: Only changed data transmitted

### Scalability Factors:
- **SQLite Limitations**: Single-writer constraint
- **Memory Usage**: JSON blob storage overhead
- **Sync Frequency**: Configurable interval (default 30s)
- **Offline Queue**: Unlimited pending operations

## Security Analysis

### Protection Mechanisms:
1. **Password Security**: bcrypt hashing with salt
2. **Token Validation**: 7-day expiration with cleanup
3. **Rate Limiting**: 20 attempts per 15 minutes for auth
4. **SQL Injection Prevention**: Parameterized queries
5. **CORS Configuration**: Restricted to app origins
6. **Input Validation**: Schema-based entity validation

### Data Privacy:
- **Organization Isolation**: Data scoped by org_id
- **Client-Side Encryption**: Not implemented (potential enhancement)
- **Audit Trail**: Ledger provides immutable history

## Testing & Quality Assurance

### Test Architecture:
- **Unit Tests**: Repository methods with mocked dependencies
- **Integration Tests**: API endpoints with test database
- **Component Tests**: Vue components with test utils
- **Schema Tests**: Database structure validation

### Test Coverage Areas:
- **Data Integrity**: Ledger calculations and cache consistency
- **Sync Logic**: Conflict resolution and error handling
- **Business Rules**: Location limits, subscription enforcement
- **API Contracts**: Request/response validation

## Deployment & Operations

### Runtime Requirements:
- **Node.js**: Backend server execution
- **Modern Browser**: IndexedDB support required
- **Stripe Account**: Billing functionality
- **SQLite File**: Persistent data storage

### Configuration Management:
- **Environment Variables**: DB_PATH, Stripe keys
- **Build Process**: Vite for frontend bundling
- **Database Migrations**: Incremental schema updates

## Limitations & Known Issues

### Technical Constraints:
1. **SQLite Concurrency**: Single writer limits high-volume scenarios
2. **Browser Storage**: IndexedDB limits vary by browser (typically 50MB-1GB)
3. **Offline Conflict**: Complex merge scenarios possible
4. **Data Loss Risk**: Browser cache clearing destroys local database

### Feature Gaps:
1. **Real-time Updates**: Polling-based sync (not WebSocket)
2. **Advanced Reporting**: Basic CSV export only
3. **Bulk Operations**: Limited batch processing capabilities
4. **Audit Logging**: Basic history without advanced querying

## Evolution & Migration Path

### Version History Evidence:
- **Database Migrations**: Billing columns, location limits, user names
- **Schema Versioning**: Dexie.js v10 schema evolution
- **Feature Layering**: Recipes, vessels, batches added incrementally
- **Repository Restructure**: Codebase reorganized into `server/` (backend) and `platforms/` (client apps)
- **Platform Expansion**: Mobile experience evolved from browser-only PWA to **Capacitor 6** native app (iOS/Android) in `platforms/brewledger-app/`; desktop console app in `platforms/console/` shares backend with mobile

### Console App Migration Status:
- **Current State**: ✅ **FULLY INTEGRATED** - Console app fully functional with authentication, sync, and data integration
- **Backend Integration**: ✅ Configured and integrated with shared backend in `server/`
- **UI Framework**: Desktop-optimized Vue 3 SPA with Tailwind CSS
- **Authentication**: ✅ Login/Register views with router guards and subscription checks
- **Data Sync**: ✅ SyncService integrated with automatic sync loop
- **Business Logic**: ✅ All 17 repositories integrated, Dashboard and Inventory views functional
- **Development Port**: Console app runs on port 5174 (mobile app on 5173)
- **Repository Paths**: Backend at `server/`, mobile at `platforms/brewledger-app/`, console at `platforms/console/`

### Extension Points:
1. **Plugin System**: Custom inventory types and workflows
2. **API Extensions**: Additional endpoints for integrations
3. **Reporting Engine**: Advanced analytics and forecasting
4. **Mobile Apps**: Capacitor 6 mobile app already in `platforms/brewledger-app/` (iOS/Android)
5. **Console App Features**: Desktop-optimized bulk operations and advanced reporting
6. **Cross-Platform Sync**: Enhanced sync capabilities between mobile and console interfaces

## Detailed Component Analysis

### 1. UI Component Architecture Patterns

#### Component Classification:
- **Layout Components**: `BottomNav.vue`, `ModalDialog.vue` - Provide structural UI elements
- **View Components**: `ItemsList.vue`, `LocationsList.vue`, `Dashboard.vue` - Page-level components with business logic
- **Utility Components**: `HelloWorld.vue` - Example/test components
- **Form Components**: `ItemForm.vue`, `LocationForm.vue` - Data entry and editing interfaces

#### Component Design Patterns:
- **Composition API**: All components use `<script setup>` with Composition API
- **Reactive State**: `ref()` and `computed()` for reactive data management
- **Repository Pattern**: Components delegate data access to repository classes
- **Route Integration**: `useRoute()` and `useRouter()` for navigation management

#### Styling Approach:
- **Tailwind CSS**: Utility-first CSS with custom theme extensions
- **Dark Mode Support**: `dark:` prefix for theme-aware styling
- **Responsive Design**: Mobile-first approach with bottom navigation
- **Component Scoping**: `<style scoped>` for component-specific styles

### 2. Repository Layer Implementation

#### Repository Responsibilities:
- **Data Access Abstraction**: Hide database implementation details from components
- **Sync Integration**: Manage `sync_status` tracking for local changes
- **Cache Management**: Handle on-hand cache updates for performance
- **Error Handling**: Centralized error handling for data operations

#### Repository Patterns:
- **Singleton Pattern**: Static methods for repository access
- **Transaction Management**: Dexie.js transactions for data integrity
- **Batch Operations**: Support for bulk data operations
- **Validation Integration**: Pre-save validation and error reporting

#### Example Repository Structure (ItemRepository):
```javascript
class ItemRepository {
  static async getAll() { /* Dexie.js query */ }
  static async getById(id) { /* Single item fetch */ }
  static async create(data) { /* Create with sync_status pending */ }
  static async update(id, data) { /* Update with version tracking */ }
  static async delete(id) { /* Soft delete with sync tracking */ }
}
```

### 3. Composables & State Management

#### Custom Composables:
- **`useSession()`**: Reactive session management with localStorage persistence
- **`useSync()`**: Sync status monitoring and manual sync triggering
- **`useModal()`**: Modal dialog management with promise-based API

#### State Management Approach:
- **Decentralized State**: No centralized store (Pinia/Vuex), uses composables
- **Reactive Composition**: `ref()` and `computed()` for component state
- **LocalStorage Integration**: Session persistence across page reloads
- **Event-Driven Updates**: Browser storage events for multi-tab sync

#### Session Management Flow:
```
Login → Token Generation → localStorage Storage → useSession() Reactivity
    ↓
API Calls → Token Validation → Component Access → Route Guards
    ↓
Logout → localStorage Clear → Session Null → Redirect to Login
```

### 4. Form Handling & Validation

#### Form Architecture:
- **Dedicated Form Components**: Separate components for add/edit operations
- **Repository Integration**: Direct repository calls for data persistence
- **Route Parameters**: Dynamic forms based on URL parameters (`:id/edit`)
- **Loading States**: Button disabling and loading indicators during submission

#### Validation Strategies:
- **Client-Side Validation**: Form field validation before submission
- **Server-Side Validation**: Backend schema validation during sync
- **Error Display**: Inline error messages with field highlighting
- **Required Fields**: HTML5 `required` attribute with custom styling

#### Form Submission Flow:
```
User Input → Form Validation → Repository Call → Sync Status Pending
    ↓
UI Feedback → Success/Error Message → Navigation/Reset
    ↓
Background Sync → Server Validation → Data Consistency
```

### 5. Navigation & Routing Patterns

#### Routing Structure:
- **Nested Routes**: Logical grouping of related functionality
- **Route Guards**: Authentication and subscription status validation
- **Dynamic Routes**: Parameter-based routing for entity editing
- **Layout Separation**: Auth layout vs. app layout with bottom navigation

#### Navigation Components:
- **`BottomNav.vue`**: Fixed bottom navigation for mobile optimization
- **Active State Management**: Dynamic class binding based on current route
- **Conditional Display**: Navigation items hidden based on subscription status
- **Safe Area Support**: `pb-safe-area` for iOS notch compatibility

#### Route Guard Logic:
```
Route Change → Auth Check → Session Validation → Subscription Check
    ↓
Public Route → Allow Access
    ↓
Private Route → Redirect to Login if No Session
    ↓
Trial Expired → Redirect to Billing Page
```
### 13. Performance & Optimization Analysis

#### Performance Characteristics:
- **Client-Side Performance**: IndexedDB operations with Dexie.js abstraction
- **Server-Side Performance**: SQLite queries with JSON blob processing
- **Network Performance**: Sync payload optimization and selective data transmission
- **UI Performance**: Vue.js reactivity with efficient component rendering

#### Optimization Strategies:
1. **Client-Side Caching**: On-hand cache pre-computes inventory quantities
2. **Server-Side Aggregation**: Server cache reduces complex query overhead
3. **Batch Operations**: Multiple changes processed in single transactions
4. **Selective Sync**: Only changed data transmitted via `lastSyncTimestamp`
5. **Pagination**: Ledger limited to 100 entries to prevent sync bloat

#### Performance Bottlenecks:
- **SQLite Single Writer**: Concurrent write operations queued
- **JSON Blob Processing**: Serialization/deserialization overhead
- **IndexedDB Quotas**: Browser storage limits vary (50MB-1GB typical)
- **Sync Frequency**: Default 30-second interval may cause perceived latency

#### Memory Management:
- **Client Memory**: Vue component trees and reactive state
- **Database Memory**: IndexedDB object stores with indexes
- **Cache Memory**: On-hand cache duplication across client and server
- **Network Memory**: Sync payload buffering during transmission

#### Scalability Considerations:
- **Vertical Scaling**: Limited by SQLite single-writer constraint
- **Horizontal Scaling**: Not supported in current architecture
- **Data Volume**: JSON blob storage may become inefficient at scale
- **Concurrent Users**: Token-based auth scales well, but SQLite limits concurrency

#### Optimization Recommendations:
1. **Database Indexing**: Ensure proper indexes on frequently queried columns
2. **Query Optimization**: Use EXPLAIN to analyze SQLite query plans
3. **Memory Profiling**: Monitor client-side memory usage during heavy operations
4. **Network Compression**: Implement gzip/brotli compression for sync payloads
5. **Lazy Loading**: Defer non-critical data loading until needed

#### Monitoring & Metrics:
 - **Performance Metrics**: Sync duration, database operation times, UI render times
 - **Resource Metrics**: Memory usage, storage consumption, network bandwidth
 - **User Metrics**: Operation success rates, error frequencies, sync completion rates
 - **Business Metrics**: Inventory accuracy, batch completion times, user engagement

### 14. Database Performance Analysis

#### IndexedDB Performance Characteristics:
- **Transaction Model**: Request-based with automatic transaction management
- **Index Performance**: Multi-entry indexes on frequently queried fields
- **Query Optimization**: Dexie.js query planner with compound indexes
- **Storage Limits**: Browser-dependent quotas with automatic cleanup

#### SQLite Performance Considerations:
- **Single Writer Constraint**: Write operations serialized, reads concurrent
- **JSON Blob Overhead**: Serialization/deserialization for each operation
- **Index Maintenance**: Automatic index updates with write amplification
- **Connection Pooling**: Single connection shared across requests

#### Cache Performance Strategies:
- **On-Hand Cache**: Pre-computed inventory quantities for instant access
- **Snapshot Updates**: Bulk cache updates from server snapshots
- **Incremental Updates**: Cache updated transactionally with ledger entries
- **Cache Invalidation**: Manual recomputation for corruption recovery

#### Query Optimization Patterns:
- **Selective Field Retrieval**: Only necessary fields fetched from JSON blobs
- **Batch Operations**: Multiple operations in single transactions
- **Pagination**: Limited result sets for large collections
- **Indexed Queries**: Proper indexing on `org_id`, `sync_status`, timestamps

### 15. Network & Sync Performance

#### Sync Protocol Efficiency:
- **Delta Updates**: Only changed data transmitted via `lastSyncTimestamp`
- **Payload Compression**: No compression implemented (potential optimization)
- **Batch Processing**: Multiple entities in single sync request
- **Idempotent Operations**: Duplicate operations safely ignored

#### Network Optimization Opportunities:
- **WebSocket Integration**: Real-time updates instead of polling
- **Payload Compression**: gzip/brotli compression for sync data
- **Connection Pooling**: Reuse HTTP connections for multiple requests
- **Request Batching**: Combine multiple API calls into single request

#### Latency Considerations:
- **Offline Operation**: Local changes immediate, sync delayed
- **Multi-Device Consistency**: Eventual consistency with sync intervals
- **User Perception**: Optimistic updates mask network latency
- **Error Recovery**: Automatic retry with exponential backoff

### 16. Frontend Performance Optimization

#### Vue.js Performance Patterns:
- **Reactive Efficiency**: Computed properties and watchers for derived state
- **Component Optimization**: `v-for` with `:key` for efficient list rendering
- **Event Handling**: Debounced input handlers for search operations
- **Memory Management**: Proper cleanup in `onUnmounted` hooks

#### Rendering Performance:
- **Virtual DOM**: Vue's efficient diffing algorithm
- **Component Reusability**: Shared components with props customization
- **Conditional Rendering**: `v-if` vs `v-show` based on frequency
- **Animation Performance**: CSS transitions vs JavaScript animations

#### Asset Optimization:
- **Code Splitting**: Route-based code splitting via Vue Router
- **Bundle Optimization**: Vite build optimization with tree shaking
- **Image Optimization**: No heavy image assets in current implementation
- **Font Loading**: System fonts used, no external font dependencies

### 17. Memory Management & Garbage Collection

#### Client-Side Memory Patterns:
- **Vue Component Trees**: Reactive state and component instances
- **IndexedDB Storage**: Persistent storage with object stores
- **Network Cache**: HTTP response caching (limited implementation)
- **UI State**: Form data, search filters, navigation state

#### Memory Leak Prevention:
- **Event Listener Cleanup**: Remove listeners in `onUnmounted` hooks
- **Subscription Management**: Proper cleanup of reactive subscriptions
- **DOM Reference Management**: Nullify references when components unmount
- **Timer Cleanup**: Clear intervals and timeouts on component destruction

#### Garbage Collection Considerations:
- **Large Object Handling**: JSON blobs may create memory pressure
- **Circular References**: Potential in complex object graphs
- **Memory Fragmentation**: Frequent allocations/deallocations
- **Heap Size Monitoring**: Browser dev tools for memory profiling

### 19. Comprehensive Edge Case Analysis

#### 1. Sync System Edge Cases:

##### Network Failure Scenarios:
- **Partial Network Connectivity**: Sync starts but connection drops mid-transfer
- **Intermittent Connectivity**: Network flaky during sync operations
- **Server Unavailable**: Backend server down during sync attempt
- **DNS Resolution Failure**: Cannot resolve backend hostname

##### Data Conflict Edge Cases:
- **Simultaneous Multi-Device Edits**: Two users edit same entity on different devices
- **Delete-Update Race**: User A deletes item while User B is editing it
- **Version Drift**: Client with stale data attempts to update server state
- **Clock Skew Issues**: Device clocks out of sync causing timestamp conflicts

##### Sync Failure Recovery:
- **Partial Sync Success**: Some entities sync, others fail
- **Corrupt Sync Payload**: Malformed JSON or data validation failures
- **Database Lock Contention**: SQLite locked during sync processing
- **Memory Pressure**: Browser runs out of memory during large sync

#### 2. Authentication & Session Edge Cases:

##### Token Management Issues:
- **Token Expiry During Operation**: Token expires mid-API call
- **Multiple Tab Sessions**: Different tabs with different session states
- **Browser Storage Quota**: localStorage full preventing session save
- **Cross-Origin Issues**: Different subdomains causing session isolation

##### Login/Logout Scenarios:
- **Concurrent Logins**: User logs in from multiple devices simultaneously
- **Force Logout**: Admin revokes user access while they're active
- **Session Hijacking**: Stolen token used from different IP/location
- **Password Change Flow**: Password changed while user has active session

#### 3. Database & Storage Edge Cases:

##### IndexedDB Limitations:
- **Storage Quota Exceeded**: Browser IndexedDB quota reached
- **Database Corruption**: IndexedDB becomes corrupted or inaccessible
- **Version Migration Failure**: Schema upgrade fails mid-migration
- **Transaction Timeout**: Long-running transaction times out

##### SQLite Constraints:
- **Single Writer Contention**: Multiple write attempts simultaneously
- **Disk Space Exhaustion**: Server disk full during database operation
- **File Permission Issues**: SQLite file permissions prevent writes
- **Database Locking**: Long-running queries block other operations

#### 4. Business Logic Edge Cases:

##### Inventory Management:
- **Negative Inventory Prevention**: Attempt to consume more than available
- **Unit Conversion Errors**: Mismatched units in calculations
- **Batch Lifecycle Violations**: Invalid state transitions in batch workflow
- **Location Limit Enforcement**: Attempt to exceed subscription location limits

##### Financial Transactions:
- **Stripe Webhook Failures**: Stripe events not processed correctly
- **Payment Processing Race**: Concurrent subscription modifications
- **Currency Conversion Issues**: Different currencies in Stripe vs application
- **Refund Processing**: Handling refunds and subscription adjustments

#### 5. UI/UX Edge Cases:

##### Form Submission Issues:
- **Double Form Submission**: User submits form multiple times quickly
- **Form Data Loss**: Browser refresh during form editing
- **Validation Race Conditions**: Async validation conflicts with submission
- **File Upload Failures**: Large file uploads timeout or fail

##### Navigation Problems:
- **Broken Deep Links**: Invalid or expired deep links
- **Back Button Navigation**: Unexpected state after browser back
- **Tab Restoration**: Browser restores tabs with stale application state
- **Offline Navigation**: Attempt to navigate to route requiring network

#### 6. Multi-Device & Offline Edge Cases:

##### Offline Operation Challenges:
- **Extended Offline Period**: Device offline for days/weeks
- **Offline Conflict Accumulation**: Many conflicting changes accumulate offline
- **Storage Exhaustion Offline**: Local storage fills while offline
- **Battery Saver Restrictions**: Device restrictions affecting background sync

##### Multi-Device Synchronization:
- **Device Time Skew**: Different device clocks causing ordering issues
- **Device Storage Differences**: Different browsers with different quotas
- **Cross-Browser Compatibility**: Different IndexedDB implementations
- **App Version Mismatch**: Different app versions with different schemas

#### 7. Security & Privacy Edge Cases:

##### Data Exposure Risks:
- **Incomplete Data Isolation**: Bugs allowing cross-org data access
- **Session Data Leakage**: Sensitive data in localStorage accessible to scripts
- **API Information Disclosure**: Error messages revealing system details
- **Log File Exposure**: Server logs containing sensitive information

##### Authentication Bypass:
- **Token Manipulation**: Modified or forged authentication tokens
- **CSRF Vulnerabilities**: Cross-site request forgery attacks
- **XSS Injection**: Cross-site scripting allowing session theft
- **Brute Force Attacks**: Automated password guessing attempts

#### 8. Performance & Scalability Edge Cases:

##### Load Handling Issues:
- **Sudden Traffic Spikes**: Unexpected high load on server
- **Memory Leak Accumulation**: Gradual memory consumption increase
- **Database Bloat**: Unbounded growth of historical data
- **Sync Storm**: Many devices syncing simultaneously after outage

##### Resource Exhaustion:
- **Connection Pool Exhaustion**: All database connections in use
- **File Descriptor Limits**: OS limits on open files/database connections
- **Memory Exhaustion**: Server runs out of available memory
- **CPU Saturation**: High CPU usage degrading performance

#### 9. Deployment & Operations Edge Cases:

##### Deployment Failures:
- **Failed Database Migration**: Schema changes fail during deployment
- **Configuration Mismatch**: Inconsistent config between environments
- **Dependency Version Conflicts**: Incompatible library versions
- **Build Process Failures**: Compilation or bundling errors

##### Monitoring & Alerting:
- **Silent Failures**: Errors that don't trigger alerts
- **Alert Fatigue**: Too many false positive alerts
- **Monitoring Blind Spots**: Unmonitored critical components
- **Log Rotation Issues**: Lost logs due to rotation or corruption

#### 10. Recovery & Disaster Scenarios:

##### Data Loss Scenarios:
- **Database Corruption**: Both client and server databases corrupted
- **Accidental Deletion**: Critical data deleted by user or admin
- **Ransomware Attack**: Data encrypted by malicious software
- **Physical Disaster**: Server hardware failure or data center outage

##### Recovery Procedures:
- **Backup Restoration**: Restoring from incomplete or outdated backups
- **Data Reconstruction**: Rebuilding data from audit logs or exports
- **System Rollback**: Reverting to previous version after failed update
- **Disaster Recovery**: Complete system rebuild from backups

### 21. Data Modeling & Schema Analysis

#### 1. Database Architecture Patterns

##### Dual Database Strategy:
- **Client-Side (IndexedDB via Dexie.js)**: Versioned schema (v10) with 17 entity tables
- **Server-Side (SQLite)**: Similar structure with JSON blob storage
- **Schema Synchronization**: Manual alignment between client and server schemas
- **Migration Strategy**: Incremental schema evolution with version tracking

##### JSON Blob Storage Pattern:
- **Core Entity Data**: Stored in `data` column as JSON strings
- **Metadata Columns**: Separate columns for id, org_id, timestamps, version, sync_status
- **Flexibility Benefits**: Schema evolution without database migrations
- **Performance Trade-off**: Serialization/deserialization overhead for each operation

#### 2. Entity Relationship Model

##### Core Entity Hierarchy:
```
Organization (orgs)
├── Users (users)
├── Locations (locations)
├── Items (items)
│   ├── Categories (categories)
│   └── Par Levels (par_levels)
├── Batches (batches)
│   ├── Batch Additions (batch_additions)
│   ├── Batch Readings (batch_readings)
│   ├── Batch Milestones (batch_milestones)
│   ├── Packaging Runs (packaging_runs)
│   └── Allocations (allocations)
├── Vessels (vessels)
├── Count Sessions (count_sessions)
│   └── Variance Events (variance_events)
├── Recipes (recipes)
│   └── Recipe Items (recipe_items)
└── Ledger Entries (ledger_entries)
```

##### Key Relationships:
- **One-to-Many**: Organization → Users, Locations, Items, Batches
- **Many-to-Many**: Recipes ↔ Items (via recipe_items join table)
- **Hierarchical**: Batches → Additions, Readings, Milestones (parent-child)
- **Transactional**: Ledger entries reference items, locations, batches

#### 3. Schema Design Patterns

##### Common Column Patterns:
- **Primary Keys**: UUID strings as TEXT primary keys
- **Organization Scoping**: `org_id` on all entity tables for multi-tenancy
- **Timestamps**: `created_at`, `updated_at`, `server_updated_at` for sync tracking
- **Version Control**: `version` column for optimistic locking
- **Sync Status**: `sync_status` ('pending', 'synced', 'error') for offline sync

##### Index Strategy:
- **Client-Side Indexes**: Dexie.js compound indexes on frequently queried fields
- **Server-Side Indexes**: SQLite indexes on `org_id`, foreign key columns
- **Performance Indexes**: `onhand_cache` with composite primary key for fast lookups
- **Query Optimization**: Indexes on `sync_status` for pending change detection

#### 4. Data Integrity Constraints

##### Referential Integrity:
- **Foreign Key Constraints**: SQLite FOREIGN KEY constraints on server
- **Application-Level Enforcement**: Client-side validation before sync
- **Cascade Considerations**: Soft deletes with referential integrity maintenance
- **Orphan Prevention**: Validation rules prevent orphaned child records

##### Business Rule Enforcement:
- **Inventory Constraints**: Negative inventory prevention via ledger validation
- **Subscription Limits**: Location count enforcement; single limit of 100 locations per org (`max_locations`)
- **Batch State Machine**: Valid state transitions enforced in business logic
- **Unit Consistency**: Brewing unit validation across related entities

#### 5. Sync-Aware Data Model

##### Sync Metadata Columns:
- **`sync_status`**: Tracks local change state ('pending', 'synced', 'error')
- **`version`**: Optimistic locking for conflict detection
- **`server_updated_at`**: Server timestamp for ordering and delta sync
- **`updated_at`**: Client timestamp for local ordering

##### Change Tracking Strategy:
- **Append-Only Ledger**: Immutable transaction history for auditability
- **Entity Versioning**: Incremental version numbers for change detection
- **Timestamp Ordering**: Chronological ordering for conflict resolution
- **Delta Detection**: `lastSyncTimestamp` for efficient change transmission

#### 6. Cache Architecture

##### On-Hand Cache Design:
- **Purpose**: Pre-computed inventory quantities for performance
- **Structure**: Composite primary key (org_id, item_id, location_id)
- **Update Strategy**: Transactional updates with ledger entries
- **Recovery Mechanism**: Full recomputation via `recomputeCache()`

##### Cache Consistency:
- **Client-Server Alignment**: Both sides maintain identical cache structures
- **Snapshot Updates**: Bulk cache replacement from server snapshots
- **Incremental Updates**: Cache updated with each ledger entry
- **Conflict Resolution**: Server cache authoritative in case of divergence

#### 7. Schema Evolution Strategy

##### Migration Patterns:
- **Forward-Compatible Design**: JSON blob storage enables schema flexibility
- **Incremental Migrations**: `ALTER TABLE ADD COLUMN` with error suppression
- **Client-Side Versioning**: Dexie.js schema version upgrades
- **Backward Compatibility**: Old clients can read new schema (within limits)

##### Version Management:
- **Database Version Tracking**: Explicit version numbers in schemas
- **Migration Scripts**: Separate migration files for schema changes
- **Rollback Strategy**: Backup before migrations for recovery
- **Testing Strategy**: Migration testing in isolated environments

#### 8. Data Modeling Best Practices

##### Domain-Driven Design:
- **Brewery Domain Model**: Entities reflect real-world brewing concepts
- **Ubiquitous Language**: Consistent terminology across codebase
- **Bounded Contexts**: Clear separation between inventory, batches, billing
- **Aggregate Roots**: Organizations as root aggregates with consistency boundaries

##### Performance Considerations:
- **Query Patterns**: Schema optimized for common access patterns
- **Index Selection**: Indexes based on actual query requirements
- **Data Denormalization**: Cache tables for performance optimization
- **Storage Efficiency**: JSON blobs vs. normalized columns trade-off analysis

### 23. Comprehensive Testing & Quality Assurance Analysis

#### 1. Testing Architecture & Strategy

##### Test Pyramid Implementation:
- **Unit Tests**: Repository methods with mocked dependencies (Vitest)
- **Integration Tests**: API endpoints with test database (Supertest + Vitest)
- **Component Tests**: Vue components with test utilities (Vue Test Utils)
- **Schema Tests**: Database structure validation and migration testing

##### Test Environment Configuration:
- **Frontend Test Setup**: JSDOM environment with fake IndexedDB
- **Backend Test Setup**: Isolated SQLite databases with cleanup
- **Mock System**: Comprehensive mocking of external services (Stripe, AuthService)
- **Test Data Management**: Factory functions and test data builders

##### Test Execution Strategy:
- **Parallel Execution**: Tests run in parallel for speed
- **Isolated Environments**: Each test suite with clean database state
- **CI/CD Integration**: GitHub Actions or similar for automated testing
- **Test Reporting**: Detailed test reports with coverage metrics

#### 2. Test Coverage Analysis

##### Repository Layer Testing:
- **CRUD Operations**: Create, read, update, delete functionality
- **Business Logic**: Inventory calculations, batch workflows, sync logic
- **Error Handling**: Validation failures, constraint violations, edge cases
- **Integration Points**: Repository interactions with other systems

##### API Endpoint Testing:
- **Authentication**: Registration, login, token validation, session management
- **Business APIs**: Inventory operations, batch management, ledger entries
- **Sync Endpoints**: Push/pull operations, conflict resolution, error handling
- **Billing Integration**: Stripe webhooks, subscription management, plan changes

##### Component Testing:
- **UI Components**: Rendering, user interactions, state management
- **Form Validation**: Input validation, error display, submission handling
- **Navigation**: Route changes, guard logic, breadcrumb navigation
- **Responsive Design**: Mobile/desktop layout, touch interactions

#### 3. Quality Assurance Practices

##### Code Quality Standards:
- **Code Review Process**: Peer review requirements and guidelines
- **Static Analysis**: ESLint configuration (potential enhancement)
- **Type Safety**: JavaScript with JSDoc comments (TypeScript potential)
- **Documentation**: Code comments, API documentation, architecture docs

##### Testing Best Practices:
- **Test Isolation**: Independent tests with no shared state
- **Mock Strategy**: Appropriate mocking levels (unit vs integration)
- **Test Data**: Realistic test data with edge cases
- **Assertion Quality**: Meaningful assertions with clear failure messages

##### Continuous Integration:
- **Automated Testing**: Test execution on every commit/pull request
- **Quality Gates**: Required test passing before merge
- **Coverage Requirements**: Minimum test coverage thresholds
- **Performance Testing**: Load testing and performance benchmarks

#### 4. Test Implementation Patterns

##### Repository Test Patterns:
```javascript
// Example repository test pattern
describe('ItemRepository', () => {
  beforeEach(async () => {
    await db.delete(); // Clean database
    await db.open();
    vi.clearAllMocks(); // Reset mocks
  });

  it('should create and retrieve item', async () => {
    const item = await ItemRepository.create({ name: 'Malt' });
    expect(item.id).toBeDefined();
    expect(item.name).toBe('Malt');
  });
});
```

##### API Test Patterns:
```javascript
// Example API test pattern
describe('Auth API', () => {
  beforeAll(async () => {
    // Setup test database
    app = createApp({ dbPath: TEST_DB_PATH });
    await initDb(app.db);
  });

  afterAll(async () => {
    // Cleanup test database
    await app.db.close();
    fs.unlinkSync(TEST_DB_PATH);
  });

  it('should register organization', async () => {
    const res = await request(app)
      .post('/api/auth/register-org')
      .send({ orgName: 'Test', email: 'test@test.com', password: 'pass' });
    
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('token');
  });
});
```

#### 5. Test Data Management

##### Test Data Strategies:
- **Factory Functions**: Reusable test data creation utilities
- **Fixtures**: Pre-defined test data sets for common scenarios
- **Randomization**: Randomized test data for edge case discovery
- **Realistic Data**: Production-like data for integration testing

##### Database State Management:
- **Transaction Rollback**: Tests wrapped in transactions for isolation
- **Database Reset**: Complete database reset between test suites
- **Snapshot Testing**: Database state comparison for regression testing
- **Migration Testing**: Schema migration validation with test data

##### Mock Data Patterns:
- **External Services**: Stripe API mocks for billing testing
- **Authentication**: Mocked AuthService for repository testing
- **Network Calls**: Mocked HTTP requests for sync testing
- **Browser APIs**: Mocked localStorage and IndexedDB for unit tests

#### 6. Performance & Load Testing

##### Performance Test Categories:
- **API Response Times**: Endpoint performance under load
- **Database Query Performance**: Index efficiency and query optimization
- **Sync Performance**: Large dataset synchronization timing
- **UI Rendering Performance**: Component render times and memory usage

##### Load Testing Strategy:
- **Concurrent Users**: Simulated multiple users accessing system
- **Data Volume Testing**: Performance with large datasets
- **Stress Testing**: System behavior under extreme load
- **Endurance Testing**: Long-running operation stability

##### Performance Monitoring:
- **Metrics Collection**: Response times, error rates, resource usage
- **Baseline Establishment**: Performance benchmarks for comparison
- **Regression Detection**: Automated performance regression testing
- **Capacity Planning**: Resource requirements for expected load

#### 7. Security Testing

##### Authentication & Authorization Testing:
- **Token Validation**: JWT token expiration and validation
- **Role-Based Access**: Admin vs user permission testing
- **Session Management**: Session timeout and cleanup testing
- **Password Security**: Password strength and hashing validation

##### Vulnerability Testing:
- **SQL Injection**: Input validation and parameterized query testing
- **XSS Prevention**: Output encoding and sanitization testing
- **CSRF Protection**: Token validation and request forgery testing
- **Data Exposure**: Information leakage and privacy testing

##### Security Compliance:
- **Data Encryption**: At-rest and in-transit encryption testing
- **Audit Logging**: Security event logging and monitoring
- **Compliance Testing**: Regulatory requirement validation
- **Penetration Testing**: External security assessment

#### 8. Test Automation & CI/CD

##### Continuous Integration Pipeline:
- **Pre-commit Hooks**: Code quality checks before commit
- **Pull Request Validation**: Automated testing on PR creation
- **Merge Gatekeeping**: Required test passing before merge
- **Deployment Validation**: Production deployment testing

##### Test Environment Management:
- **Environment Parity**: Test environments matching production
- **Infrastructure as Code**: Test environment provisioning automation
- **Data Seeding**: Automated test data population
- **Environment Cleanup**: Automated resource cleanup after tests

##### Monitoring & Reporting:
- **Test Results Dashboard**: Centralized test result visualization
- **Failure Analysis**: Automated root cause analysis for test failures
- **Trend Analysis**: Test performance and coverage trends over time
- **Quality Metrics**: Code quality metrics and improvement tracking

#### 9. Test Maintenance & Evolution

##### Test Refactoring:
- **Test Code Quality**: Maintainable and readable test code
- **Test Data Management**: Evolvable test data strategies
- **Test Organization**: Logical test structure and grouping
- **Test Documentation**: Clear test purpose and scenario documentation

##### Test Evolution Strategy:
- **Test Coverage Expansion**: Incremental test coverage improvement
- **Test Technology Updates**: Framework and tool updates
- **Test Performance Optimization**: Faster test execution strategies
- **Test Reliability Improvement**: Flaky test detection and resolution

##### Test Governance:
- **Test Standards**: Established testing standards and guidelines
- **Test Review Process**: Code review for test implementations
- **Test Metrics Tracking**: Quality metrics monitoring and reporting
- **Test Improvement Planning**: Continuous test improvement roadmap

### 24. Error Handling & User Feedback

#### Error Display Patterns:
- **Modal Dialogs**: `useModal()` for critical errors and confirmations
- **Inline Messages**: Form field errors with contextual positioning
- **Toast Notifications**: Not implemented (potential enhancement)
- **Loading States**: Button spinners and disabled states during operations

#### Error Recovery:
- **Network Errors**: Automatic retry with exponential backoff
- **Validation Errors**: Clear error messages with field focus
- **Sync Failures**: Pending queue preservation with manual retry option
- **Database Errors**: Graceful degradation with user notification

#### User Experience Considerations:
- **Immediate Feedback**: Optimistic updates for responsive UI
- **Progressive Disclosure**: Complex operations broken into steps
- **Accessibility**: Semantic HTML with ARIA attributes (limited implementation)
- **Mobile Optimization**: Touch-friendly controls and bottom navigation

## Synthesis & Strategic Recommendations

### Architectural Strengths

#### 1. Local-First Design Excellence:
- **Offline Resilience**: Robust offline operation with automatic sync recovery
- **User Experience**: Immediate UI feedback with background consistency
- **Network Tolerance**: Graceful degradation during connectivity issues
- **Data Ownership**: Users retain control over their inventory data

#### 2. Sync System Sophistication:
- **Operation-Based Approach**: Fine-grained conflict resolution capabilities
- **Bidirectional Flow**: Seamless multi-device synchronization
- **Optimistic Updates**: Responsive user experience despite network latency
- **Data Integrity**: Comprehensive validation and consistency guarantees

#### 3. Domain-Specific Specialization:
- **Brewery Workflow Optimization**: Tailored for brewing inventory management
- **Batch Lifecycle Support**: Complete tracking from ingredient to finished product
- **Unit-Aware Calculations**: Proper handling of brewing-specific measurements
- **Industry Compliance**: Supports standard brewing documentation requirements

### Critical Technical Decisions

#### 1. Technology Stack Choices:
- **Vue.js 3 + Vite**: Modern frontend with excellent developer experience
- **SQLite + IndexedDB**: Dual database approach for local-first architecture
- **Express.js**: Lightweight backend with minimal dependencies
- **Tailwind CSS**: Utility-first CSS for rapid UI development

#### 2. Data Architecture Patterns:
- **JSON Blob Storage**: Flexible schema evolution with relational metadata
- **Operation-Based Sync**: Append-only log for auditability and conflict resolution
- **Dual Cache System**: Client and server caches for performance optimization
- **Immutable Ledger**: Append-only transaction history for audit compliance

#### 3. Security Implementation:
- **Token-Based Auth**: Stateless authentication with 7-day expiration
- **Organization Isolation**: Complete data separation between organizations
- **Input Validation**: Comprehensive schema-based validation
- **Rate Limiting**: Protection against brute force attacks

### Risk Assessment & Mitigation

#### High-Risk Areas:
1. **Secret Management**: Resolved. Stripe, OpenRouter, Brave, and other keys are loaded from root `.env` via dotenv; no secrets in source. See §2 Secret Management and `changes/env-secret-extraction.md`.
   - **Mitigation**: Env vars; `.env` gitignored; scripts and server load from same file.
   - **Priority**: Addressed.

2. **SQLite Concurrency**: Single-writer limitation
   - **Mitigation**: Connection pooling and write queue management
   - **Priority**: Medium for scaling beyond small teams

3. **Browser Storage Limits**: IndexedDB quota constraints
   - **Mitigation**: Data pruning and compression strategies
   - **Priority**: Medium for long-term usage

4. **Conflict Resolution**: Basic last-write-wins approach
   - **Mitigation**: Enhanced merge strategies and user intervention
   - **Priority**: Medium for collaborative workflows

#### Medium-Risk Areas:
1. **Error Recovery**: Limited automatic retry mechanisms
2. **Monitoring**: Basic logging without centralized monitoring
3. **Backup Strategy**: Manual database backup requirements
4. **Performance Scaling**: No horizontal scaling capabilities

### Future Development Roadmap

#### Phase 1: Production Readiness (Immediate)
1. **Security Hardening**: External secret configuration, HTTPS enforcement
2. **Monitoring Integration**: Application performance monitoring and error tracking
3. **Backup Automation**: Automated database backup and recovery procedures
4. **Deployment Scripts**: Containerization and cloud deployment automation

#### Phase 2: Enhanced Features (Short-term)
1. **Real-time Updates**: WebSocket integration for instant sync notifications
2. **Advanced Reporting**: Custom report builder and analytics dashboard
3. **Bulk Operations**: Batch import/export and mass update capabilities
4. **Mobile Applications**: Progressive Web App optimization or native wrappers

#### Phase 3: Scalability & Enterprise (Long-term)
1. **Database Migration**: PostgreSQL support for larger deployments
2. **Multi-tenant Architecture**: Support for brewery chains with multiple locations
3. **API Extensibility**: Public API for third-party integrations
4. **Advanced Analytics**: Predictive inventory and batch success forecasting

### Maintenance & Operational Considerations

#### Development Workflow:
- **Code Quality**: Add ESLint and Prettier for consistent code style
- **Testing Strategy**: Increase test coverage, especially for edge cases
- **Documentation**: API documentation with OpenAPI/Swagger
- **CI/CD Pipeline**: Automated testing and deployment pipeline
- **Development Scripts**: `run-dev.sh` and `run-dev.bat` for multi-service development
  - Services: Backend API from `server/` (port 3000), Mobile App from `platforms/brewledger-app/` (port 5173), Console App from `platforms/console/` (port 5174)
  - Logging: All services output to `logs/` directory
  - Process Management: Proper cleanup on exit with PID tracking

#### Operational Requirements:
- **Server Requirements**: Node.js runtime with SQLite write permissions
- **Storage Requirements**: Regular database backup and monitoring
- **Network Requirements**: HTTPS for Stripe webhooks and secure API
- **Monitoring Requirements**: Application logs, error tracking, performance metrics

#### Support & Maintenance:
- **User Support**: Error reporting and feedback mechanisms
- **Data Migration**: Tools for schema evolution and data migration
- **Security Updates**: Regular dependency updates and security patches
- **Performance Optimization**: Ongoing performance monitoring and tuning

## Conclusion

BrewLedger represents a sophisticated implementation of local-first architecture for a specialized domain (brewery inventory management). The repository structure cleanly separates backend (`server/`) from client platforms (`platforms/brewledger-app/` for mobile, `platforms/console/` for desktop). The system successfully balances offline capability with multi-device synchronization, implements robust business logic for inventory tracking, and integrates commercial billing via Stripe. The architecture demonstrates thoughtful consideration of real-world constraints while maintaining extensibility for future enhancements.

The codebase shows evidence of iterative development with attention to testing, documentation, and maintainability. Key strengths include the operation-based sync protocol, comprehensive data validation, and mobile-optimized user experience. Areas for potential improvement include enhanced conflict resolution, real-time updates, and more advanced reporting capabilities.

### Final Assessment:
- **Architecture Maturity**: Production-ready with minor security concerns
- **Code Quality**: Well-structured with good separation of concerns
- **Test Coverage**: Adequate for core functionality, could be expanded
- **Documentation**: Good technical documentation, could benefit from user guides
- **Scalability**: Suitable for small to medium breweries, requires enhancements for large-scale deployment

This analysis provides comprehensive technical reference for agents and future development context, covering all major systems, their interactions, and strategic considerations for the BrewLedger application.

## Console App Integration - Complete Implementation

### Overview
The BrewLedger Console app (`platforms/console/`) is a desktop-optimized management interface that shares the same backend API (`server/`) as the Capacitor mobile app. It provides enhanced desktop features for brewery operations while maintaining full data synchronization with the mobile app.

### Architecture & Integration

#### Technology Stack
- **Frontend**: Vue.js 3 + Vite + Tailwind CSS + Dexie.js (IndexedDB)
- **Backend**: Shared Express.js server in `server/` (port 3000)
- **Database**: IndexedDB (client-side) + SQLite (server-side, shared)
- **Authentication**: JWT-like token-based auth (shared with mobile app)
- **Sync Protocol**: Operation-based sync (shared protocol)

#### Project Structure
```
platforms/console/
├── src/
│   ├── db.js                    # IndexedDB schema (v10, matches mobile app)
│   ├── config.js                # API configuration
│   ├── main.js                  # Vue app entry point
│   ├── App.vue                  # Main layout with sidebar navigation
│   ├── router/
│   │   └── index.js            # Router with auth guards and subscription checks
│   ├── services/
│   │   ├── AuthService.js      # Authentication service (shared logic)
│   │   └── SyncService.js      # Sync service (shared protocol)
│   ├── composables/
│   │   ├── useSession.js       # Reactive session management
│   │   └── useSync.js          # Sync state management
│   ├── repositories/           # All 17 repositories (shared with mobile app)
│   │   ├── ItemRepository.js
│   │   ├── LocationRepository.js
│   │   ├── BatchRepository.js
│   │   ├── LedgerRepository.js
│   │   └── ... (all repositories)
│   ├── blog/
│   │   ├── posts/              # Markdown blog posts with frontmatter
│   │   └── README.md           # Blog post format documentation
│   ├── components/
│   │   ├── BlogSidebar.vue     # Popular posts + About BrewLedger CTA
│   │   └── MarkdownRenderer.vue
│   ├── utils/
│   │   └── blogLoader.js       # Load/parse markdown posts, loadPopularPosts()
│   └── views/
│       ├── Login.vue           # Authentication view
│       ├── Register.vue         # Registration view
│       ├── Dashboard.vue        # Main dashboard with inventory, low stock, batches timeline
│       ├── Inventory.vue        # Inventory management view
│       ├── Ledger.vue            # Ledger (transaction history) view
│       ├── BlogList.vue         # Blog index (public)
│       ├── BlogPost.vue         # Individual blog post (public)
│       ├── Analytics.vue       # Analytics view (placeholder)
│       ├── Reports.vue          # Reports view (placeholder)
│       └── Settings.vue         # Settings with subscription status
```

### Authentication Integration

#### Login/Register Flow
1. **Registration**: Users create organization via `/register` endpoint
2. **Login**: Users authenticate via `/auth/login` endpoint
3. **Session Storage**: Token and session data stored in localStorage
4. **Router Guards**: Protected routes require valid token and subscription
5. **Token Validation**: Cached validation (1 minute) to reduce API calls
6. **Subscription Checks**: Router redirects expired/cancelled subscriptions to settings

#### Router Guard Implementation
```javascript
// Key features:
- Token validation with caching (1 minute cache)
- Subscription status checking (trial expiration, cancellation)
- Automatic redirects for expired subscriptions
- Cache clearing on logout
```

#### Session Management
- **Reactive Session**: `useSession()` composable provides reactive session state
- **Auto-refresh**: Session refreshed on app mount
- **Logout**: Proper cleanup of sync loops and token cache
- **Multi-tab Support**: localStorage changes propagate across tabs

### Sync Service Integration

#### Sync Implementation
- **Automatic Sync**: Sync loop starts automatically when authenticated
- **Sync Interval**: 30 seconds (configurable)
- **Error Handling**: Sync errors displayed in header status indicator
- **Loop Management**: Prevents multiple sync loops from starting
- **Cleanup**: Sync loop stopped on logout

#### Sync Status Display
- Visual indicator in App.vue header
- Shows "Syncing...", "Synced", or "Sync Error" states
- Real-time sync status updates

### Dashboard Features

#### Inventory Overview
- **Top 10 Items**: Displays top inventory items by quantity
- **Real-time Data**: Loads from IndexedDB repositories
- **Location Display**: Shows primary location for each item
- **Category Display**: Shows item categories

#### Low Stock Items
- **Par Level Checking**: Individual (per-location) and global (total on-hand) par levels; distinct item count
- **Visual Alerts**: Warning-styled cards with global vs per-location scope indicators
- **Location Context**: Shows which location has low stock or "Global" for total breach
- **Threshold Display**: Shows current quantity vs. minimum threshold
- **Manage Link**: Link to Inventory for par level management

#### Active Batches Timeline
- **Milestone-based Timeline**: Overlapping timeline visualization based on batch milestones
- **Date Range Calculation**: Automatically calculates date range from milestone dates
- **Batch Bars**: Visual bars showing batch duration and milestones
- **Status Display**: Shows batch status and milestone completion
- **Edge Case Handling**: Handles empty timelines, single milestones, invalid dates

#### Timeline Visualization Details
- **Date Markers**: Shows date range at top of timeline
- **Batch Positioning**: Batches positioned based on first/last milestone dates
- **Overlapping Display**: Multiple batches can overlap on timeline
- **Scrollable**: Max height with scrolling for many batches
- **Color Coding**: Different colors for different batches

### Inventory View

#### Features
- **Real-time Stock Levels**: Loads from LedgerRepository cache
- **Search Functionality**: Filter items by name, category, location
- **Status Indicators**: Visual status badges (In Stock, Low Stock, Out of Stock); low stock border accent
- **Par Level Integration**: Individual and global pars; "Manage Par Levels" modal with scope selector (Global or per-location)
- **Locations and Par Status (Expandable Rows)**: Each inventory row can be expanded to show (1) **Global par level**: total on-hand vs min, status (In Stock / Low Stock) or "No global par set"; (2) **By location**: table of all locations where the item has stock or a par level—Location, Qty, Par (min), Status (In Stock / Low Stock / No par). Locations list is the union of locations with quantity > 0 and locations with a per-location par level. Expand/collapse per row; "Locations" column shows count (e.g. "3 locations + global").
- **Error Handling**: Error display with retry functionality
- **Data Validation**: Filters deleted items and validates references

#### Data Loading
- Loads on component mount
- Watches sync timestamp for updates
- Debounced reloads to prevent rapid refreshes
- Error handling with user feedback

### Ledger View

#### Overview
- **Purpose**: Display immutable transaction history (ledger entries) in the desktop console; parity with mobile app Ledger view.
- **Route**: `/ledger` (requires auth).
- **Source**: Adapted from `platforms/brewledger-app/src/views/Ledger.vue`; console view at `platforms/console/src/views/Ledger.vue`.

#### Features
- **Transaction List**: Ledger entries shown with item name, location, type badge (RECEIVE/ADJUST green, CONSUME/NEG orange, TRANSFER blue), quantity (+/-), date/time, and optional note.
- **Name Resolution**: Item and location names resolved from active repositories; historical/deleted entities from raw IndexedDB (items, locations by org_id); fallback to ledger snapshot (`item_name`, `location_name`) then ID.
- **Data Source**: `LedgerRepository.getEntries(filters)`; console uses same LedgerRepository and IndexedDB schema as mobile (ledger_entries, onhand_cache).
- **Error Handling**: Error state with message and Retry button; load() wrapped in try/catch; aligns with Inventory/Dashboard error patterns.
- **Layout**: Desktop-optimized (no bottom nav padding); rounded cards, hover states; loading and empty states.

#### Integration
- **Backend**: No new API; ledger is client-side IndexedDB; sync pushes/pulls ledger entries via existing sync protocol.
- **Navigation**: Sidebar nav item "Ledger" (📜) at `/ledger`; page title "Ledger | BrewLedger"; description "Transaction history and audit trail".
- **Auth**: Route `requiresAuth: true`; LedgerRepository and ItemRepository.getContext() scope by org_id.

#### Documentation
- **Feature analysis**: `changes/ledger-view-console.md` (first and second iteration analysis, error handling follow-up).

### Settings Page

#### Subscription Management
- **Status Display**: Shows current subscription plan and status
- **Trial Information**: Displays trial end date and expiration status
- **Warning Banners**: Shows alerts for expired/cancelled subscriptions
- **Organization Info**: Displays organization name (read-only)

#### Settings Tabs
- **General**: Organization settings, display preferences
- **API Configuration**: Backend API status and sync settings
- **User Management**: List org users (Name, Email) and add new users (admin only). Uses GET /api/users for list and POST /api/auth/invite for create. Non-admins see a read-only message. No roles, last active, or edit/delete in UI. Console `UserService` and Settings users tab implement loading/error/empty states and inline add-user form (name, email, temporary password, confirm); mobile Settings retains the same invite flow for admins.
- **System Info**: Application version and database information

### Error Handling & Resilience

#### Error Handling Strategy
- **Try-Catch Blocks**: Comprehensive error handling in data loading
- **Error Display**: User-friendly error messages with retry buttons
- **Loading States**: Visual feedback during async operations
- **Graceful Degradation**: App continues to function with partial data

#### Error Recovery
- **Retry Mechanisms**: Manual retry buttons on error displays
- **Sync Error Handling**: Sync errors logged and displayed
- **Data Validation**: Validates data before display
- **Reference Checking**: Validates item/location references exist

### Performance Optimizations

#### Implemented Optimizations
1. **Token Validation Caching**: 1-minute cache reduces API calls
2. **Debounced Reloads**: Prevents rapid data reloads on sync
3. **Concurrent Load Prevention**: Flags prevent multiple simultaneous loads
4. **Timeline Height Calculation**: Dynamic height based on batch count
5. **Data Filtering**: Filters deleted items before display

#### Future Optimization Opportunities
1. **Virtual Scrolling**: For large inventory lists
2. **Lazy Loading**: Load dashboard data in chunks
3. **Memoization**: Cache computed values in Dashboard
4. **Server-side Filtering**: For very large datasets

### Security Considerations

#### Authentication Security
- **Token-based Auth**: Same security model as mobile app
- **Token Validation**: Validated on every protected route
- **Session Expiration**: Handled via router guards
- **Subscription Enforcement**: Subscription checks prevent unauthorized access

#### Data Security
- **Organization Isolation**: All queries filtered by org_id
- **Token Storage**: Secure localStorage storage (same as mobile app)
- **API Authorization**: All API calls use Authorization headers
- **XSS Protection**: Vue.js automatic escaping

### Integration Points

#### Shared Backend
- **API Endpoints**: Uses same `/api/auth/*`, GET `/api/users` (admin-only org-scoped list), and `/api/sync` endpoints
- **Authentication**: Same token-based authentication system
- **Sync Protocol**: Same operation-based sync protocol
- **Data Schema**: Same database schema (IndexedDB v10)

#### Data Synchronization
- **Bidirectional Sync**: Console app syncs with same backend as mobile app
- **Conflict Resolution**: Server-authoritative conflict resolution
- **Real-time Updates**: Changes from mobile app appear in console after sync
- **Offline Support**: Console app works offline with pending changes queue

### Known Limitations & Future Enhancements

#### Current Limitations
1. **Billing Page**: No dedicated billing page (redirects to settings)
1. **Multi-tab Sync**: No coordination between multiple console app tabs
2. **Performance**: Could benefit from virtual scrolling for large lists
3. **Error Boundaries**: No Vue error boundaries (relies on try-catch)

#### Future Enhancements
1. **Advanced Analytics**: Enhanced analytics dashboard
2. **Bulk Operations**: Desktop-optimized bulk edit capabilities
3. **Export Features**: Advanced export and reporting
4. **Multi-tab Coordination**: Sync coordination between tabs
5. **Real-time Updates**: WebSocket integration for instant updates

### Testing Considerations

#### Test Scenarios
1. **Authentication**: Login, logout, token expiration, subscription checks
2. **Sync**: Sync on login, sync errors, sync loop management
3. **Data Loading**: Empty states, error states, large datasets
4. **Timeline**: Empty timelines, single milestones, many batches
5. **Edge Cases**: Network failures, concurrent operations, deleted references

#### Integration Testing
- Test sync between console and mobile app
- Test subscription status propagation
- Test concurrent user operations
- Test offline/online transitions

### Deployment Considerations

#### Build Process
- **Vite Build**: Standard Vite build process
- **Port Configuration**: Runs on port 5174 (dev) or configured port (prod)
- **Static Assets**: Can be served from any web server
- **Environment Variables**: API_BASE_URL configurable

#### Production Deployment
- **Static Hosting**: Frontend can be hosted on CDN or static host
- **Backend Dependency**: Requires backend in `server/` running
- **CORS Configuration**: Backend must allow console app origin
- **HTTPS Required**: For production (Stripe webhooks require HTTPS)

### Documentation Updates

#### Code Documentation
- All repositories have same structure as mobile app
- Services follow same patterns as mobile app
- Composables provide reactive state management
- Views use Composition API with `<script setup>`

#### Architecture Documentation
- Console app documented in this analysis.md
- Full systems and implementation diagram: `docs/SYSTEMS-AND-IMPLEMENTATION-DIAGRAM.md` (Level 0–5: context, repository, stack, subsystems, key flows, UI/API map; changes and bugs mapping).
- Feature analysis document in `changes/console-app-integration-analysis.md`
- Feature analysis for systems diagram in `changes/systems-implementation-diagram.md`
- Router guard logic documented
- Sync service integration documented

### Conclusion

The BrewLedger Console app is now fully integrated with the authentication service, sync service, and all business logic repositories. It provides a desktop-optimized interface for brewery management while maintaining full data synchronization with the Capacitor mobile app through the shared backend in `server/`. The implementation includes comprehensive error handling, performance optimizations, and security measures consistent with the mobile app architecture.

---

## Milestone Templates System - Complete Implementation

### Overview

This feature replaces the previous preset milestones with hide/show by an org-level milestone template system. Organizations manage multiple named milestone templates (lists of milestones with labels and descriptions). When creating a batch, users assign a template; the template is snapshotted to the batch. Users can fully edit templates (add, remove, reorder, edit labels/descriptions). A default template mirrors the original 11 milestones. Batch status equals the last completed milestone's label. Hiding functionality has been removed entirely.

### Architecture

#### Data Model

**milestone_templates** (new syncable table):
- `id`, `org_id`, `updated_at`, `server_updated_at`, `version`, `sync_status`
- `data`: JSON `{ name, milestones: [{ id, label, description, sort_order, is_system? }] }`
- Milestone object: `id` (UUID), `label`, `description`, `sort_order` (no statusType); `is_system` (boolean, optional) marks the forced last “Production Complete” milestone (TTB).
- **Forced last milestone**: The repository always appends a single “Production Complete” milestone (`is_system: true`) at the end of the list on create/update. Before appending, any existing forced milestone(s) in the incoming list are stripped (by `label === 'Production Complete'` or `is_system === true`), so the stored list is always `[...userMilestones, Production Complete]` and never duplicated when the user adds milestones after it.

**Batches** (modified):
- **Add** `milestone_definitions`: Array snapshot `[{ id, label, description, sort_order }]` – copy of template at creation
- **Add** `milestone_template_id`: Optional reference (for display)
- **Remove** `hidden_milestones`

**batch_milestones** (modified):
- **Replace** `milestone_type` (string) with `milestone_definition_id` (string, references `id` in `batch.milestone_definitions`)
- **Keep** `batch_id`, `occurred_at`, `completed`, `org_id`, etc.
- Server accepts both `milestone_type` and `milestone_definition_id` for migration

#### Status Calculation

**Rule**: Status = the last milestone that has been checked off (by `sort_order`).
- Get completed milestones from `batch_milestones`
- Sort by `sort_order` from `batch.milestone_definitions`
- Status = label of the last (highest sort_order) completed milestone
- If no milestones completed: status = "PLANNED"

**Active vs closed batches**: A batch is "complete" when the last milestone in its `milestone_definitions` is checked off. Use this for dashboard filtering.

#### Repository Changes

**MilestoneTemplateRepository** (new, both apps):
- `getAll()`, `getById()`, `create()`, `update()`, `delete()`, `applyRemoteUpsert()`
- `ensureDefaultTemplate(orgId)` – creates "Default" template if none exists
- `DEFAULT_MILESTONES` – default 11 milestones (Knocked Out, Pitched, etc.)
- `LEGACY_TYPE_TO_INDEX` – maps legacy types to index for migration
- `PRODUCTION_COMPLETE_LABEL` – exported constant `'Production Complete'` for form use
- **Forced last milestone**: On create/update, incoming milestones are filtered to remove any with `label === PRODUCTION_COMPLETE_LABEL` or `is_system === true`; then exactly one forced “Production Complete” milestone is appended. This prevents duplicate forced milestones when the UI sends milestones with user-added items after the forced one.

**BatchMilestoneRepository** (both apps):
- **Remove** `DEFINITIONS`, `getVisibleMilestones`, `getVisibleDefinitions`
- **Add** `getDefinitionsForBatch(batch)` – returns `batch.milestone_definitions` or null
- **Change** `ensure(batchId, milestoneDefinitionId, occurredAt)` – uses `milestone_definition_id`
- **Change** `initForBatch(batchId, definitions, initialStatus, knockedOutAt)` – when status "BREWED", completes first milestone
- **Add** `mapLegacyMilestoneTypeToDefinitionId(batch, legacyType)` – for migration

**BatchRepository** (both apps):
- **Remove** `hideMilestone`, `showMilestone`, `getHiddenMilestones`
- **Add** template snapshot on `create()` – snapshots selected template to `batch.milestone_definitions`
- **Add** `getDefaultTemplateId()` – returns org default template
- **Change** `update()` – no status-to-milestone mapping; status set by UI when milestones change

#### Backend Validation

**Server** (`server/server.js`):
- `validateEntity('milestone_template', ...)` – requires `name` (string), `milestones` (array)
- `validateEntity('batch_milestone', ...)` – requires `batch_id` and either `milestone_definition_id` OR `milestone_type`
- `validateEntity('batch', ...)` – allows `milestone_definitions` (array), `milestone_template_id`; removes hidden_milestones validation
- `milestone_templates` table in `init_db.js`; processChange, fetchUpdates for `milestone_templates`

### UI Components

#### Milestone Templates Management (Mobile & Console)

**Location**: `platforms/brewledger-app/src/views/MilestoneTemplates.vue`, `MilestoneTemplateForm.vue` (mobile); `platforms/console/src/views/` (console)

**Features**:
- List org templates with Edit and Delete (block delete if only one)
- **Set as default** (console): "Set as default" shows an in-page success/error banner (no browser alert); banner auto-dismisses (4s success, 6s error) and has a dismiss button.
- Create template – name + milestones (add, remove, reorder, edit label/description)
- Edit template – full CRUD on milestones; **forced last “Production Complete” milestone** is read-only (label/description shown as text, “Required for TTB” badge; no edit/remove/move-down). “Add milestone” now always inserts **before** the forced one, move-down is blocked when the next row is forced, and form load normalizes older templates to restore the forced milestone to the final position. At least one user milestone with a label is required on save.
- Routes: `/milestone-templates`, `/milestone-templates/add`, `/milestone-templates/:id/edit`
- Settings link: "Milestone templates" under Configuration

#### BatchForm (Mobile)

**Location**: `platforms/brewledger-app/src/views/BatchForm.vue`

**Changes**:
- Added "Milestone Template" dropdown (default: Default template)
- Passes `milestone_template_id` to `BatchRepository.create()`
- On create, template is snapshotted to `batch.milestone_definitions`

#### BatchDetail Timeline (Mobile)

**Location**: `platforms/brewledger-app/src/views/BatchDetail.vue`

**Changes**:
- Uses `batch.milestone_definitions` instead of hardcoded DEFINITIONS
- **Removed** all hide/show milestone UI (hiddenMilestones, handleHideMilestoneClick, unhideMilestone)
- Toggle uses `milestone_definition_id`
- `computedStatus` = last completed milestone's label
- Status modal maps PLANNED/BREWED/etc. to milestone indices for bulk ensure/uncheck

#### MilestonePieChart (Console)

**Location**: `platforms/console/src/components/MilestonePieChart.vue`

**Changes**:
- Uses `batch.milestones` (merged with definitions) – each has `id`, `label`, `completed`
- **Removed** hidden milestones, hide/unhide, `allowHide` prop
- Sectors colored green if completed, gray if not
- Current status = last completed milestone label
- `sector-click` navigates to batch detail (if route exists)

#### Dashboard (Console)

**Location**: `platforms/console/src/views/Dashboard.vue`

**Changes**:
- Active batches = batches where last milestone not completed (not all milestones done)
- Merges `batch.milestone_definitions` with `batch_milestones` for display
- **Removed** hide/unhide handlers

### Migration

**Client migration** (`platforms/brewledger-app/src/utils/migrateMilestoneTemplates.js`, console equivalent):
- Runs when session is available (App.vue watch, console onMounted)
- `runMilestoneTemplatesMigration()`: For each org, ensure Default template; for each batch without `milestone_definitions`, backfill from Default and migrate `batch_milestones` from `milestone_type` to `milestone_definition_id`
- `migrateBatchIfNeeded(batch)`: Single-batch migration when loading BatchDetail

**Dexie v13** (mobile and console):
- Adds `milestone_templates` store
- Updates `batch_milestones` index from `milestone_type` to `milestone_definition_id`

### Sync

**milestone_templates**: Full sync (gather, send, apply, markAsSynced) like other entity tables. The server creates exactly one default milestone template per org at registration (new orgs only); clients no longer create the initial default. Client `ensureDefaultTemplate(orgId)` only ensures one template is marked default when templates already exist; when zero templates exist it returns without creating (sync delivers the server-created default). **Duplicate-on-login guard (mobile)**: After applying server milestone_templates updates, the mobile SyncService removes local templates that have the same `name` as a received template but a different `id`, so a locally-created "Default" (from migration before first sync) does not duplicate the server’s "Default". See `changes/milestone-templates-duplicate-fix.md`, `changes/server-default-milestone-template.md`.

**batch_milestones**: Now use `milestone_definition_id`; server accepts both for backward compatibility during migration.

### Feature Analysis

- Detailed analysis in `changes/milestone-templates-system-analysis.md`

### 14. Architecture & Risk Review (2026-02-11)

- **Scope**: Security, data integrity, scalability/ops; report-only (no code changes). Full write-up in `changes/architecture-risk-review-2026-02-11.md`.
- **Secret exposure**: Live Stripe keys and the public Discord webhook URL are committed; move to environment variables, rotate immediately, and proxy contact submissions with bot/rate controls to prevent abuse and PII leakage.
- **Accounting tokens**: QBO access/refresh tokens stored in SQLite without encryption and refreshed opportunistically; encrypt at rest (KMS/wrapping key), scope per-org, and serialize refresh to avoid token races.
- **Sync integrity gaps**: `batch_location` deletes/combine removals still do not sync, so vessel layouts diverge across devices; add delete-sync plus idempotency keys for ledger/volume adjustments to prevent duplicates during offline retries.
- **Scalability/ops**: Single SQLite backend risks lock contention and durability issues; enable WAL + backups or migrate to PostgreSQL, add per-org rate limits for sync-heavy endpoints, and health checks for DB locks.
- **Observability/PII**: Add structured logging with redaction/rotation for Stripe/QBO/contact payloads; document incident response for leaked keys/webhooks.

### 15. Sync Integrity & Idempotency (2026-02-11)

- **Scope**: Propagate batch_location deletions and prevent duplicate ledger/volume writes on retries. Details in `changes/sync-integrity-idempotency.md`.
- **Batch locations**: Soft-delete with `deleted_at` + version bump; getters exclude deleted rows; remote deletes purge local rows.
- **Idempotency keys**: `client_request_id` added on create for ledger entries and batch volume adjustments (mobile + console); server stores/dedupes via new columns and unique indexes (`ledger_entries`, `batch_volume_adjustments`), migration `server/migrate_client_request_id.js`.

## Bug Fixes

### Duplicate SyncService Import (January 28, 2026)

**Issue**: The mobile app (`platforms/brewledger-app/src/views/BatchDetail.vue`) had a duplicate import statement for `SyncService`, causing a Vue compiler error: `[vue/compiler-sfc] Identifier 'SyncService' has already been declared. (17:9)`.

**Fix**: Removed the duplicate import on line 442, keeping the original import on line 438. This resolves the compilation error and allows the mobile app to build successfully.

**Files Modified**:
- `platforms/brewledger-app/src/repositories/BatchRepository.js` - Added logic to uncheck CLOSED milestone when status changes away from 'CLOSED'
- `platforms/console/src/repositories/BatchRepository.js` - Same fix applied for consistency
- `platforms/brewledger-app/src/views/BatchDetail.vue` - Updated `toggleMilestone()` to refresh batch from DB after status update

**Edge Cases Handled**:
- Milestone already unchecked: Check prevents unnecessary update
- Milestone doesn't exist: Gracefully handles missing milestone
- Race conditions: Idempotent check ensures safe multiple calls
- Direct status changes: Fix applies to both milestone-based and direct status changes via `saveStatus()`

**Testing**: Verified that unchecking CLOSED milestone now correctly reverts batch status to the appropriate previous status based on other completed milestones.

**Documentation**: Detailed analysis in `changes/batch-status-revert-bug-fix.md`

### Batch Status Revert Bug (January 28, 2026)

**Issue**: Batch statuses stay marked as "CLOSED" even when the CLOSED milestone is unchecked. The status gets marked as CLOSED the first time the milestone is checked but doesn't revert when unchecked.

**Root Cause**: The `BatchRepository.update()` method only creates/checks milestones when moving TO certain statuses (e.g., status='CLOSED' → ensures CLOSED milestone is checked), but doesn't uncheck milestones when moving AWAY from them. When a user unchecked the CLOSED milestone, the status would update correctly, but if the status was changed directly or if there was a race condition, the CLOSED milestone could remain checked.

**Fix**: Added logic to `BatchRepository.update()` to uncheck milestones when status changes away from them:

```javascript
if (updates.status) {
  const oldStatus = current.status;
  const newStatus = updates.status;
  
  // Uncheck milestones when status changes away from them
  if (oldStatus === 'CLOSED' && newStatus !== 'CLOSED') {
    const closedMilestone = await db.batch_milestones
      .where('batch_id').equals(id)
      .filter(m => m.milestone_type === 'CLOSED')
      .first();
    if (closedMilestone && closedMilestone.completed) {
      await BatchMilestoneRepository.update(closedMilestone.id, { completed: false });
    }
  }
  
  // Ensure milestones when moving to certain statuses (existing logic)
  // ...
}
```

Additionally, updated `toggleMilestone()` in `BatchDetail.vue` to refresh batch from DB after status update to ensure we have the latest state.

**Files Modified**:
- `platforms/brewledger-app/src/views/BatchDetail.vue` - Removed duplicate `SyncService` import