import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

/**
 * GET /api/wiki/character?name=...&chapter=...
 * Proxies to the FastAPI backend wiki search endpoint.
 * The chapter param is used server-side to filter out spoiler data.
 */
export async function GET(request: NextRequest) {
    const { searchParams } = new URL(request.url);
    const name = searchParams.get('name');
    const chapter = searchParams.get('chapter') ?? '9999';
    const locale = searchParams.get('locale') ?? 'vi';

    if (!name || name.trim().length < 2) {
        return NextResponse.json({ error: 'Invalid character name' }, { status: 400 });
    }

    try {
        const params = new URLSearchParams({ name: name.trim(), chapter, locale });
        const res = await fetch(`${BACKEND_URL}/wiki/character?${params}`, {
            next: { revalidate: 300 }, // Cache 5 minutes per character
        });

        if (!res.ok) {
            // Character not found is a soft-fail — return null, not error
            if (res.status === 404) {
                return NextResponse.json(null, { status: 200 });
            }
            return NextResponse.json({ error: 'Backend error' }, { status: res.status });
        }

        const data = await res.json();
        return NextResponse.json(data);
    } catch {
        // Network error — return null gracefully so tooltip can still render 
        return NextResponse.json(null, { status: 200 });
    }
}
