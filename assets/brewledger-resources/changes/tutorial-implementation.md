# Tutorial Implementation (Brewer-Focused In-App Tour)

## Scope

- **Audience**: Brewers new to BrewLedger; no billing or sync demo (platform-usage only).
- **Platform**: Console web app first; each step includes an optional mobile callout where behavior differs.
- **Delivery**: One action per screen; "Why brewers care" expandable; "Got it" / "Skip for now"; progress bar; "Continue tour" when step already done on current route.

## Routes Touched

Tutorial steps are anchored to routes (and optional query):

| Step ID         | Route / context                    |
|-----------------|------------------------------------|
| welcome         | `/dashboard`                       |
| sign_in         | `/login`                           |
| brewery_info    | `/settings?tab=brewery`            |
| locations       | `/locations`                       |
| inventory_items | `/items`                           |
| receiving       | `/receive`                         |
| counts          | `/inventory`                       |
| transfers       | `/racking`                         |
| batches         | `/batches` (list only)             |
| recipes_beers   | `/recipes`                         |
| packaging       | `/batches/:id` (batch detail)      |
| removals        | `/removals`                        |
| ttb_form        | `/reports/ttb-form`                |
| users_roles     | `/settings?tab=users`              |
| reports_exports | `/reports`                         |
| support         | `/dashboard`                       |

## Safety and Assumptions

- **Protected items**: Tutorial does not perform destructive actions; default Finished Beer item delete is already blocked elsewhere.
- **System check**: Welcome step requires "Run quick check" (localStorage write/read) before "Start"; no cookies required.
- **Sign-in skip**: If user is already logged in, completing Welcome navigates to Brewery info (skip sign_in).
- **Persistence**: Progress is stored in `localStorage` under key `tutorial_progress_${orgId}_${userId}`; cleared on logout implicitly (different org/user).

## Codebase Hygiene

- **Structure**: Step definitions in `platforms/console/src/services/tutorial/tutorialSteps.js`; composable `useTutorial` in `composables/useTutorial.js`; UI in `components/tutorial/` (TutorialProgressBar, TutorialStepCard, TutorialShell).
- **State**: Centralized in composable; `markStepComplete`, `markSkipped`, `reset`, `passSystemCheck`; progress loaded/saved when org/user refs change.
- **Content**: Copy and route anchors live in `tutorialSteps.js`; no hardcoded strings in Vue templates for step body/title.
- **Integration**: App.vue provides `tutorial` and renders TutorialShell when session exists and not landing/blog; Dashboard injects `tutorial` and shows "Take the tour" when tutorial is not active.

## Optional Follow-Ups

- E2E tests: one happy-path per module; one TTB gap-fix flow.
- Unit tests: progress save/load and advance/skip guards.
- Accessibility: focus order, aria labels on tooltips/callouts, no timer-based advance.
- Media: lazy-load optional "Show me" GIF/video per step; placeholder ready in step config if needed.
