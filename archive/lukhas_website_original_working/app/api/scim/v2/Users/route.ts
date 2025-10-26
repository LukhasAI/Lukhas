import { NextRequest, NextResponse } from 'next/server';

// Minimal SCIM skeleton — fill with your directory model & pagination
export async function GET(req: NextRequest) {
  const Resources: any[] = []; // TODO: Fetch users from database
  return NextResponse.json({ 
    Resources, 
    totalResults: Resources.length, 
    startIndex: 1, 
    itemsPerPage: Resources.length, 
    schemas: ['urn:ietf:params:scim:api:messages:2.0:ListResponse']
  });
}

export async function POST(req: NextRequest) {
  // Provision user
  const body = await req.json(); // { userName, name, emails, active, ... }
  // TODO: Create user in database
  const newUser = {
    ...body,
    id: 'user_' + Date.now(),
    meta: {
      resourceType: 'User',
      created: new Date().toISOString(),
      lastModified: new Date().toISOString()
    }
  };
  return NextResponse.json(newUser, { status: 201 });
}