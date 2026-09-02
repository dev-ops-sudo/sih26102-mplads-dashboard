# SIH26102 MPLADS Intelligence Dashboard

Frontend-only React + Vite prototype for the SIH26102 MPLADS Intelligence and Risk Monitoring platform.

## What is included

- Professional responsive dashboard layout for Ministry, State, District, and Constituency officials.
- Mock data-driven KPI cards, filters, project list, detail drawer, alerts, charts, timeline, and intelligence panels.
- Level 2 anomaly detection, Level 3 explainable risk scoring, Level 4 investigation chat, and Level 5 predictive early warnings.
- Image intelligence comparison UI, agency intelligence, duplicate relationship visualization, geographic intelligence placeholder, search, and notification preview.
- Motion polish with count-up KPIs, reveal animations, drawer transitions, gauge animation, alert pulse, and `prefers-reduced-motion` support.

## Run locally

```bash
npm install
npm run dev
```

Then open the local URL shown in the terminal.

## Build

```bash
npm run build
```

## Replacing mock data later

All realistic mock data is isolated in `src/data/mockData.ts`. Replace the exported arrays and objects with API responses while keeping the same TypeScript shapes in `src/types.ts`, or add adapter functions that map backend responses into these shapes.
