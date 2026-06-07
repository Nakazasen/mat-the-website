import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import AdminProvisionalLibraryPage from "./page";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useRouter() {
    return {
      push: vi.fn(),
      refresh: vi.fn(),
    };
  },
  usePathname() {
    return "/admin/provisional-library";
  }
}));

describe("AdminProvisionalLibraryPage Dashboard", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("handles 401 Unauthorized and displays sign-in requirement UI", async () => {
    const fetchMock = vi.fn().mockImplementation((url) => {
      if (url.includes("stats=true")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ total: 0, high_confidence: 0, medium_confidence: 0 })
        });
      }
      return Promise.resolve({
        ok: false,
        status: 401,
        json: async () => ({ error: "Unauthorized: Vui lòng đăng nhập admin" }),
      });
    });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminProvisionalLibraryPage />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled();
    });

    // Displays authorization request
    await screen.findByText("YÊU CẦU XÁC THỰC ADMIN");
    expect(screen.getByText("Bạn cần đăng nhập bằng tài khoản Admin để truy cập trang này.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ĐẾN TRANG ĐĂNG NHẬP" })).toBeInTheDocument();
  });

  it("loads and renders provisional library records when API call succeeds", async () => {
    const mockStats = {
      total: 10,
      high_confidence: 6,
      medium_confidence: 4
    };

    const mockData = {
      items: [
        {
          id: "item-123",
          name: "Tinh thể zombie",
          type: "item",
          summary: "Vật phẩm dạng tinh thể chứa năng lượng.",
          evidence: [
            {
              chapter_number: 8,
              chapter_title: "Phân phối chiến lợi phẩm",
              chunk_index: 2,
              content_hash: "hash-8",
              preview: "Nhặt được một viên tinh thể zombie từ quái vật..."
            }
          ],
          confidence: 0.5,
          quality_class: "medium_confidence",
          status: "provisional",
          source: "story_chunks_auto_extract",
          feedback_score: 0,
          needs_review: false,
          chapter_numbers: [8],
          first_chapter: 8,
          last_chapter: 8,
          created_at: "2026-06-07T12:00:00Z"
        }
      ],
      total: 1,
      page: 1,
      page_size: 50
    };

    const fetchMock = vi.fn().mockImplementation((url) => {
      if (url.includes("stats=true")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockStats
        });
      }
      return Promise.resolve({
        ok: true,
        json: async () => mockData
      });
    });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminProvisionalLibraryPage />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled();
    });

    // 1. Render title “Thư viện tự động”.
    await screen.findByText("THƯ VIỆN TỰ ĐỘNG (PROVISIONAL)");

    // 2. Hiển thị badge “Provisional — chưa phải canon”.
    expect(screen.getByText(/Cảnh báo bản nháp \(Provisional\):/)).toBeInTheDocument();

    // 3. Render record có name/type/quality/confidence.
    expect(screen.getByText("Tinh thể zombie")).toBeInTheDocument();
    expect(screen.getAllByText("Vật phẩm / Tinh thể")[0]).toBeInTheDocument();
    expect(screen.getByText("Tin cậy trung bình")).toBeInTheDocument();
    expect(screen.getByText("0.5")).toBeInTheDocument();

    // 4. Evidence preview hiển thị chapter/content_hash/preview khi click.
    const expandBtn = screen.getByRole("button", { name: /XEM EVIDENCE/ });
    expect(expandBtn).toBeInTheDocument();
    fireEvent.click(expandBtn);

    await screen.findByText("Bằng chứng (Citation Evidence)");
    expect(screen.getByText("Chương 8: Phân phối chiến lợi phẩm")).toBeInTheDocument();
    expect(screen.getByText(/Nhặt được một viên tinh thể zombie/)).toBeInTheDocument();
    expect(screen.getByText(/hash: hash-8/)).toBeInTheDocument();

    // 5. Không có nút Apply to wiki.
    expect(screen.queryByRole("button", { name: /apply.*wiki/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /áp dụng/i })).not.toBeInTheDocument();

    // 6. Không có raw token input.
    expect(screen.queryByPlaceholderText(/token/i)).not.toBeInTheDocument();
  });
});
