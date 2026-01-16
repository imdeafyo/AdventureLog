# AdventureLog: Development Timeline & Origin Story

By: Sean Morley, Founder & Lead Developer

This is the timeline of **how AdventureLog came to be, how it kept surviving my terrible early design choices, and how it slowly learned to be useful**. I wrote this as a detailed, phase-by-phase story so contributors, users, and future-me can see what decisions were made, why, and what problems we hit (and fixed) along the way.

> TL;DR: started as _NextVenture_, learned web dev the hard way, resurrected as _AdventureLog_, switched stacks twice, survived an chaotic Reddit launch, grew through community requests, and today the project is very much alive.

## Quick roadmap

- **Phase 0 — Ideation & Prototyping:** March 2023 → July 2023  
  The seed. Lots of learning, lots of scrapped prototypes.
- **Phase 1 — AdventureLog, SvelteKit roots:** March 2024 → July 2024  
  Frontend-first, local-storage MVP, severe Docker struggles, file storage chaos, MinIO pain.
- **Phase 2 — Django saves the day:** July 2024 → August 2024  
  Backend matured quickly; REST API, Django admin, file storage sanity.
- **Phase 3 — Definition, Community Growth, and Integrations:** Sept 2024 → June 2025  
  Feature solidification, sharing, world data, Immich integration, big UX decisions.
- **Phase 4 — Solidification & Expansion:** June 2025 → Present  
  UI rebuild, rename of core concepts, activities/trails, heavy QoL and performance work.

## Phase 0 — Initial Ideation and Prototyping

**Dates:** March 2023 — July 2023

This phase was basically me being excited, naive, and wildly optimistic.

### What I planned

- Start as **NextVenture**: a curated list of national parks, cities, landmarks — places people check off. Simple premise, obvious joy.
- A focus on letting users mark where they've been, build a list of places to visit, and keep a little travel log.

### What actually happened

- I was learning the **React / Node / Express** (MERN) stack on the fly. Every problem felt like a mountain and every mountain required rewriting whole parts of the codebase once I learned better practices (it was not that enjoyable to be honest).
- I produced multiple small prototypes, each progressively less terrible than the last. Progress! But also lots of “why did I do that” moments.
- Burnout + humility set in: I needed a break to learn fundamentals rather than pile band-aids on a shaky codebase (yeah I didn't really learn a lot during that break either, but at least I wasn't actively writing bad code).

### Small but important pivots

- While on break I renamed the project to **AdventureLog** — it felt better, cleaner, and more fitting than the working title.
- I played with tiny experiments, tested UI ideas, and tried different stacks mentally so the next attempt wouldn’t be purely guesswork. I was very intrested in the project just lacking the right technical foundation.

### Takeaway

Phase 0 was less about shipping and more about surviving the learning curve. The project’s DNA (places, visits, memories) was clear; I just needed the right tools and patience to implement it.

## Phase 1 — Initial Development of AdventureLog (SvelteKit era)

**Dates:** March 2024 — July 2024  
**Versions:** v0.1.0-alpha → v0.3.1

This was the “frontend-first, learn-by-doing” era. SvelteKit won me because it’s delightful to write and let me prototype fast. I still use SvelteKit for the frontend today and love it.

### Core progress

- Built a single-page app MVP where adventures were stored in **localStorage**. Simple, demoable, and enough to prove the concept.
- Learned SvelteKit app structure, routing, and how to think in reactive UI.

### Auth and backend beginnings

- Implemented authentication with **Lucia** so users could create accounts and persist data beyond local storage. That transition felt like leveling up.
- Switched from local-only to a backend API using **SvelteKit’s API routes** to centralize storage and multi-device access.

### Deployment & DevOps pain

- Began containerizing everything: Dockerfiles (frontend & backend), `docker-compose`, and env variables. Took days of hair-pulling but I got a reliably deployable container. Victory was greatly needed at this point.
- File uploads became a major sticking point: SvelteKit had no baked-in file handling story. I experimented with a self-hosted S3-compatible solution — **MinIO**. It worked, but felt hacky: extra moving parts, weird integration edges, and a general “this isn’t elegant” feeling. I pretty much knew at this point I was walking down a dead-end path...

### Major decision to pivot

- The MinIO + SvelteKit upload situation (and the need for a more robust API/admin story) made me decide to **rewrite the backend in Django**. I started the backend from scratch with a fresh project layout and a clearer architecture plan. This felt like ripping off a bandage: painful but necessary.

### Lessons learned

- Rapid frontend iteration is fantastic for shaping UX, but for persistent data and file handling, I needed a backend that provided batteries-included features (auth, file storage, admin) — enter Django.

## Phase 2 — Django Backend & Early Stability

**Dates:** July 2024 — August 2024  
**Versions:** v0.4.0 → v0.6.0

After the SvelteKit experiment I rewired the backend into Django + Django REST Framework. This phase is where the project matured technically in a big way.

### Why Django?

- **Django’s admin**, built-in auth, and mature file handling made life dramatically easier. I could iterate on the API fast and manage the DB through a UI when debugging or testing. Django REST Framework allowed a clean separation between API and frontend.

### What changed (notably)

- Reused frontend SvelteKit components where possible, but the API endpoints were completely reworked to talk to Django.
- Switched file uploads from MinIO to Django’s file storage on the server filesystem — simpler and, honestly, a relief.
- Introduced **collections**, **lodgings**, **notes**, **checklists** — broadening the scope beyond “just places” into trip planning and trip context. (Restaurants were later pruned and replaced with transportation models for better clarity.)

### Stability and schema work

- One big database change (v0.5.1): I switched primary keys to **UUIDs** instead of auto-incrementing integers. That was scary but intentional: UUIDs make merging and scaling safer later on. Happily, it was done early — before many users existed — which avoided painful migrations later.

### Community & launch

- I drafted a release post for r/selfhosted and decided to ship _before_ college started. On **August 15, 2024** I posted it, and it blew up more than I dared hope: **~400 upvotes, 180+ comments**, and a surge of installs and conversations. The repo got a large influx of attention and traffic, the kind of validation that keeps a project alive through times of doubt.

### Immediate aftermath

- I spent the next week triaging issues, helping users deploy, and shipping fixes. It was a stressful but extremely educational crunch while simultaneously moving to college. That crunch was intense, but it was also the moment I learned how real user feedback shapes a project’s priorities.

### Takeaway

Switching to Django was the right move, it reduced friction, sped up backend feature development, and made the application more maintainable.

## Phase 3 — Defining AdventureLog & Community-Guided Growth

**Dates:** September 2024 — June 2025  
**Versions:** v0.7.0 → v0.10.0

This phase is about defining the product: what is AdventureLog, what is it not, and how do we make it useful for other people?

### Core feature evolution

- **Multiple visits per location:** Users wanted to track repeat trips to the same place. Adding visit history became central to the data model.
- **Collection sharing & permissions:** Collections could be shared with other accounts for collaborative trip planning, implementing the permission logic here was fiddly and involved a lot of debugging. But once it worked, collaboration felt genuinely useful.
- **World travel data:** Initially we were manually entering countries and regions. A generous contributor pointed to a JSON dataset with countries/regions/cities - integrating that made world travel features robust and maintainable. (City support came later.)
- **Categories & tags:** After debating categories vs tags, we leaned into categories as the primary organizational mechanism (with tags available as flexible metadata). Later, custom categories were added so users could create their own classification schemes.

### UX polish & identity

- Logo: I swapped out the placeholder Windows map emoji for a proper logo designed by a friend (thanks, Jacob!). It made the app look more “real” and brandable.
- Localization: Frontend got translations to make AdventureLog accessible to more users.
- Calendar view: added a calendar to visualize trips over time, another highly requested feature.

### Integrations & polish

- **Immich integration** (huge win): Sync photos from Immich to AdventureLog adventures. This solved the “where do my travel photos live?” problem for many self-hosters and reduced friction for users who already had an Immich instance.
- **Backend optimizations:** performance tweaks, PWA support, OIDC support for enterprise-friendly auth, and other server configurability options.

### Community milestones

- Docker image downloads crossed **100K** — a concrete, surreal milestone. GitHub stars crossed **1K** shortly after. These numbers matter because they mean people are using and relying on AdventureLog.
- Collections received “smart recommendations” — algorithmic suggestions for new locations to add to a collection based on existing entries. This added a bit of discovery and delight.

### Ops & deployment improvements

- Simplified deployment by removing an extra Nginx container. Instead the backend serves media via an internal Nginx proxy. Fewer containers made deployment easier for hobbyist hosts.

### Takeaway

Phase 3 is where AdventureLog stopped being “my little project” and started becoming a community-shaped tool. The roadmap was heavily guided by user requests, and that made the app both more useful and more fun to build.

## Phase 4 — Solidification & Expansion of the Core Platform

**Dates:** June 2025 — Present  
**Versions:** v0.11.0 → Present

Now the project focuses on _polish, robustness, and expanding the core platform_ rather than constantly changing directions.

### Primary themes

- **Solidifying core UX**: a major UI rebuild to improve accessibility, usability, and cohesion. The goal was not only to look nicer but to make features easier to discover and use.
- **Expanding travel tracking & trip planning**: deeper integrations, better activity support, and more ways to view and interact with your travel history.

### Notable changes & features

- **Rename: “adventures” → “locations”**: This semantic pivot helped clarify the data model. A _location_ is a place that can have multiple _visits_; collections are groups of locations for trip planning. The rename reduced user confusion and aligned the product to real-world mental models.
- **Activities & Trails**:
  - Activities: connect visits to activity providers (e.g., Strava imports) so users can show what they did at a location — not just that they were there.
  - Trails: link trail data either via a URL or by integrating with self-hosted platforms (like Wanderer). This enriches the outdoor-adventure use case.
- **File attachments & broader media options:** allow PDFs and other travel documents to be attached to locations/visits.
- **Server configurability & geocoding:** more options for self-hosted operators, plus an optional Google Maps integration for geocoding.
- **New Itineraries**: a reimagined trip planning experience that focuses on day-by-day plans rather than just collections of locations. Uses a drag-and-drop interface for easy itinerary building.

### Ongoing priorities

- Performance tuning and bug fixes continue to be the top priority — the fewer regressions, the more people trust the app.
- Accessibility improvements, better testing, and expanding integrations in a way that doesn’t bloat the core experience.

### Major community milestones

- Docker image downloads crossed **1 Million** — a huge milestone that reflects sustained interest and usage.

### Takeaway

This phase is about turning AdventureLog from “a promising tool” into “a dependable tool.” It’s less about big rewrites and more about incremental, meaningful improvements.

## Lessons, patterns, and a few thoughts

1. **Pick the right tool for the job**
   - The SvelteKit prototype phase taught me how fast UI iteration can progress. The Django rewrite taught me you can’t ignore backend primitives (auth, file handling, admin) if you want to ship a stable self-hosted app. Each stack had strengths, use them where they matter.

2. **Community feedback is gold**
   - The Reddit launch pushed the project into real usage. Responding to issues and user requests shaped core features more than any design doc ever could.

3. **Keep breaking changes reasonable**
   - UUIDs as primary keys were scary, but doing it early saved headaches. Plan big breaking changes early; avoid them once people rely on your software.

4. **Simplicity wins in deployment**
   - Removing extra containers and simplifying deployment options made AdventureLog more approachable for hobbyist hosts — which is the core audience.

5. **Iterate visibly**
   - Small, visible wins (better login flow, calendar, Immich sync) build momentum and community trust.

## Current state & what’s next

AdventureLog is alive, maintained, and focused on being the best self-hosted travel app it can be: accessible, performant, and useful for trip planning and personal travel history.

Writing this made me realize how much of AdventureLog’s identity came from mistakes, feedback, and stubbornness. It’s the result of learning, throwing away things that didn’t work, embracing tools that did, and listening to people who actually used it. I’m proud of how it’s evolved and excited for the next phase.

If you made it this far: thanks. If you want to help — issues, PRs, ideas, or design feedback are always welcome. The project is alive because of an amazing community of users and contributors!

— Sean
