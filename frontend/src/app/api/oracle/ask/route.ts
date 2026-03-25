import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

/**
 * POST /api/oracle/ask
 * Proxies to the FastAPI AI Oracle backend.
 * The API key never reaches the browser — it lives in the backend .env.
 */
export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        if (!body.question || typeof body.question !== 'string' || body.question.trim().length < 5) {
            return NextResponse.json({ error: 'Câu hỏi không hợp lệ' }, { status: 400 });
        }

        // Forward to FastAPI backend — it holds the Gemini API key
        const res = await fetch(`${BACKEND_URL}/oracle/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Forward real IP for rate limiting
                'X-Forwarded-For': request.headers.get('x-forwarded-for') ?? '',
            },
            body: JSON.stringify({
                question: body.question.trim().slice(0, 500),
                chapter_progress: Math.max(1, Number(body.chapter_progress) || 1),
            }),
        });

        if (res.status === 429) {
            return NextResponse.json(
                { error: 'HỆ THỐNG ĐANG BỊ NHIỄU SÓNG. Thử lại vào ngày mai.' },
                { status: 429 }
            );
        }

        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            return NextResponse.json(
                { error: errorData.detail ?? 'Backend error' },
                { status: res.status }
            );
        }

        const data = await res.json();
        return NextResponse.json(data);

    } catch (error: any) {
        return NextResponse.json(
            { error: 'Mất kết nối với Oracle server.' },
            { status: 502 }
        );
    }
}
