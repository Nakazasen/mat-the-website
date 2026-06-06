import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import AdminFeedbackPage from "./page";

// Mock sessionStorage
const sessionStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();
Object.defineProperty(window, "sessionStorage", {
  value: sessionStorageMock,
});

describe("AdminFeedbackPage Dashboard", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    vi.restoreAllMocks();
    sessionStorageMock.clear();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("renders authentication token form initially", () => {
    render(<AdminFeedbackPage />);
    
    expect(screen.getByText("YÊU CẦU XÁC THỰC ADMIN")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Nhập X-Oracle-Feedback-Admin-Token...")).toBeInTheDocument();
    
    const verifyBtn = screen.getByRole("button", { name: "XÁC THỰC & TẢI PHẢN HỒI" });
    expect(verifyBtn).toBeInTheDocument();
    expect(verifyBtn).toBeDisabled();
  });

  it("enables the fetch button when token is entered", () => {
    render(<AdminFeedbackPage />);
    
    const input = screen.getByPlaceholderText("Nhập X-Oracle-Feedback-Admin-Token...");
    const verifyBtn = screen.getByRole("button", { name: "XÁC THỰC & TẢI PHẢN HỒI" });
    
    fireEvent.change(input, { target: { value: "test-token-123" } });
    
    expect(verifyBtn).not.toBeDisabled();
  });

  it("handles authentication failure and displays invalid token error", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({ error: "Forbidden: Invalid admin token" }),
    });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminFeedbackPage />);
    
    const input = screen.getByPlaceholderText("Nhập X-Oracle-Feedback-Admin-Token...");
    const verifyBtn = screen.getByRole("button", { name: "XÁC THỰC & TẢI PHẢN HỒI" });
    
    fireEvent.change(input, { target: { value: "wrong-token" } });
    fireEvent.click(verifyBtn);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    // Check request url and headers
    expect(fetchMock.mock.calls[0]?.[0]).toBe("/api/oracle/feedback/pending");
    const headers = fetchMock.mock.calls[0]?.[1]?.headers as Record<string, string>;
    expect(headers?.["X-Oracle-Feedback-Admin-Token"]).toBe("wrong-token");

    // Display error message
    await screen.findByText("Forbidden: Invalid admin token");
    expect(screen.queryByText("Đã xác thực Admin Token")).not.toBeInTheDocument();
  });

  it("loads and renders pending feedbacks when token authentication succeeds", async () => {
    const mockFeedbacks = [
      {
        id: "fb-1",
        question: "Hàn Phong là ai?",
        answer: "Hàn Phong là đoàn trưởng.",
        source: "local_wiki",
        chapter_progress: 15,
        feedback_type: "wrong",
        user_comment: "Thiếu tên đầy đủ.",
        suggested_correction: "Hàn Phong là Đoàn Trưởng Hàn Phong.",
        status: "pending",
        created_at: "2026-06-06T10:00:00Z",
      }
    ];

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockFeedbacks,
    });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminFeedbackPage />);
    
    const input = screen.getByPlaceholderText("Nhập X-Oracle-Feedback-Admin-Token...");
    const verifyBtn = screen.getByRole("button", { name: "XÁC THỰC & TẢI PHẢN HỒI" });
    
    fireEvent.change(input, { target: { value: "valid-token" } });
    fireEvent.click(verifyBtn);

    // Verify session verification bar is displayed
    await screen.findByText(/Đã xác thực Admin Token/i);
    expect(screen.getByText("1")).toBeInTheDocument(); // pending count

    // Verify item fields render
    expect(screen.getByText("Sai kiến thức")).toBeInTheDocument();
    expect(screen.getByText("Chương 15")).toBeInTheDocument();
    expect(screen.getByText("local_wiki")).toBeInTheDocument();
    expect(screen.getByText("Hàn Phong là ai?")).toBeInTheDocument();
    expect(screen.getByText("Hàn Phong là đoàn trưởng.")).toBeInTheDocument();
    expect(screen.getByText("Thiếu tên đầy đủ.")).toBeInTheDocument();
    expect(screen.getByText("Hàn Phong là Đoàn Trưởng Hàn Phong.")).toBeInTheDocument();

    // Verify reviewer inputs and actions are shown
    expect(screen.getByPlaceholderText("Viết ghi chú duyệt (tối đa 2000 ký tự)...")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "RESOLVE" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ACCEPT" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "REJECT" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "REVIEWED" })).toBeInTheDocument();
  });

  it("submits PATCH action successfully and removes resolved item from list", async () => {
    const mockFeedbacks = [
      {
        id: "fb-1",
        question: "Q1",
        answer: "A1",
        source: "cache",
        chapter_progress: 10,
        feedback_type: "missing",
        user_comment: "C1",
        suggested_correction: "Corr1",
        status: "pending",
        created_at: "2026-06-06T10:00:00Z",
      }
    ];

    // Mock first call GET /api/oracle/feedback/pending, second call PATCH /api/oracle/feedback/fb-1
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockFeedbacks,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ok: true, feedback_id: "fb-1", status: "resolved" }),
      });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminFeedbackPage />);
    
    // Auth
    const input = screen.getByPlaceholderText("Nhập X-Oracle-Feedback-Admin-Token...");
    const verifyBtn = screen.getByRole("button", { name: "XÁC THỰC & TẢI PHẢN HỒI" });
    fireEvent.change(input, { target: { value: "valid-token" } });
    fireEvent.click(verifyBtn);

    // Wait for render
    await screen.findByText("Q1");

    // Write reviewer note
    const noteArea = screen.getByPlaceholderText("Viết ghi chú duyệt (tối đa 2000 ký tự)...");
    fireEvent.change(noteArea, { target: { value: "Duyệt ok." } });

    // Click Resolve
    const resolveBtn = screen.getByRole("button", { name: "RESOLVE" });
    fireEvent.click(resolveBtn);

    // Verify PATCH fetch
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(2);
    });

    const patchCall = fetchMock.mock.calls[1];
    expect(patchCall?.[0]).toBe("/api/oracle/feedback/fb-1");
    
    const requestOptions = patchCall?.[1];
    expect(requestOptions?.method).toBe("PATCH");
    
    const headers = requestOptions?.headers as Record<string, string>;
    expect(headers?.["X-Oracle-Feedback-Admin-Token"]).toBe("valid-token");
    
    const requestBody = JSON.parse(requestOptions?.body as string);
    expect(requestBody).toEqual({
      status: "resolved",
      reviewer_note: "Duyệt ok.",
    });

    // Item should disappear from the list (leaving list empty)
    await screen.findByText("Không có báo lỗi pending nào cần xử lý.");
    expect(screen.queryByText("Q1")).not.toBeInTheDocument();
    
    // Displays success banner
    await screen.findByText("Đã cập nhật phản hồi thành công sang trạng thái: RESOLVED");
  });
});
