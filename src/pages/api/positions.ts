// Server-side proxy: hides which Polymarket wallet is queried.
// The wallet address lives only in the WALLET_ADDRESS Pages env var.
const UPSTREAM = 'https://data-api.polymarket.com/positions';

export const prerender = false;

export async function GET({ request, locals }) {
  const wallet = locals.runtime?.env?.WALLET_ADDRESS;
  if (!wallet) {
    return new Response(JSON.stringify({ error: 'wallet not configured' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
  const url = new URL(request.url);
  const limit = Math.min(Number(url.searchParams.get('limit')) || 100, 200);

  try {
    const r = await fetch(`${UPSTREAM}?user=${wallet}&limit=${limit}`, {
      signal: AbortSignal.timeout(8000),
      headers: { 'User-Agent': 'cash-machine-site' },
    });
    if (!r.ok) {
      return new Response(JSON.stringify({ error: `upstream ${r.status}` }), {
        status: 502,
        headers: { 'Content-Type': 'application/json' },
      });
    }
    const body = await r.text();
    return new Response(body, {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=30',
      },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: 'upstream timeout' }), {
      status: 504,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
