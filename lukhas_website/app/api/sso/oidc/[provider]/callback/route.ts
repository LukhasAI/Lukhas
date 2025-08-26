import { NextRequest, NextResponse } from 'next/server';
// import { Issuer } from 'openid-client';
import { issueAccessToken } from '@/packages/auth/jwt';

export async function GET(req: NextRequest, { params }: { params: { provider: string }}) {
  const url = new URL(req.url);

  // TODO: Uncomment when openid-client is installed
  // const issuer = await Issuer.discover(process.env[`${params.provider.toUpperCase()}_ISSUER`]!);
  // const client = new issuer.Client({
  //   client_id: process.env.OIDC_CLIENT_ID!,
  //   client_secret: process.env.OIDC_CLIENT_SECRET!,
  //   redirect_uris: [new URL(`/api/sso/oidc/${params.provider}/callback`, req.url).toString()],
  //   response_types: ['code']
  // });

  // const tokenSet = await client.callback(url.origin + url.pathname, Object.fromEntries(url.searchParams));
  // const id = tokenSet.claims();

  // For now, mock the user data
  const id = {
    sub: 'user_' + Date.now(),
    email: 'sso@lukhas.ai',
    name: 'SSO User',
    org: params.provider
  };

  // TODO: Map id to org/user; enforce T4/T5; create session
  const access = await issueAccessToken({ sub: id.sub, org: id.org || 'default' });

  // Redirect to app with token
  return NextResponse.redirect(new URL(`/app?token=${access}`, req.url));
}
