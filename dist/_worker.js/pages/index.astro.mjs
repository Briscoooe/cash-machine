globalThis.process ??= {}; globalThis.process.env ??= {};
import { e as createComponent, k as renderHead, r as renderTemplate, h as createAstro } from '../chunks/astro/server_ayzMwmTg.mjs';
/* empty css                                 */
export { renderers } from '../renderers.mjs';

const $$Astro = createAstro();
const prerender = false;
const $$Index = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$Index;
  let state = { mode: "\u2014", started: "\u2014", paper_balance: "\u2014" };
  let trades = [], rejected = [], costs_daily = [], runs_recent = [];
  try {
    const db = Astro2.locals.runtime.env.DB;
    const q = async (sql) => (await db.prepare(sql).all()).results;
    state = Object.fromEntries((await q("SELECT k,v FROM state")).map((r) => [r.k, r.v]));
    trades = await q("SELECT * FROM trades ORDER BY ts_utc DESC");
    rejected = await q("SELECT * FROM rejected ORDER BY ts_utc DESC");
    costs_daily = await q("SELECT * FROM daily_totals ORDER BY date_utc DESC");
    runs_recent = await q("SELECT ts_utc, model, trigger, cost_usd FROM council_runs ORDER BY ts_utc DESC LIMIT 15");
  } catch (e) {
    console.error("D1 read error", e);
  }
  const totalCost = costs_daily.reduce((a, d) => a + d.total_cost_usd, 0);
  const money = (n) => "$" + Number(n).toFixed(2);
  return renderTemplate`<html data-astro-cid-j7pv25f6> <head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cash Machine — Polymarket Dry Run</title>${renderHead()}</head> <body data-astro-cid-j7pv25f6> <h1 data-astro-cid-j7pv25f6>Cash Machine <span class="badge" data-astro-cid-j7pv25f6>${state.mode}</span></h1> <p class="muted" data-astro-cid-j7pv25f6>Polymarket dry run · started ${state.started?.slice?.(0, 10) || state.started} · wallet <code data-astro-cid-j7pv25f6>${state.wallet?.slice?.(0, 10) || ""}…</code></p> <div class="cards" data-astro-cid-j7pv25f6> <div class="card" data-astro-cid-j7pv25f6><div class="l" data-astro-cid-j7pv25f6>Paper balance</div><div class="v" data-astro-cid-j7pv25f6>${money(state.paper_balance)}</div></div> <div class="card" data-astro-cid-j7pv25f6><div class="l" data-astro-cid-j7pv25f6>Open positions</div><div class="v" data-astro-cid-j7pv25f6>${trades.filter((t) => t.status === "open").length}</div></div> <div class="card" data-astro-cid-j7pv25f6><div class="l" data-astro-cid-j7pv25f6>Council spend</div><div class="v" data-astro-cid-j7pv25f6>${money(totalCost)}</div></div> </div> <h2 data-astro-cid-j7pv25f6>Open positions</h2> ${trades.length === 0 ? renderTemplate`<p class="empty muted" data-astro-cid-j7pv25f6>None — scans run every 10 minutes</p>` : renderTemplate`<table data-astro-cid-j7pv25f6><tr data-astro-cid-j7pv25f6><th data-astro-cid-j7pv25f6>Market</th><th data-astro-cid-j7pv25f6>Side</th><th data-astro-cid-j7pv25f6>Size</th><th data-astro-cid-j7pv25f6>Entry</th><th data-astro-cid-j7pv25f6>Date</th></tr> ${trades.map((t) => renderTemplate`<tr data-astro-cid-j7pv25f6><td data-astro-cid-j7pv25f6>${t.market}</td><td data-astro-cid-j7pv25f6>${t.side}</td><td data-astro-cid-j7pv25f6>${money(t.size_usd)}</td><td data-astro-cid-j7pv25f6>${t.entry_price}</td><td class="muted" data-astro-cid-j7pv25f6>${t.ts_utc?.slice?.(0, 10)}</td></tr>`)} </table>`} <h2 data-astro-cid-j7pv25f6>Council cost by day</h2> <table data-astro-cid-j7pv25f6><tr data-astro-cid-j7pv25f6><th data-astro-cid-j7pv25f6>Date</th><th data-astro-cid-j7pv25f6>Cost</th><th data-astro-cid-j7pv25f6>Calls</th></tr> ${costs_daily.map((d) => renderTemplate`<tr data-astro-cid-j7pv25f6><td data-astro-cid-j7pv25f6>${d.date_utc}</td><td data-astro-cid-j7pv25f6>${money(d.total_cost_usd)}</td><td data-astro-cid-j7pv25f6>${d.run_count}</td></tr>`)} </table> <h2 data-astro-cid-j7pv25f6>Rejected theses</h2> ${rejected.length === 0 ? renderTemplate`<p class="empty" data-astro-cid-j7pv25f6>None yet</p>` : renderTemplate`<table data-astro-cid-j7pv25f6><tr data-astro-cid-j7pv25f6><th data-astro-cid-j7pv25f6>Thesis</th><th data-astro-cid-j7pv25f6>Decision</th><th data-astro-cid-j7pv25f6>Date</th></tr> ${rejected.map((r) => renderTemplate`<tr data-astro-cid-j7pv25f6><td data-astro-cid-j7pv25f6>${r.thesis?.slice?.(0, 120)}</td><td class="muted" data-astro-cid-j7pv25f6>${r.decision}</td><td class="muted" data-astro-cid-j7pv25f6>${r.ts_utc?.slice?.(0, 10)}</td></tr>`)} </table>`} <h2 data-astro-cid-j7pv25f6>Recent council calls</h2> <table data-astro-cid-j7pv25f6><tr data-astro-cid-j7pv25f6><th data-astro-cid-j7pv25f6>When</th><th data-astro-cid-j7pv25f6>Model</th><th data-astro-cid-j7pv25f6>Trigger</th><th data-astro-cid-j7pv25f6>Cost</th></tr> ${runs_recent.map((r) => renderTemplate`<tr data-astro-cid-j7pv25f6><td class="muted" data-astro-cid-j7pv25f6>${r.ts_utc?.slice?.(0, 16).replace("T", " ")}</td><td data-astro-cid-j7pv25f6>${r.model}</td><td class="muted" data-astro-cid-j7pv25f6>${r.trigger}</td><td data-astro-cid-j7pv25f6>$${r.cost_usd?.toFixed?.(4)}</td></tr>`)} </table> </body></html>`;
}, "/root/cash-machine/src/pages/index.astro", void 0);

const $$file = "/root/cash-machine/src/pages/index.astro";
const $$url = "";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Index,
  file: $$file,
  prerender,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
