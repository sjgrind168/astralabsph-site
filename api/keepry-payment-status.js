const SUPABASE_STATUS_URL =
  'https://dpcfmtzrqtkqhvifpdzm.supabase.co/functions/v1/payment-return-status';

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');

  if (req.method !== 'GET') {
    return res.status(405).json({ ready: false, paid: false, premium: false });
  }

  const paymentId = String(req.query?.payment_id || '');
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(paymentId)) {
    return res.status(400).json({ ready: false, paid: false, premium: false });
  }

  try {
    const url = new URL(SUPABASE_STATUS_URL);
    url.searchParams.set('payment_id', paymentId);
    url.searchParams.set('_', String(Date.now()));

    const upstream = await fetch(url, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      cache: 'no-store',
    });

    const data = await upstream.json().catch(() => ({}));
    return res.status(upstream.ok ? 200 : upstream.status).json({
      ready: data?.ready === true,
      paid: data?.paid === true,
      premium: data?.premium === true,
    });
  } catch {
    return res.status(502).json({ ready: false, paid: false, premium: false });
  }
}
