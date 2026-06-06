import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { LocaleProvider } from "@/context/LocaleContext";
import { ThemeProvider } from "@/context/ThemeContext";
import OraclePanel from "./OraclePanel";

// Mock localStorage for ThemeProvider
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    clear: () => {
      store = {};
    },
  };
})();
Object.defineProperty(window, "localStorage", {
  value: localStorageMock,
});

function renderOraclePanel(ui: React.ReactNode) {
  return render(
    <ThemeProvider>
      <LocaleProvider locale="vi">
        {ui}
      </LocaleProvider>
    </ThemeProvider>
  );
}

describe("OraclePanel Feedback Flow", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    vi.restoreAllMocks();
    localStorageMock.clear();
    // Mock scrollIntoView since jsdom doesn't support it
    window.HTMLElement.prototype.scrollIntoView = vi.fn();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("does not render feedback button for the welcome message (index 0)", () => {
    renderOraclePanel(<OraclePanel chapterProgress={10} defaultOpen={true} />);
    
    // Welcome message is present
    expect(screen.getByText(/HỆ THỐNG ĐÃ KẾT NỐI/i)).toBeInTheDocument();
    
    // Feedback button should not be present
    expect(screen.queryByRole("button", { name: "Báo lỗi câu trả lời" })).not.toBeInTheDocument();
  });

  it("renders feedback button after oracle answers, allows opening and submitting feedback successfully", async () => {
    // 1. Mock the /api/oracle/ask response
    const mockAskResponse = {
      ok: true,
      json: async () => ({
        answer: "Tôi là Oracle, tôi biết mọi thứ về truyện.",
        source: "local_wiki",
      }),
    };

    // 2. Mock the /api/oracle/feedback response
    const mockFeedbackResponse = {
      ok: true,
      json: async () => ({
        success: true,
      }),
    };

    const fetchMock = vi.fn().mockImplementation((url) => {
      if (url.includes("/api/oracle/ask")) {
        return Promise.resolve(mockAskResponse);
      }
      if (url.includes("/api/oracle/feedback")) {
        return Promise.resolve(mockFeedbackResponse);
      }
      return Promise.reject(new Error("Unknown URL"));
    });
    global.fetch = fetchMock as typeof fetch;

    renderOraclePanel(<OraclePanel chapterProgress={10} defaultOpen={true} />);

    // Type a question and submit
    const input = screen.getByPlaceholderText(/đặt câu hỏi/i);
    const submitBtn = screen.getByRole("button", { name: /gửi/i });

    fireEvent.change(input, { target: { value: "Ai là nhân vật chính?" } });
    fireEvent.click(submitBtn);

    // Wait for the oracle answer to render
    await screen.findByText("Tôi là Oracle, tôi biết mọi thứ về truyện.");

    // "Báo lỗi câu trả lời" button should now be visible
    const reportBtn = screen.getByRole("button", { name: "Báo lỗi câu trả lời" });
    expect(reportBtn).toBeInTheDocument();

    // Click to open feedback form
    fireEvent.click(reportBtn);

    // Form should render feedback fields
    expect(screen.getByText("Báo lỗi câu trả lời RAG")).toBeInTheDocument();
    const commentArea = screen.getByPlaceholderText("Góp ý của bạn về câu trả lời...");
    const correctionArea = screen.getByPlaceholderText("Đề xuất sửa đổi thông tin đúng (nếu có)...");
    const sendBtn = screen.getByRole("button", { name: "Gửi phản hồi" });
    const cancelBtn = screen.getByRole("button", { name: "Hủy" });

    // Send button should be disabled when comment is empty
    expect(sendBtn).toBeDisabled();

    // Fill comment and correction
    fireEvent.change(commentArea, { target: { value: "Câu trả lời bị thiếu thông tin quan trọng." } });
    expect(sendBtn).not.toBeDisabled();

    fireEvent.change(correctionArea, { target: { value: "Nhân vật chính là Lâm Phong." } });

    // Select error type (e.g. "missing" - Thiếu thông tin)
    const selectType = screen.getByRole("combobox");
    fireEvent.change(selectType, { target: { value: "missing" } });

    // Submit the feedback
    fireEvent.click(sendBtn);

    // Verify API called with exact payload mapping
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(2);
    });

    const feedbackCall = fetchMock.mock.calls.find(call => call[0].includes("/api/oracle/feedback"));
    expect(feedbackCall).toBeDefined();
    
    const requestOptions = feedbackCall![1];
    expect(requestOptions?.method).toBe("POST");
    
    const requestBody = JSON.parse(requestOptions?.body as string);
    expect(requestBody).toEqual({
      question: "Ai là nhân vật chính?",
      answer: "Tôi là Oracle, tôi biết mọi thứ về truyện.",
      source: "local_wiki",
      citations: [],
      chapter_progress: 10,
      feedback_type: "missing",
      user_comment: "Câu trả lời bị thiếu thông tin quan trọng.",
      suggested_correction: "Nhân vật chính là Lâm Phong.",
    });

    // Success message should be shown
    await screen.findByText("Đã gửi góp ý. Cảm ơn bạn đã giúp cải thiện AI.");

    // Cancel / Close feedback section
    const successCancelBtn = screen.getByRole("button", { name: "Hủy" });
    fireEvent.click(successCancelBtn);

    // Form should disappear and "Báo lỗi câu trả lời" button should be visible again
    expect(screen.queryByText("Báo lỗi câu trả lời RAG")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Báo lỗi câu trả lời" })).toBeInTheDocument();
  });

  it("displays error message if submitting feedback fails, and can cancel", async () => {
    // 1. Mock /api/oracle/ask success
    const mockAskResponse = {
      ok: true,
      json: async () => ({
        answer: "Trả lời nháp.",
        source: "gemini",
      }),
    };

    // 2. Mock /api/oracle/feedback failure
    const mockFeedbackResponse = {
      ok: false,
      status: 500,
      json: async () => ({
        error: "Internal Server Error",
      }),
    };

    const fetchMock = vi.fn().mockImplementation((url) => {
      if (url.includes("/api/oracle/ask")) {
        return Promise.resolve(mockAskResponse);
      }
      if (url.includes("/api/oracle/feedback")) {
        return Promise.resolve(mockFeedbackResponse);
      }
      return Promise.reject(new Error("Unknown URL"));
    });
    global.fetch = fetchMock as typeof fetch;

    renderOraclePanel(<OraclePanel chapterProgress={25} defaultOpen={true} />);

    // Ask question
    const input = screen.getByPlaceholderText(/đặt câu hỏi/i);
    const submitBtn = screen.getByRole("button", { name: /gửi/i });
    fireEvent.change(input, { target: { value: "Test fail?" } });
    fireEvent.click(submitBtn);

    await screen.findByText("Trả lời nháp.");

    // Open form
    const reportBtn = screen.getByRole("button", { name: "Báo lỗi câu trả lời" });
    fireEvent.click(reportBtn);

    // Type comment
    const commentArea = screen.getByPlaceholderText("Góp ý của bạn về câu trả lời...");
    fireEvent.change(commentArea, { target: { value: "AI bịa chuyện." } });

    // Submit
    const sendBtn = screen.getByRole("button", { name: "Gửi phản hồi" });
    fireEvent.click(sendBtn);

    // Should display error message
    await screen.findByText("Chưa gửi được góp ý. Vui lòng thử lại.");

    // Click cancel to close
    const cancelBtn = screen.getByRole("button", { name: "Hủy" });
    fireEvent.click(cancelBtn);

    // Check that form is closed
    expect(screen.queryByText("Báo lỗi câu trả lời RAG")).not.toBeInTheDocument();
  });
});
