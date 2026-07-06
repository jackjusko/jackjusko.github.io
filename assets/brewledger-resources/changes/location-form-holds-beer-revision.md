# Location Form: Holds Beer Revision (Desktop + Mobile)

## Summary

Both desktop and mobile LocationForm views were revised to add an introductory explanation of locations, a Yes/No question about whether the location holds finished beer products, and conditional TTB stage selection. When the user answers "No", the TTB stage defaults to cellar (bulk) and the stage dropdown is hidden.

## What Changed

### Desktop (platforms/console/src/views/LocationForm.vue)

- **Intro copy**: Added paragraph: "A location is just a spot in your facility where things are kept. Give it a name so you can track inventory there."
- **holdsBeer state**: New `ref(null)` for Yes/No; on edit, set to `true` when loading.
- **Yes/No question**: "Will this location hold any finished beer products?" with radio buttons (Yes/No).
- **Conditional TTB stage**: TTB stage dropdown only shown when `holdsBeer === true`.
- **Save logic**: If `holdsBeer === false`, payload uses `stage: 'cellar'`; on create, validation requires holdsBeer to be answered.
- **Helper text**: When stage dropdown is visible: "Choose the TTB stage that best matches where beer is stored here."

### Mobile (platforms/brewledger-app/src/views/LocationForm.vue)

- Same changes as desktop; uses `LOCATION_STAGE_LABELS` from LocationRepository for stage options.
- Removed unused `AuthService` import.

### Mobile LocationRepository (platforms/brewledger-app/src/repositories/LocationRepository.js)

- Exported `LOCATION_STAGE_LABELS` for consistency with console.

## Feature Analysis

### First pass

- **Edit mode**: When loading an existing location, `holdsBeer` is set to `true` so the TTB stage dropdown is shown. User can switch to "No" if the location does not hold beer (e.g. grain room).
- **Create mode**: User must answer Yes or No before submit; validation blocks save if unanswered.
- **Payload**: No schema change; API still receives `{ name, stage }`. Non-beer locations get `stage: 'cellar'`.
- **Settings → Locations tab**: Unchanged; bulk stage editor remains for existing locations.

### Second pass

- **Tutorial**: Tutorial step "Locations & TTB stage" copy may benefit from mentioning the holds-beer question. Optional follow-up.
- **Accessibility**: Radio buttons use proper labels; screen readers will announce the question and options.
- **Mobile radio styling**: Uses `text-blue-600` for focus ring (mobile app palette); console uses `text-primary-600` (warm accent). Both platforms remain consistent within their design systems.
- **Form state across toggles**: When user toggles holdsBeer from Yes→No→Yes, `form.stage` is not cleared; the dropdown shows the previous selection. Save logic correctly overrides stage to cellar only when holdsBeer is false at submit time. No change needed.
- **Edit flow**: Existing locations load with holdsBeer=true; user can switch to No to mark a repurposed location (e.g. cellar → grain room). Stage is saved as cellar. Correct.
