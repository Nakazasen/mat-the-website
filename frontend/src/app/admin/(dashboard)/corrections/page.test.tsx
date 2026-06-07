import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import AdminCorrectionsPage from "./page";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useRouter() {
    return {
      push: vi.fn(),
    };
  },
}));

describe("AdminCorrectionsPage Dashboard", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("handles 401 Unauthorized and displays sign-in requirement UI", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ error: "Unauthorized: Vui lòng đăng nhập admin" }),
    });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminCorrectionsPage />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    expect(fetchMock.mock.calls[0]?.[0]).toBe("/api/oracle/corrections/pending?status=draft");

    // Displays authorization request
    await screen.findByText("YÊU CẦU XÁC THỰC ADMIN");
    expect(screen.getByText("Bạn cần đăng nhập bằng tài khoản Admin để truy cập trang này.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ĐẾN TRANG ĐĂNG NHẬP" })).toBeInTheDocument();
  });

  it("loads and renders pending corrections when API call succeeds", async () => {
    const mockCorrections = [
      {
        id: "corr-1",
        feedback_id: "fb-1",
        entity_name: "Đoàn Trưởng Hàn Phong",
        correction_type: "entity_profile",
        proposed_content: JSON.stringify({
          entity_type: "character",
          priority: "high",
          summary: "Đoàn trưởng đội dọn dẹp.",
          content: "Là nhân vật chính trong truyện."
        }),
        evidence: [
          {
            chapter_number: 1,
            chapter_title: "Mở đầu",
            chunk_index: 0,
            preview: "Hàn Phong đứng nhìn thành phố đổ nát."
          }
        ],
        status: "draft",
        reviewer_note: "Cần kiểm tra thêm.",
        created_at: "2026-06-06T10:00:00Z",
        updated_at: "2026-06-06T10:00:00Z"
      }
    ];

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCorrections,
    });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminCorrectionsPage />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    // Verify entity name and props render
    await screen.findByText("Đoàn Trưởng Hàn Phong");
    expect(screen.getByText(/Tổng cộng:/)).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument(); // Count

    // Verify properties
    expect(screen.getByText("Hồ sơ thực thể")).toBeInTheDocument();
    expect(screen.getByText("character")).toBeInTheDocument();
    expect(screen.getByText("high")).toBeInTheDocument();
    expect(screen.getByText("Đoàn trưởng đội dọn dẹp.")).toBeInTheDocument();
    expect(screen.getByText("Là nhân vật chính trong truyện.")).toBeInTheDocument();

    // Verify evidence
    expect(screen.getByText("Chương 1 : Mở đầu")).toBeInTheDocument();
    expect(screen.getByText(/Hàn Phong đứng nhìn thành phố đổ nát/)).toBeInTheDocument();

    // Verify reviewer inputs and actions are shown
    expect(screen.getByPlaceholderText("Viết ghi chú duyệt (tối đa 2000 ký tự)...")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "RESOLVE" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ACCEPT" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "REJECT" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "REVIEWED" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "NEEDS MORE INFO" })).toBeInTheDocument();

    // Verify there is NO button/text to apply to wiki directly or tokens input
    expect(screen.queryByRole("button", { name: /apply.*wiki/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /áp dụng.*wiki/i })).not.toBeInTheDocument();
    expect(screen.queryByPlaceholderText(/token/i)).not.toBeInTheDocument();
  });

  it("submits PATCH action successfully and removes item from list", async () => {
    const mockCorrections = [
      {
        id: "corr-1",
        feedback_id: null,
        entity_name: "Trương Khởi",
        correction_type: "entity_profile",
        proposed_content: JSON.stringify({
          entity_type: "character",
          summary: "Cơ phó trực thăng.",
        }),
        evidence: [],
        status: "draft",
        reviewer_note: "",
        created_at: "2026-06-06T10:00:00Z",
        updated_at: "2026-06-06T10:00:00Z"
      }
    ];

    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockCorrections,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ok: true, correction_id: "corr-1", status: "approved" }),
      });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminCorrectionsPage />);

    // Wait for initial load
    await screen.findByText("Trương Khởi");

    // Write note
    const noteArea = screen.getByPlaceholderText("Viết ghi chú duyệt (tối đa 2000 ký tự)...");
    fireEvent.change(noteArea, { target: { value: "Đồng ý hồ sơ này." } });

    // Click Accept
    const acceptBtn = screen.getByRole("button", { name: "ACCEPT" });
    fireEvent.click(acceptBtn);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(2);
    });

    const patchCall = fetchMock.mock.calls[1];
    expect(patchCall?.[0]).toBe("/api/oracle/corrections/corr-1");

    const options = patchCall?.[1];
    expect(options?.method).toBe("PATCH");

    // Client must NOT send ORACLE_FEEDBACK_ADMIN_TOKEN directly to browser endpoint
    const headers = options?.headers as Record<string, string>;
    expect(headers?.["X-Oracle-Feedback-Admin-Token"]).toBeUndefined();

    const body = JSON.parse(options?.body as string);
    expect(body).toEqual({
      status: "accepted",
      reviewer_note: "Đồng ý hồ sơ này."
    });

    // Item is removed
    await screen.findByText("Không có bản nháp tri thức nào khớp với bộ lọc.");
    expect(screen.queryByText("Trương Khởi")).not.toBeInTheDocument();
  });
});
