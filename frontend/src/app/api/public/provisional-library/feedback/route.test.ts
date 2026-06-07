import { NextRequest } from "next/server";
import { describe, expect, it, vi } from "vitest";
import { POST } from "./route";

// Mock getServerAdminClient
vi.mock("@/lib/supabase-server", () => ({
  getServerAdminClient: vi.fn().mockResolvedValue({
    from: vi.fn().mockReturnValue({
      insert: vi.fn().mockReturnValue({
        select: vi.fn().mockReturnValue({
          single: vi.fn().mockResolvedValue({
            data: { id: "mock-feedback-id-123" },
            error: null
          })
        })
      })
    })
  })
}));

describe("Public Provisional Library Feedback API Route", () => {
  it("rejects missing provisional_id", async () => {
    const req = new NextRequest("http://localhost/api/public/provisional-library/feedback", {
      method: "POST",
      body: JSON.stringify({
        record_name: "Entity",
        feedback_type: "wrong_info",
        user_comment: "Correct comment"
      })
    });
    const res = await POST(req);
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toContain("provisional_id là bắt buộc");
  });

  it("rejects invalid feedback_type", async () => {
    const req = new NextRequest("http://localhost/api/public/provisional-library/feedback", {
      method: "POST",
      body: JSON.stringify({
        provisional_id: "record-1",
        record_name: "Entity",
        feedback_type: "invalid_type",
        user_comment: "Correct comment"
      })
    });
    const res = await POST(req);
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toContain("Loại feedback không hợp lệ");
  });

  it("rejects comment too short", async () => {
    const req = new NextRequest("http://localhost/api/public/provisional-library/feedback", {
      method: "POST",
      body: JSON.stringify({
        provisional_id: "record-1",
        record_name: "Entity",
        feedback_type: "wrong_info",
        user_comment: "ab"
      })
    });
    const res = await POST(req);
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toContain("quá ngắn");
  });

  it("accepts valid feedback and inserts into database", async () => {
    const req = new NextRequest("http://localhost/api/public/provisional-library/feedback", {
      method: "POST",
      body: JSON.stringify({
        provisional_id: "record-1",
        record_name: "Entity",
        feedback_type: "wrong_info",
        user_comment: "Bằng chứng này bị sai."
      })
    });
    const res = await POST(req);
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.ok).toBe(true);
    expect(data.feedback_id).toBe("mock-feedback-id-123");
  });
});
