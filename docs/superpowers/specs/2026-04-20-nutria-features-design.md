# NutrIA Feature Expansion — Design Spec

## Goal
Add four incremental features to NutrIA in priority order: bottom tab bar redesign, persistent user profile, food diary with weekly dashboard, and smart nutritional alerts in chat.

## Implementation Order (B — Incremental)
1. Bottom tab bar redesign
2. User profile panel
3. Food diary tab + weekly dashboard
4. Smart nutritional alerts in chat

---

## Feature 1: Bottom Tab Bar

### What changes
The existing top tab bar (`<nav class="tabs">`) is removed and replaced with a fixed bottom navigation bar. The four tabs are: Chat, Diario (new), Calculadora, Foto.

### Visual design
- Fixed to bottom of viewport (`position:fixed; bottom:0; left:0; right:0`)
- Background: `var(--surface)`, top border: `1px solid var(--border)`
- Each tab: icon only, no label text, 44px minimum tap target
- Active tab icon color: `var(--accent)` — inactive: `var(--muted)`
- `<body>` gets `padding-bottom` equal to bar height (~60px) so content is not obscured

### Icons (SVG inline)
- Chat: speech bubble path
- Diario: open book / notebook path
- Calculadora: calculator rectangle path
- Foto: camera path

### Tab order (left to right)
Chat · Diario · Calculadora · Foto

### Behavior
- Tapping an icon switches the active panel (same JS logic as current tabs)
- Active state toggled via `.active` class on the button
- Smooth opacity transition on switch (existing `fadeUp` keyframe)

---

## Feature 2: User Profile Panel

### Trigger
Tapping the existing profile button (`#prof-btn`) in the header opens the panel.

### UI
Slide-up sheet (same pattern as existing modals in the codebase). Contains:
- Nombre (text, optional)
- Edad (number, years)
- Peso (number, kg)
- Altura (number, cm)
- Sexo (segmented: Hombre / Mujer)
- Objetivo (segmented: Perder grasa / Mantener / Ganar músculo)
- "Guardar" button → saves and closes
- "Cerrar" button → closes without saving

### Persistence
Saved to `localStorage` key `nutria-profile` as JSON:
```json
{
  "nombre": "Mario",
  "edad": 25,
  "peso": 75,
  "altura": 178,
  "sexo": "hombre",
  "objetivo": "cut"
}
```

### Daily goal calculation (from profile)
Computed client-side using Mifflin-St Jeor + activity multiplier (same formula already in Calculadora tab). Stored in memory on page load from saved profile. Used by diary summary cards, chart goal line, and alerts.

### Chat integration
Profile data is merged into the `ctx` object sent with each `/api/chat` request so the AI personalises responses based on the user's goal and stats.

---

## Feature 3: Food Diary Tab + Weekly Dashboard

### New tab
A new `<div id="panel-diario" class="panel">` added to the HTML. New tab button (book icon) inserted second in the bottom bar.

### Panel structure (top to bottom)

#### Day navigator
`← 20 abr 2026 →` — arrows to navigate between days. Defaults to today.

#### Daily summary cards
Four cards in a 2×2 grid: Calorías, Proteína, Carbos, Grasa.
Each card shows `consumed / goal` and a progress bar.
Progress bar color: green (≤90%), orange (90–110%), red (>110%).
If no profile set, goal shows `—`.

#### Entry list
Scrollable list of food entries for the selected day.
Each row: food name · grams · kcal · delete (×) button.
Empty state: *"No hay entradas para este día"*.

#### Manual add form
- Text input: food name (lookup against local `calories_db`)
- Number input: grams (default 100)
- "Añadir" button → searches DB, adds entry, clears form
- If not found: inline error *"Alimento no encontrado"*

#### Weekly chart
Chart.js bar chart (CDN: `https://cdn.jsdelivr.net/npm/chart.js`).
X-axis: last 7 days. Y-axis: kcal consumed.
Horizontal dashed line: daily kcal goal from profile.
Colors follow `var(--accent)` palette.
Fallback if CDN unavailable: *"Gráfica no disponible"* text.

### localStorage schema
Key: `nutria-diary`
```json
{
  "2026-04-20": [
    { "nombre": "Arroz", "gramos": 150, "kcal": 195, "proteina": 3.6, "carbos": 43.5, "grasa": 0.5 }
  ]
}
```

### "Añadir al diario" button in chat
When `datos_locales` is non-empty in the API response, the server includes an `alimento_detectado` field. JS renders a small button below the bot message. Tapping it opens the add form pre-filled with the food name (100g default, editable).

Extended API response shape:
```json
{
  "respuesta": "...",
  "contexto": {},
  "alimento_detectado": { "nombre": "Arroz", "kcal": 130, "proteina": 2.4, "carbos": 29, "grasa": 0.3 }
}
```

---

## Feature 4: Smart Nutritional Alerts in Chat

### Conditions to show alerts
Both must be true:
1. `nutria-profile` exists in localStorage
2. Today's diary has ≥ 1 entry

### Alert logic (client-side)
After each AI response, compute today's totals vs goals:

| Condition | Level | Example |
|-----------|-------|---------|
| Nutrient ≥ 90% of goal | 🟢 green | "¡Proteína del día completada!" |
| Nutrient 50–90% of goal | 🟡 yellow | "Te faltan ~40g de proteína" |
| Nutrient < 50% of goal | 🔴 red | "Solo llevas el 30% de tu proteína" |
| Nutrient > 110% of goal | 🔴 red | "Has superado las calorías en ~200 kcal" |

One alert shown per response — worst offender first (excess kcal > deficit kcal > deficit protein > deficit carbs > deficit fat).

### UI
Small card appended below the bot message bubble. Left border colored by level. Smaller font than chat text. Updates naturally with each new message.

---

## Data Flow

```
localStorage[nutria-profile]
        │
        ├──► daily goal calculation (JS, on page load)
        │         ├──► diary summary cards
        │         ├──► weekly chart goal line
        │         └──► alert thresholds
        │
        └──► chat context (sent with each /api/chat request)

localStorage[nutria-diary]
        │
        ├──► diary entry list
        ├──► daily totals → summary cards
        ├──► weekly chart bars
        └──► alert current values
```

---

## Error Handling
- Food not found in DB: inline error, no entry added
- Chart.js CDN unavailable: text fallback shown
- localStorage unavailable (private browsing): features degrade gracefully, no crashes
- Profile missing: goals show `—`, alerts suppressed

---

## Out of Scope
- Cross-device sync (requires backend)
- Custom macro goals (always derived from profile formula)
- Push notifications
- Export to CSV
