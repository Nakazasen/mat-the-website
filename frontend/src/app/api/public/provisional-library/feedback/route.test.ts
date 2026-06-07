import { NextRequest } from "next/server";
import { describe, expect, it, vi } from "vitest";
import { POST } from "./route";

// Mock getServerAdminClient
vi.mock("@/lib/supabase-server", () => {
  const mockFrom = {
    select: vi.fn().mockImplementation((fields, options) => {
      if (options && options.count) {
        return {
          eq: vi.fn().mockReturnThis(),
          gte: vi.fn().mockResolvedValue({ count: 0, error: null })
        };
      }
      return {
        single: vi.fn().mockResolvedValue({ data: { id: "mock-feedback-id-123" }, error: null })
      };
    }),
    insert: vi.fn().mockReturnValue({
      select: vi.fn().mockReturnValue({
        single: vi.fn().mockResolvedValue({
          data: { id: "mock-feedback-id-123" },
          error: null
        })
      })
    })
  };

  // Setup eq method chain mock for rate limiter count check
  const selectQueryMock = {
    eq: vi.fn().mockReturnThis(),
    gte: vi.fn().mockResolvedValue({ count: 0, error: null })
  };
  mockFrom.select.prototype = selectQueryMock;

  return {
    getServerAdminClient: vi.fn().mockResolvedValue({
      from: vi.fn().mockReturnValue(mockFrom)
    })
  };
});

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
        provisional_id: "record-123",
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
        provisional_id: "record-123",
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

  it("rejects comment too long", async () => {
    const longComment = "a".repeat(2001);
    const req = new NextRequest("http://localhost/api/public/provisional-library/feedback", {
      method: "POST",
      body: JSON.stringify({
        provisional_id: "record-123",
        record_name: "Entity",
        feedback_type: "wrong_info",
        user_comment: longComment
      })
    });
    const res = await POST(req);
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toContain("vượt quá giới hạn 2000 ký tự");
  });

  it("rejects comment with too many URLs", async () => {
    const req = new NextRequest("http://localhost/api/public/provisional-library/feedback", {
      method: "POST",
      body: JSON.stringify({
        provisional_id: "record-123",
        record_name: "Entity",
        feedback_type: "wrong_info",
        user_comment: "Check out http://link1.com and https://link2.org and http://link3.net"
      })
    });
    const res = await POST(req);
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toContain("chứa quá nhiều liên kết");
  });

  it("rejects repeated garbage comment", async () => {
    const req = new NextRequest("http://localhost/api/public/provisional-library/feedback", {
      method: "POST",
      body: JSON.stringify({
        provisional_id: "record-123",
        record_name: "Entity",
        feedback_type: "wrong_info",
        user_comment: "This is garbage aaaaaa!"
      })
    });
    const res = await POST(req);
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toContain("chứa nhiều ký tự lặp lại vô nghĩa");
  });

  it("rejects non-empty honeypot website", async () => {
    const req = new NextRequest("http://localhost/api/public/provisional-library/feedback", {
      method: "POST",
      body: JSON.stringify({
        provisional_id: "record-123",
        record_name: "Entity",
        feedback_type: "wrong_info",
        user_comment: "Valid comment here",
        website: "http://attacker.com"
      })
    });
    const res = await POST(req);
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toContain("Yêu cầu bị từ chối do nghi ngờ spam");
  });

  it("accepts valid feedback and inserts into database", async () => {
    const req = new NextRequest("http://localhost/api/public/provisional-library/feedback", {
      method: "POST",
      body: JSON.stringify({
        provisional_id: "record-123",
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
