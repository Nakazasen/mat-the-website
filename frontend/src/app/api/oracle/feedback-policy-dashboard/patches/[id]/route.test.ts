import { NextRequest } from "next/server";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { PATCH } from "./route";

const mocks = vi.hoisted(() => {
  return {
    mockGetUser: vi.fn(),
    mockSingle: vi.fn(),
    mockUpdate: vi.fn(),
    mockDelete: vi.fn(),
    mockIn: vi.fn(),
  };
});

vi.mock("@/lib/supabase-server", () => {
  const mockSupabase = {
    auth: {
      getUser: mocks.mockGetUser,
    },
    from: vi.fn().mockImplementation((table) => {
      if (table === "provisional_library_effective_patches") {
        return {
          select: vi.fn().mockReturnThis(),
          eq: vi.fn().mockImplementation((col, val) => {
            if (col === "id") {
              return {
                single: mocks.mockSingle,
              };
            }
            return {
              single: vi.fn(),
            };
          }),
          update: mocks.mockUpdate,
        };
      }
      if (table === "oracle_cache") {
        const mockDelChain = {
          in: mocks.mockIn,
        };
        mocks.mockDelete.mockReturnValue(mockDelChain);
        return {
          select: vi.fn().mockReturnValue({
            data: [
              { id: 1, response: "Here is a response about Hàn Phong." },
              { id: 2, response: "Here is a response about Zombie." },
            ],
            error: null,
          }),
          delete: mocks.mockDelete,
        };
      }
      return {};
    }),
  };

  return {
    getServerAdminClient: vi.fn().mockResolvedValue(mockSupabase),
  };
});

describe("PATCH /api/oracle/feedback-policy-dashboard/patches/[id]", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.mockIn.mockResolvedValue({ error: null });
  });

  it("returns 401 if user is not logged in", async () => {
    mocks.mockGetUser.mockResolvedValue({ data: { user: null } });

    const req = new NextRequest("http://localhost/api/oracle/feedback-policy-dashboard/patches/patch-123", {
      method: "PATCH",
      body: JSON.stringify({ action: "disable", reviewer_note: "Test note" }),
    });

    const params = Promise.resolve({ id: "patch-123" });
    const res = await PATCH(req, { params });
    expect(res.status).toBe(401);
    const data = await res.json();
    expect(data.error).toBe("Unauthorized: Vui lòng đăng nhập admin");
  });

  it("returns 400 for invalid action", async () => {
    mocks.mockGetUser.mockResolvedValue({ data: { user: { id: "admin-1" } } });

    const req = new NextRequest("http://localhost/api/oracle/feedback-policy-dashboard/patches/patch-123", {
      method: "PATCH",
      body: JSON.stringify({ action: "invalid-action", reviewer_note: "Test note" }),
    });

    const params = Promise.resolve({ id: "patch-123" });
    const res = await PATCH(req, { params });
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toBe("Action must be 'disable' or 'restore'");
  });

  it("returns 400 if reviewer_note is not a string", async () => {
    mocks.mockGetUser.mockResolvedValue({ data: { user: { id: "admin-1" } } });

    const req = new NextRequest("http://localhost/api/oracle/feedback-policy-dashboard/patches/patch-123", {
      method: "PATCH",
      body: JSON.stringify({ action: "disable" }),
    });

    const params = Promise.resolve({ id: "patch-123" });
    const res = await PATCH(req, { params });
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toBe("Reviewer note must be a string");
  });

  it("returns 404 if patch is not found", async () => {
    mocks.mockGetUser.mockResolvedValue({ data: { user: { id: "admin-1" } } });
    mocks.mockSingle.mockResolvedValue({ data: null, error: { message: "Not found" } });

    const req = new NextRequest("http://localhost/api/oracle/feedback-policy-dashboard/patches/patch-123", {
      method: "PATCH",
      body: JSON.stringify({ action: "disable", reviewer_note: "Test note" }),
    });

    const params = Promise.resolve({ id: "patch-123" });
    const res = await PATCH(req, { params });
    expect(res.status).toBe(404);
    const data = await res.json();
    expect(data.error).toBe("Patch not found");
  });

  it("successfully disables a patch and clears related cache", async () => {
    mocks.mockGetUser.mockResolvedValue({ data: { user: { id: "admin-1" } } });
    mocks.mockSingle.mockResolvedValue({
      data: {
        id: "patch-123",
        target_name: "Hàn Phong",
        query_pattern: null,
        reason: "Initial reason",
        effective_status: "active",
      },
      error: null,
    });

    const mockEq = vi.fn().mockResolvedValue({ error: null });
    mocks.mockUpdate.mockReturnValue({
      eq: mockEq,
    });

    const req = new NextRequest("http://localhost/api/oracle/feedback-policy-dashboard/patches/patch-123", {
      method: "PATCH",
      body: JSON.stringify({ action: "disable", reviewer_note: "This is incorrect" }),
    });

    const params = Promise.resolve({ id: "patch-123" });
    const res = await PATCH(req, { params });
    expect(res.status).toBe(200);

    const data = await res.json();
    expect(data.ok).toBe(true);
    expect(data.status).toBe("disabled");
    expect(data.cache_cleared_count).toBe(1); // Only Hàn Phong matches response 1

    expect(mocks.mockUpdate).toHaveBeenCalledWith(
      expect.objectContaining({
        effective_status: "disabled",
        reason: "Initial reason | [Admin Disabled: This is incorrect]",
      })
    );
    expect(mockEq).toHaveBeenCalledWith("id", "patch-123");
    expect(mocks.mockDelete).toHaveBeenCalled();
    expect(mocks.mockIn).toHaveBeenCalledWith("id", [1]);
  });

  it("successfully restores a patch and clears related cache", async () => {
    mocks.mockGetUser.mockResolvedValue({ data: { user: { id: "admin-1" } } });
    mocks.mockSingle.mockResolvedValue({
      data: {
        id: "patch-123",
        target_name: null,
        query_pattern: "Zombie",
        reason: "Disabled | [Admin Disabled: Out of date]",
        effective_status: "disabled",
      },
      error: null,
    });

    const mockEq = vi.fn().mockResolvedValue({ error: null });
    mocks.mockUpdate.mockReturnValue({
      eq: mockEq,
    });

    const req = new NextRequest("http://localhost/api/oracle/feedback-policy-dashboard/patches/patch-123", {
      method: "PATCH",
      body: JSON.stringify({ action: "restore", reviewer_note: "Re-activating" }),
    });

    const params = Promise.resolve({ id: "patch-123" });
    const res = await PATCH(req, { params });
    expect(res.status).toBe(200);

    const data = await res.json();
    expect(data.ok).toBe(true);
    expect(data.status).toBe("active");
    expect(data.cache_cleared_count).toBe(1); // Only Zombie matches response 2

    expect(mocks.mockUpdate).toHaveBeenCalledWith(
      expect.objectContaining({
        effective_status: "active",
        reason: "Disabled | [Admin Disabled: Out of date] | [Admin Restored: Re-activating]",
      })
    );
    expect(mockEq).toHaveBeenCalledWith("id", "patch-123");
    expect(mocks.mockDelete).toHaveBeenCalled();
    expect(mocks.mockIn).toHaveBeenCalledWith("id", [2]);
  });
});
