import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const AUTH_COOKIE = 'brand-explorer-auth'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  if (pathname === '/login' || pathname.startsWith('/api/') || pathname.startsWith('/_next/') || pathname.startsWith('/data/')) {
    return NextResponse.next()
  }

  const authCookie = request.cookies.get(AUTH_COOKIE)

  if (!authCookie || authCookie.value !== 'authenticated') {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('from', pathname)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
