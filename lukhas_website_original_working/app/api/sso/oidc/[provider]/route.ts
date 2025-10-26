import { NextRequest, NextResponse } from 'next/server';
// Note: Install openid-client: npm install openid-client
// import { Issuer, generators } from 'openid-client';

const providers = {
  okta: process.env.OKTA_ISSUER,
  azure: process.env.AZURE_AD_ISSUER,
  google: process.env.GOOGLE_ISSUER,
} as const;

export async function GET(req: NextRequest, { params }: { params: { provider: keyof typeof providers }}) {
  const issuerUrl = providers[params.provider];
  if (!issuerUrl) return new NextResponse('Unknown provider', { status: 400 });

  // TODO: Uncomment when openid-client is installed
  // const issuer = await Issuer.discover(issuerUrl);
  // const client = new issuer.Client({
  //   client_id: process.env.OIDC_CLIENT_ID!,
  //   client_secret: process.env.OIDC_CLIENT_SECRET!,
  //   redirect_uris: [new URL(`/api/sso/oidc/${params.provider}/callback`, req.url).toString()],
  //   response_types: ['code']
  // });

  // const state = generators.state();
  // const nonce = generators.nonce();
  // const authUrl = client.authorizationUrl({
  //   scope: 'openid email profile',
  //   state, nonce
  // });

  // For now, return a placeholder
  const authUrl = `${issuerUrl}/authorize?client_id=${process.env.OIDC_CLIENT_ID}&redirect_uri=${encodeURIComponent(
    new URL(`/api/sso/oidc/${params.provider}/callback`, req.url).toString()
  )}&response_type=code&scope=openid+email+profile`;

  // TODO: persist state/nonce in session
  return NextResponse.redirect(authUrl);
}