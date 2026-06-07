import { NextRequest } from "next/server";
import { describe, expect, it, vi } from "vitest";
import { POST } from "./route";

const mocks = vi.hoisted(() => {
  return {
    duplicateCount: 0,
    mockInsert: vi.fn(),
  };
});

// Mock getServerAdminClient
vi.mock("@/lib/supabase-server", () => {
  const mockFrom = {
    select: vi.fn().mockImplementation((fields, options) => {
      if (options && options.count) {
        const mockChain = {
          eq: vi.fn().mockReturnThis(),
          gte: vi.fn().mockImplementation(() => Promise.resolve({ count: mocks.duplicateCount, error: null }))
        };
        // Bind methods to mock chain for chaining support
        mockChain.eq.mockReturnValue(mockChain);
        return mockChain;
      }
      return {
        single: vi.fn().mockResolvedValue({ data: { id: "mock-feedback-id-123" }, error: null })
      };
    }),
    insert: mocks.mockInsert
  };

  // Setup default insert mock behavior
  mocks.mockInsert.mockReturnValue({
    select: vi.fn().mockReturnValue({
      single: vi.fn().mockResolvedValue({
        data: { id: "mock-feedback-id-123" },
        error: null
      })
    })
  });

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

  it("returns 429 when duplicate feedback is sent within 5 minutes", async () => {
    mocks.duplicateCount = 1; // trigger rate limiter
    const req = new NextRequest("http://localhost/api/public/provisional-library/feedback", {
      method: "POST",
      body: JSON.stringify({
        provisional_id: "record-123",
        record_name: "Entity",
        feedback_type: "wrong_info",
        user_comment: "Duplicate comment"
      })
    });
    const res = await POST(req);
    expect(res.status).toBe(429);
    const data = await res.json();
    expect(data.error).toContain("trùng lặp hoặc gửi quá nhanh");

    mocks.duplicateCount = 0; // reset
  });

  it("rejects invalid provisional_id format", async () => {
    const req = new NextRequest("http://localhost/api/public/provisional-library/feedback", {
      method: "POST",
      body: JSON.stringify({
        provisional_id: "short", // too short (< 6)
        record_name: "Entity",
        feedback_type: "wrong_info",
        user_comment: "Valid comment"
      })
    });
    const res = await POST(req);
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toContain("provisional_id không hợp lệ");
  });

  it("ignores/does not insert injected admin status/patch fields", async () => {
    mocks.mockInsert.mockClear();
    mocks.mockInsert.mockReturnValue({
      select: vi.fn().mockReturnValue({
        single: vi.fn().mockResolvedValue({
          data: { id: "mock-feedback-id-123" },
          error: null
        })
      })
    });

    const req = new NextRequest("http://localhost/api/public/provisional-library/feedback", {
      method: "POST",
      body: JSON.stringify({
        provisional_id: "record-123",
        record_name: "Entity",
        feedback_type: "wrong_info",
        user_comment: "Valid comment",
        status: "approved", // injected admin field
        effective_status: "active", // injected patch field
        oracle_policy: "block" // injected policy field
      })
    });
    const res = await POST(req);
    expect(res.status).toBe(200);

    // Assert insert was called without the injected fields
    expect(mocks.mockInsert).toHaveBeenCalledWith(
      expect.objectContaining({
        provisional_id: "record-123",
        status: "pending" // Should default to pending, not "approved"
      })
    );
    expect(mocks.mockInsert).not.toHaveBeenCalledWith(
      expect.objectContaining({
        effective_status: "active",
        oracle_policy: "block"
      })
    );
  });
});
