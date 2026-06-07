import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import PublicProvisionalLibraryPage from "./page";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useRouter() {
    return {
      push: vi.fn(),
      refresh: vi.fn(),
    };
  },
  usePathname() {
    return "/library";
  }
}));

// Mock @/context/ThemeContext
vi.mock("@/context/ThemeContext", () => ({
  useTheme() {
    return {
      theme: "dark",
      fontFamily: "sans",
      fontSize: 18,
      setTheme: vi.fn(),
      setFontSize: vi.fn(),
      setFontFamily: vi.fn(),
    };
  }
}));

describe("PublicProvisionalLibraryPage", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("loads and renders provisional library records for public view when API succeeds", async () => {
    const mockData = {
      items: [
        {
          id: "item-789",
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
          chapter_numbers: [8],
          first_chapter: 8,
          last_chapter: 8,
          created_at: "2026-06-07T12:00:00Z"
        }
      ],
      total: 1,
      page: 1,
      page_size: 20
    };

    const fetchMock = vi.fn().mockImplementation(() => {
      return Promise.resolve({
        ok: true,
        json: async () => mockData
      });
    });
    global.fetch = fetchMock as typeof fetch;

    render(<PublicProvisionalLibraryPage />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled();
    });

    // 1. Render title “Thư viện tự động”
    await screen.findByRole("heading", { name: "THƯ VIỆN TỰ ĐỘNG" });

    // 2. Render disclaimer warning
    expect(screen.getByText(/Đây là dữ liệu nháp \(provisional\)/)).toBeInTheDocument();

    // 3. Render item details
    expect(screen.getByText("Tinh thể zombie")).toBeInTheDocument();
    expect(screen.getAllByText("Vật phẩm / Tinh thể")[0]).toBeInTheDocument();
    expect(screen.getByText("Tin cậy trung bình")).toBeInTheDocument();
    expect(screen.getByText("0.5")).toBeInTheDocument();

    // 4. Evidence expansion
    const expandBtn = screen.getByRole("button", { name: /XEM TRÍCH ĐOẠN/ });
    expect(expandBtn).toBeInTheDocument();
    fireEvent.click(expandBtn);

    await screen.findByText("Trích đoạn minh chứng (Citation Evidence)");
    expect(screen.getByText("Chương 8: Phân phối chiến lợi phẩm")).toBeInTheDocument();
    expect(screen.getByText(/Nhặt được một viên tinh thể zombie/)).toBeInTheDocument();

    // 5. No Apply to wiki or edit buttons
    expect(screen.queryByRole("button", { name: /apply/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /áp dụng/i })).not.toBeInTheDocument();

    // 6. No token input
    expect(screen.queryByPlaceholderText(/token/i)).not.toBeInTheDocument();
  });
});
