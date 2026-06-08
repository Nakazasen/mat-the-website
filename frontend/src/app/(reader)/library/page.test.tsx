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
          source: "exact_concept_backfill_v1",
          feedback_score: 0,
          chapter_numbers: [8],
          first_chapter: 8,
          last_chapter: 8,
          created_at: "2026-06-07T12:00:00Z",
          effective_status: "trusted",
          oracle_policy: "allow"
        },
        {
          id: "item-disputed",
          name: "Dị năng hỏa hệ lỗi",
          type: "ability",
          summary: "Dị năng phun lửa.",
          evidence: [
            {
              chapter_number: 10,
              chapter_title: "Bí cảnh hỏa diệm",
              chunk_index: 1,
              content_hash: "hash-10",
              preview: "Phun lửa mạnh mẽ..."
            }
          ],
          confidence: 0.7,
          quality_class: "high_confidence",
          status: "provisional",
          source: "story_chunks_auto_extract",
          feedback_score: 5,
          chapter_numbers: [10],
          first_chapter: 10,
          last_chapter: 10,
          created_at: "2026-06-07T12:05:00Z",
          effective_status: "disputed",
          oracle_policy: "block"
        },
        {
          id: "item-patched-summary",
          name: "Vật phẩm hiệu chỉnh",
          type: "item",
          summary: "Tóm tắt gốc.",
          evidence: [],
          confidence: 0.8,
          quality_class: "high_confidence",
          status: "provisional",
          source: "story_chunks_auto_extract",
          feedback_score: 1,
          chapter_numbers: [11],
          first_chapter: 11,
          last_chapter: 11,
          created_at: "2026-06-07T12:10:00Z",
          effective_status: "trusted",
          oracle_policy: "allow",
          patch_type: "effective_summary",
          effective_summary: "Tóm tắt mới đã hiệu chỉnh hoàn toàn."
        }
      ],
      total: 3,
      page: 1,
      page_size: 20
    };

    const fetchMock = vi.fn().mockImplementation((url) => {
      if (url.includes("/api/public/provisional-library?")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockData
        });
      }
      return Promise.resolve({
        ok: true,
        json: async () => ({ ok: true, feedback_id: "feedback-123" })
      });
    });
    global.fetch = fetchMock as typeof fetch;

    render(<PublicProvisionalLibraryPage />);

    // Wait for retrieval load
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled();
    });

    // 1. Render title “Thư viện tự động”
    await screen.findByRole("heading", { name: "THƯ VIỆN TỰ ĐỘNG" });

    // 2. Render disclaimer warning
    expect(screen.getByText(/Đây là dữ liệu nháp \(provisional\)/)).toBeInTheDocument();

    // 3. Render item details
    expect(screen.getByText("Tinh thể zombie")).toBeInTheDocument();
    expect(screen.getAllByText("Vật phẩm / Tinh thạch")[0]).toBeInTheDocument();
    expect(screen.getByText("Tin cậy trung bình")).toBeInTheDocument();
    expect(screen.getByText("0.5")).toBeInTheDocument();
    expect(screen.getByText("Khái niệm trọng tâm")).toBeInTheDocument();

    // 3b. Render disputed item details & badges
    expect(screen.getByText("Dị năng hỏa hệ lỗi")).toBeInTheDocument();
    expect(screen.getByText("Đã bị cộng đồng/RAG hạ độ tin cậy")).toBeInTheDocument();

    // 3c. Render patched summary item & badge
    expect(screen.getByText("Vật phẩm hiệu chỉnh")).toBeInTheDocument();
    expect(screen.getByText("Tóm tắt đã được hiệu chỉnh")).toBeInTheDocument();
    expect(screen.getByText("Tóm tắt mới đã hiệu chỉnh hoàn toàn.")).toBeInTheDocument();

    // 4. Evidence expansion
    const expandBtn = screen.getAllByRole("button", { name: /XEM TRÍCH ĐOẠN/ })[0];
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

    // 7. Feedback inline form render
    const feedbackBtn = screen.getAllByRole("button", { name: /BÁO LỖI MỤC NÀY/ })[0];
    expect(feedbackBtn).toBeInTheDocument();
    fireEvent.click(feedbackBtn);

    // Form fields presence
    expect(screen.getByText("Báo lỗi / Góp ý mục: Tinh thể zombie")).toBeInTheDocument();
    expect(screen.getByText("Vui lòng mô tả lỗi cụ thể, tránh spam hoặc gửi nhiều lần cùng nội dung.")).toBeInTheDocument();

    const websiteInput = screen.getByLabelText("Website") as HTMLInputElement;
    expect(websiteInput).toBeInTheDocument();
    expect(websiteInput.value).toBe("");

    const selectType = screen.getByRole("combobox", { name: /loại lỗi/i }) as HTMLSelectElement;
    expect(selectType).toBeInTheDocument();
    expect(selectType.value).toBe("wrong_info");

    const commentInput = screen.getByPlaceholderText(/Nhập ý kiến đóng góp của bạn/i) as HTMLTextAreaElement;
    expect(commentInput).toBeInTheDocument();

    const correctionInput = screen.getByPlaceholderText(/Đề xuất thông tin sửa đổi/i) as HTMLTextAreaElement;
    expect(correctionInput).toBeInTheDocument();

    // Client side validation check (empty comment)
    const submitBtn = screen.getByRole("button", { name: /GỬI BÁO LỖI/ });
    fireEvent.click(submitBtn);
    expect(screen.getByText("Ý kiến đóng góp không được trống.")).toBeInTheDocument();

    // Client side validation check (short comment)
    fireEvent.change(commentInput, { target: { value: "hi" } });
    fireEvent.click(submitBtn);
    expect(screen.getByText("Ý kiến đóng góp quá ngắn (tối thiểu 3 ký tự).")).toBeInTheDocument();

    // Valid submit
    fireEvent.change(commentInput, { target: { value: "Bằng chứng này bị sai lệch." } });
    fireEvent.change(correctionInput, { target: { value: "Đề xuất sửa thành đúng chương 8." } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(2);
    });

    // Check payload passed to POST fetch
    const lastCall = fetchMock.mock.calls[1];
    expect(lastCall[0]).toBe("/api/public/provisional-library/feedback");
    const callOpts = lastCall[1];
    expect(callOpts.method).toBe("POST");
    const requestBody = JSON.parse(callOpts.body);
    expect(requestBody.provisional_id).toBe("item-789");
    expect(requestBody.record_name).toBe("Tinh thể zombie");
    expect(requestBody.feedback_type).toBe("wrong_info");
    expect(requestBody.user_comment).toBe("Bằng chứng này bị sai lệch.");
    expect(requestBody.suggested_correction).toBe("Đề xuất sửa thành đúng chương 8.");
    expect(requestBody.website).toBe(""); // honeypot is empty

    // Success thank you banner displays
    await screen.findByText(/Cảm ơn bạn đã gửi đóng góp ý kiến!/);
  });

  it("calls fetch with correct query params for Vật phẩm / Tinh thạch and Kỹ năng / Sách kỹ năng filters", async () => {
    const mockData = { items: [], total: 0, page: 1, page_size: 20 };
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve({
      ok: true,
      json: async () => mockData
    }));
    global.fetch = fetchMock as typeof fetch;

    render(<PublicProvisionalLibraryPage />);

    // 1. Select "Vật phẩm / Tinh thạch" filter
    const selectFilter = screen.getByRole("combobox", { name: /phân loại/i }) as HTMLSelectElement;
    fireEvent.change(selectFilter, { target: { value: "item_crystal" } });

    await waitFor(() => {
      // Check if fetch was called with type=item_crystal
      const lastCall = fetchMock.mock.calls[fetchMock.mock.calls.length - 1];
      expect(lastCall[0]).toContain("type=item_crystal");
    });

    // 2. Select "Kỹ năng / Sách kỹ năng" filter
    fireEvent.change(selectFilter, { target: { value: "skill" } });

    await waitFor(() => {
      // Check if fetch was called with type=skill
      const lastCall = fetchMock.mock.calls[fetchMock.mock.calls.length - 1];
      expect(lastCall[0]).toContain("type=skill");
    });
  });
});
