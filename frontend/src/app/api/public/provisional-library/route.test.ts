import { NextRequest } from "next/server";
import { describe, expect, it, vi } from "vitest";
import { GET } from "./route";

const { mockSelect, mockNeq, mockIn, mockEq, mockOr, mockOrder, mockLimit, mockRange, mockExecute } = vi.hoisted(() => ({
  mockSelect: vi.fn().mockReturnThis(),
  mockNeq: vi.fn().mockReturnThis(),
  mockIn: vi.fn().mockReturnThis(),
  mockEq: vi.fn().mockReturnThis(),
  mockOr: vi.fn().mockReturnThis(),
  mockOrder: vi.fn().mockReturnThis(),
  mockLimit: vi.fn().mockReturnThis(),
  mockRange: vi.fn().mockReturnThis(),
  mockExecute: vi.fn().mockResolvedValue({
    data: [
      { id: "id-1", name: "Tinh thể zombie", type: "crystal_core", quality_class: "high_confidence", status: "provisional", needs_review: false },
      { id: "id-2", name: "Băng Độc", type: "ability_skill", quality_class: "high_confidence", status: "provisional", needs_review: false }
    ],
    count: 2,
    error: null
  })
}));

// Mock getServerAdminClient
vi.mock("@/lib/supabase-server", () => {
  const mockQuery = {
    select: mockSelect,
    in: mockIn,
    neq: mockNeq,
    eq: mockEq,
    or: mockOr,
    order: mockOrder,
    limit: mockLimit,
    range: mockRange,
    then: vi.fn().mockImplementation((resolve) => {
      return mockExecute().then(resolve);
    })
  };

  const mockFrom = vi.fn().mockReturnValue(mockQuery);

  return {
    getServerAdminClient: vi.fn().mockResolvedValue({
      from: mockFrom
    })
  };
});

describe("Public Provisional Library GET API Route", () => {
  it("queries provisional_library table with quality_class, status, and needs_review filters", async () => {
    mockSelect.mockClear();
    mockNeq.mockClear();
    mockIn.mockClear();
    mockEq.mockClear();
    mockOr.mockClear();

    const req = new NextRequest("http://localhost/api/public/provisional-library?page=1&page_size=10");
    const res = await GET(req);
    expect(res.status).toBe(200);

    const data = await res.json();
    expect(data.items).toHaveLength(2);
    expect(data.items[0].name).toBe("Tinh thể zombie");

    // Verify filters
    expect(mockSelect).toHaveBeenCalledWith("*", { count: "exact" });
    expect(mockIn).toHaveBeenCalledWith("quality_class", ["high_confidence", "medium_confidence"]);
    expect(mockNeq).toHaveBeenCalledWith("status", "discard");
    expect(mockNeq).toHaveBeenCalledWith("needs_review", true);
  });

  it("does not expose private config or keys", async () => {
    const req = new NextRequest("http://localhost/api/public/provisional-library?page=1&page_size=10");
    const res = await GET(req);
    const data = await res.json();

    // Verify no secret fields are exposed in response
    const keys = Object.keys(data);
    expect(keys).not.toContain("supabase_key");
    expect(keys).not.toContain("token");
    expect(keys).not.toContain("service_role");
  });
});
