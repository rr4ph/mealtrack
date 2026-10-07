# Mealtrack: Working Context and Guardrails

## Mission and current priority

Mealtrack is a full-stack meal-planning and grocery-management app. Its core question is: **what can the user make from what they have, and what do they need to buy?**

The MVP priority is a reliable meal workflow: create meals, attach ingredients, view them, then move toward comparing missing ingredients with supermarket products. Product search, inventory, and store data support that goal; they are not an invitation to turn the project into a full shopping platform yet.

**Goal: ship the MVP.** Prefer small, complete, testable changes over architecture projects or feature expansion.

## Repository map

~~~
backend/
  database/             PostgreSQL schema and connection helper
  src/api/              FastAPI route modules
  src/classes/          Domain/data-access classes
  src/supermarkets/     Morrisons, Tesco, and Sainsbury's adapters
  src/utils/            geography, matching, enums, ingredient-type helpers
frontend/src/           React + TypeScript + Vite UI
tests/backend/          domain and supermarket-adapter tests
docs/                   domain model and ER-diagram source
~~~

There are existing uncommitted frontend changes, including the new meal screens. They are user work: do not overwrite, revert, reformat wholesale, or fold them into unrelated changes.

## Architecture

- **Frontend:** React 19, TypeScript, Vite, and plain CSS. It uses fetch directly; there is no router, state library, or component framework.
- **Backend:** Python + FastAPI. backend/src/main.py mounts all route modules below /api and permits http://localhost:5173 through CORS.
- **Persistence:** PostgreSQL via psycopg. backend/database/schema.sql is the schema source of truth. The classes under backend/src/classes contain the persistence behaviour used by the routes.
- **Provider layer:** Morrisons, Tesco, and Sainsbury's adapters implement the shared SupermarketClient abstraction and normalise data into Product and Shop types.

Keep this shape unless a requested feature genuinely needs a targeted change. Do not introduce a second API client, global store, routing library, ORM migration, authentication system, component/design system, or broad state-management rewrite for a small MVP change.

## Domain model and database

~~~
User 1--1 Inventory 1--* InventoryItem *--1 Product
User 1--* Meal 1--* Ingredient *--1 IngredientType 1--* Product
~~~

- users: username, password hash, optional postcode.
- user_inventories: exactly one inventory per user.
- products: normalised supermarket product, including external ID, optional ingredient type, price/unit price, brand, pack size, supermarket, and last price-update time.
- inventory_items: a quantity of a product in an inventory; unique per product/inventory pair.
- meals: a user's named meal plus portion and portion unit.
- ingredients: a meal's required ingredient type, quantity, and unit.
- ingredient_types: shared generic ingredients/categories joining recipes to suitable products.

Recipe ingredients intentionally point to ingredient_type_id rather than a specific product. Preserve that separation: recipes are generic, while the product layer selects supermarket products later.

## API conventions and implemented endpoints

All routes live below /api. Route modules define Pydantic request/response models. Query parameters use snake_case and identifiers use path parameters. Keep additions consistent; do not silently change established payloads.

### Users

- POST /api/users — create a user/inventory. Body: username, password, optional postcode.

### Meals and ingredients

- GET /api/meals?user_id={id} — list a user's meals.
- POST /api/meals — create: user_id, name, portion, portion_unit.
- PATCH /api/meals/{meal_id} — update using the same body.
- DELETE /api/meals/{meal_id}?user_id={id}.
- GET /api/meals/{meal_id}/ingredients?user_id={id}.
- GET /api/meals/{meal_id}/ingredients/{ingredient_id}?user_id={id}.
- POST /api/meals/{meal_id}/ingredients — ingredient_type_id, quantity, quantity_unit.
- PATCH /api/meals/{meal_id}/ingredients/{ingredient_id} — same ingredient body.
- POST /api/meals/{meal_id}/ingredients/{ingredient_id}/increase and /decrease — quantity body.
- DELETE /api/meals/{meal_id}/ingredients/{ingredient_id}.

### Ingredient types and inventory

- GET /api/ingredient-types; POST /api/ingredient-types (name).
- POST /api/ingredient-types/merge (kept_id, deleted_id).
- GET /api/inventory/{inventory_id}/items/{product_id}.
- POST /api/inventory/{inventory_id}/items — product_id, quantity, quantity_unit.
- POST /api/inventory/{inventory_id}/items/{product_id}/increase and /decrease — quantity.
- PATCH and DELETE /api/inventory/{inventory_id}/items/{product_id}.

### Products

- GET /api/products?query={text}&supermarket={all|morrisons|tesco|sainsburys}. all is the default.
- POST /api/products — persist a normalised product.

An explicitly requested provider failure returns the existing 502 response. In an all-provider search, failure of one provider is intentionally tolerated and successful providers still return results. Do not make search all-or-nothing.

## Supermarket providers

- Supported providers: **Morrisons, Tesco, and Sainsbury's**.
- Each has provider-specific parsing behind the shared client interface. Preserve that isolation and update adapter tests with parser changes.
- Tesco product search needs TESCO_API_KEY in the environment. Never commit or hard-code keys.
- Morrisons and Sainsbury's call public web endpoints, which can be brittle.
- Store lookup/distance utilities exist but are not public FastAPI routes and are not a completed UI flow. Do not invent one unless requested.

## UI direction and current screen state

The visual direction is intentionally dark and desktop-first: a fixed left navigation, slim top bar, card/panel layout, near-black/slate surfaces, light text, muted grey copy, and a restrained magenta/purple accent (the #d43cff family). Use compact uppercase eyebrow labels, simple glyph icons, and rounded panels/buttons. Do not replace it with a light theme, generic starter UI, component-library redesign, or wholesale CSS rewrite.

- **Dashboard:** landing view with live supermarket search. Inventory/missing-product cards remain placeholders until inventory and meal data are connected.
- **Meals:** fetches GET /api/meals?user_id=1, shows loading/error/empty/card states, opens CreateMeal, and selects a detail view. The hard-coded user ID is an intentional MVP shortcut; do not add auth just to remove it.
- **CreateMeal:** loads ingredient types, validates locally, creates a meal, then posts each ingredient. This sequential process can leave a meal created if a later ingredient fails; only address that narrowly if explicitly requested—do not start a transactional rewrite.
- **MealDetails:** loads the meal's ingredients and ingredient-type lookup, then resolves IDs to names. It displays quantities. Its Edit meal and Delete buttons are visual placeholders, not working actions yet.
- **CSS:** App.css is the active stylesheet and is large because the redesigned screens were built in place. It contains duplicate/overlapping Meal Details styles, particularly around the danger/delete control. If asked to clean it: retain the final intended rules, remove only redundancy after checking usages, and do not restyle unrelated screens.

## Known gaps and deliberately deferred work

- No login/session UI; frontend currently uses user ID 1 for MVP development.
- Inventory and Products pages are navigation placeholders; dashboard inventory/missing-product data is not wired.
- Meal-details edit/delete actions are not wired.
- No end-to-end recipe-to-inventory comparison or shopping-list generation yet.
- Store location/distance support is backend capability, not a completed user flow.
- Product persistence/caching, favourites, recommendations, and price-history UX are future work.
- No frontend test setup exists in this repository.

These are a backlog, not implied work. Implement only the next MVP slice the user asks for.

## Run and check

Use the existing scripts. Do not add manifests or toolchains unless explicitly asked.

~~~
# Frontend (from frontend/)
npm install
npm run dev
npm run build
npm run lint

# Backend (from repository root; Python environment and PostgreSQL configured)
python -m uvicorn backend.src.main:app --reload --port 8000

# Backend tests (from repository root)
python -m pytest tests/backend
~~~

The backend requires its Python dependencies (including FastAPI, psycopg, requests, and pytest for testing) and the existing PostgreSQL schema/connection setup. Never report that the app or tests are working unless they ran in the current session.

The handoff recorded **77 backend tests green**. This checkout currently contains 83 discovered test functions, so 77 is a previous verified baseline, not a current result. Rerun the test command before reporting the current status; never lower the baseline to make a change look green.

## Collaboration rules

- Be direct and practical: identify the relevant issue, make the focused fix, and explain it plainly.
- Work on **one issue at a time**. Do not bundle cleanup, future features, or unrelated improvements.
- When asked for a complete file, provide the complete file—not patch fragments or ellipses.
- Inspect relevant files before editing; preserve existing work and state any material assumption.
- Make only the requested change. Avoid speculative refactors, dependency churn, file moves/renames, or formatting sweeps.
- Verify proportionately with the smallest relevant check, and report exactly what ran and what did not.
- Do not overwrite uncommitted frontend work or use destructive Git commands unless explicitly requested.
- If a request materially expands scope (auth, routing, data-model redesign, provider replacement, new UI system), stop and ask first.

The standard is not theoretical perfection. It is a focused, coherent Mealtrack MVP that can be shipped.


