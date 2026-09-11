# Cash Machine

Live dashboard for the Polymarket dry-run trading project.

**URL:** https://cash-machine-ezr.pages.dev

## Stack
- Astro 5 (SSR) on Cloudflare Pages
- Data in Cloudflare D1 (`cash-machine` database)
- Local state (`/root/polymarket/shadow_trades.json`, `costs.db`) syncs to D1 after each council run

## What it shows
- Paper balance, open positions, mode
- Council cost by day + recent council calls (model, trigger, cost)
- Rejected theses with decisions

## Development
```
pnpm install
pnpm dev
```

## Deploy
```
pnpm build
npx wrangler pages deploy dist --project-name cash-machine
```

Bindings are declared in `astro.config.mjs` and `wrangler.toml` (D1 database `eeb98259-0e2f-44a0-8683-470f3d614e3c`).