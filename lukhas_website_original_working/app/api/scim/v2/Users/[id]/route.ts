import { NextRequest, NextResponse } from 'next/server';

export async function GET(_: NextRequest, { params }: { params: { id: string }}) {
  // TODO: Fetch user by id from database
  return NextResponse.json({ 
    id: params.id, 
    userName: 'example@lukhas.ai',
    name: {
      givenName: 'Example',
      familyName: 'User'
    },
    emails: [{
      value: 'example@lukhas.ai',
      primary: true
    }],
    active: true,
    schemas: ['urn:ietf:params:scim:schemas:core:2.0:User']
  });
}

export async function PATCH(req: NextRequest, { params }: { params: { id: string }}) {
  const body = await req.json(); // { Operations: [...] }
  // TODO: Apply operations to user
  const updatedUser = {
    id: params.id,
    ...body,
    meta: {
      lastModified: new Date().toISOString()
    }
  };
  return NextResponse.json(updatedUser);
}

export async function DELETE(_: NextRequest, { params }: { params: { id: string }}) {
  // TODO: Deactivate/delete user
  console.log(`Deleting user ${params.id}`);
  return new NextResponse(null, { status: 204 });
}