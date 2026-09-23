import { createHash, X509Certificate } from 'node:crypto';
import { SignedDataVerifier, Environment } from '@apple/app-store-server-library';

// Isolated Node.js verification endpoint. Never writes entitlements or logs JWS.
// Supabase checks the returned transaction hash, identity, product and revocation
// before it can grant Keepry lifetime access.
export const config = { maxDuration: 60 };

const BUNDLE_ID = 'com.astralabs.keepry';
const PRODUCT_ID = 'keepry_premium_lifetime';
const ROOT_URLS = [
  'https://www.apple.com/appleca/AppleIncRootCertificate.cer',
  'https://www.apple.com/certificateauthority/AppleRootCA-G2.cer',
  'https://www.apple.com/certificateauthority/AppleRootCA-G3.cer',
];
let rootPromise;

function reply(res, status, body) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  return res.status(status).json(body);
}

async function appleRoots() {
  if (!rootPromise) {
    rootPromise = Promise.all(ROOT_URLS.map(async (url) => {
      const response = await fetch(url, { signal: AbortSignal.timeout(8_000), cache: 'no-store' });
      if (!response.ok) throw new Error('APPLE_CERT_FETCH_FAILED');
      const bytes = Buffer.from(await response.arrayBuffer());
      if (bytes.length < 250 || bytes.length > 16_384) throw new Error('APPLE_CERT_INVALID_SIZE');
      new X509Certificate(bytes);
      return bytes;
    })).catch((error) => {
      rootPromise = undefined;
      throw error;
    });
  }
  return rootPromise;
}

function safeUnverifiedEnvironment(jws) {
  // Routing only. The verifier independently authenticates the environment,
  // certificate chain and ES256 signature before any transaction is returned.
  const parts = jws.split('.');
  if (parts.length !== 3 || parts.some((part) => !part || !/^[A-Za-z0-9_-]+$/.test(part))) return null;
  const header = JSON.parse(Buffer.from(parts[0], 'base64url').toString('utf8'));
  if (header?.alg !== 'ES256' || !Array.isArray(header.x5c) || header.x5c.length !== 3 ||
    header.x5c.some((cert) => typeof cert !== 'string' || cert.length > 12000)) return null;
  const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString('utf8'));
  if (payload?.bundleId !== BUNDLE_ID || payload?.productId !== PRODUCT_ID) return null;
  return payload.environment === 'Production' ? Environment.PRODUCTION :
    payload.environment === 'Sandbox' ? Environment.SANDBOX : null;
}

export default async function handler(req, res) {
  if (req.method === 'GET') return reply(res, 200, { ready: true, service: 'keepry-apple-node-verifier', writes_entitlements: false });
  if (req.method !== 'POST') return reply(res, 405, { error: 'METHOD_NOT_ALLOWED' });
  if (String(req.headers['content-type'] || '').split(';')[0].trim() !== 'application/json') {
    return reply(res, 415, { error: 'JSON_REQUIRED' });
  }
  const jws = req.body?.signed_transaction;
  if (typeof jws !== 'string' || jws.length < 500 || jws.length > 20_000) {
    return reply(res, 400, { error: 'INVALID_JWS_FORMAT' });
  }
  let environment;
  try { environment = safeUnverifiedEnvironment(jws); } catch { environment = null; }
  if (!environment) return reply(res, 422, { error: 'UNRECOGNIZED_TRANSACTION' });

  const suppliedAppId = req.body?.app_apple_id;
  const appAppleId = Number.isSafeInteger(suppliedAppId) && suppliedAppId > 0 ? suppliedAppId : undefined;
  if (environment === Environment.PRODUCTION && !appAppleId) {
    return reply(res, 503, { error: 'PRODUCTION_APP_ID_NOT_CONFIGURED' });
  }
  try {
    const verifier = new SignedDataVerifier(
      await appleRoots(), environment === Environment.PRODUCTION,
      environment, BUNDLE_ID,
      environment === Environment.PRODUCTION ? appAppleId : undefined,
    );
    const verified = await verifier.verifyAndDecodeTransaction(jws);
    if (verified.bundleId !== BUNDLE_ID || verified.productId !== PRODUCT_ID ||
      verified.environment !== environment || !verified.transactionId ||
      verified.revocationDate != null) {
      return reply(res, 422, { error: 'TRANSACTION_NOT_ELIGIBLE' });
    }
    // Only small, verified, non-sensitive fields leave the Node service.
    return reply(res, 200, {
      verified: true,
      signed_transaction_sha256: createHash('sha256').update(jws).digest('hex'),
      bundleId: verified.bundleId,
      productId: verified.productId,
      environment: verified.environment,
      transactionId: String(verified.transactionId),
      originalTransactionId: String(verified.originalTransactionId || verified.transactionId),
      purchaseDate: verified.purchaseDate,
      revocationDate: verified.revocationDate ?? null,
    });
  } catch (error) {
    // Never reflect raw Node/Apple exceptions, certificate material, or JWS.
    const retryable = error?.status === 2 ||
      /APPLE_CERT_FETCH_FAILED|fetch failed|timeout|ETIMEDOUT/i.test(String(error?.message || ''));
    return reply(res, retryable ? 503 : 422,
      { error: retryable ? 'APPLE_VERIFIER_TEMPORARILY_UNAVAILABLE' : 'APPLE_VERIFICATION_FAILED' });
  }
}
