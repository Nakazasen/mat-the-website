import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import AdminWikiCandidatesPage from "./page";
import AdminNav from "../../AdminNav";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useRouter() {
    return {
      push: vi.fn(),
      refresh: vi.fn(),
    };
  },
  usePathname() {
    return "/admin/wiki-candidates";
  }
}));

// Mock Supabase admin client for AdminNav
vi.mock("@/lib/supabase-admin", () => ({
  createAdminClient() {
    return {
      auth: {
        getSession: vi.fn().mockResolvedValue({ data: { session: null } }),
        signOut: vi.fn(),
      }
    };
  }
}));

describe("AdminWikiCandidatesPage Dashboard", () => {
  const originalFetch = global.fetch;
  const originalNavigator = global.navigator;

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    global.fetch = originalFetch;
    global.navigator = originalNavigator;
  });

  it("handles 401 Unauthorized and displays sign-in requirement UI", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ error: "Unauthorized: Vui lòng đăng nhập admin" }),
    });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminWikiCandidatesPage />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    expect(fetchMock.mock.calls[0]?.[0]).toBe("/api/oracle/wiki-candidates");

    // Displays authorization request
    await screen.findByText("YÊU CẦU XÁC THỰC ADMIN");
    expect(screen.getByText("Bạn cần đăng nhập bằng tài khoản Admin để truy cập trang này.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ĐẾN TRANG ĐĂNG NHẬP" })).toBeInTheDocument();
  });

  it("loads and renders wiki candidates when API call succeeds", async () => {
    const mockCandidates = [
      {
        correction_id: "corr-123",
        entity_name: "Tinh thể zombie",
        entity_type: "Vật phẩm",
        summary: "",
        content: "",
        aliases: ["Tinh thể", "Zombie core"],
        evidence: [
          {
            chapter_number: 734,
            chapter_title: "Phủ vải lụa lên đồ đao",
            chunk_index: 8,
            preview: "Tiếng nói chuyện vẫn trầm đều, giấy tờ xào xạc..."
          }
        ],
        source: "rag_corrections",
        status: "needs_human_fill",
        human_review_required: true,
        notes: "Generated from approved rag_corrections; not applied to wiki_entries."
      }
    ];

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCandidates,
    });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminWikiCandidatesPage />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    // 1. Page title renders correctly
    await screen.findByText("ỨNG VIÊN WIKI ORACLE");

    // 2. Candidate name renders
    expect(screen.getByText("Tinh thể zombie")).toBeInTheDocument();

    // 3. Evidence list renders
    expect(screen.getByText("Chương 734 : Phủ vải lụa lên đồ đao")).toBeInTheDocument();
    expect(screen.getByText(/Tiếng nói chuyện vẫn trầm đều/)).toBeInTheDocument();

    // 4. Aliases render
    expect(screen.getByText("Tinh thể")).toBeInTheDocument();
    expect(screen.getByText("Zombie core")).toBeInTheDocument();

    // 5. Empty summary/content displays badge
    expect(screen.getByText("Cần người duyệt điền nội dung")).toBeInTheDocument();

    // 6. Verification of status badge
    expect(screen.getByText("Cần điền thêm (Needs Fill)")).toBeInTheDocument();

    // 7. Verification that NO "Apply to wiki" or DB write options are exposed
    expect(screen.queryByRole("button", { name: /apply.*wiki/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /áp dụng/i })).not.toBeInTheDocument();

    // 8. Verification that no raw token input is present
    expect(screen.queryByPlaceholderText(/token/i)).not.toBeInTheDocument();
  });

  it("allows local changes to summary/content and copies JSON payload", async () => {
    const mockCandidates = [
      {
        correction_id: "corr-123",
        entity_name: "Tinh thể zombie",
        entity_type: "Vật phẩm",
        summary: "",
        content: "",
        aliases: [],
        evidence: [],
        source: "rag_corrections",
        status: "needs_human_fill",
        human_review_required: true,
        notes: "test notes"
      }
    ];

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCandidates,
    });
    global.fetch = fetchMock as typeof fetch;

    const mockWriteText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(global, "navigator", {
      value: {
        clipboard: {
          writeText: mockWriteText
        }
      },
      writable: true
    });

    render(<AdminWikiCandidatesPage />);

    await screen.findByText("Tinh thể zombie");

    // Edit summary
    const summaryInput = screen.getByPlaceholderText("Nhập tóm tắt một câu của thực thể...");
    fireEvent.change(summaryInput, { target: { value: "Tóm tắt mới từ admin." } });

    // Edit content
    const contentInput = screen.getByPlaceholderText("Nhập chi tiết về thực thể, vai trò, thuộc tính...");
    fireEvent.change(contentInput, { target: { value: "Chi tiết đầy đủ từ admin." } });

    // Copy JSON payload
    const copyBtn = screen.getByRole("button", { name: "COPY CANDIDATE JSON" });
    fireEvent.click(copyBtn);

    await waitFor(() => {
      expect(mockWriteText).toHaveBeenCalledTimes(1);
    });

    const copiedJSON = JSON.parse(mockWriteText.mock.calls[0]?.[0]);
    expect(copiedJSON.summary).toBe("Tóm tắt mới từ admin.");
    expect(copiedJSON.content).toBe("Chi tiết đầy đủ từ admin.");
    expect(copiedJSON.status).toBe("ready_for_review"); // Status is updated dynamically!
  });

  it("calls backend API with mapped proposed_content when clicking Save Draft", async () => {
    const mockCandidates = [
      {
        correction_id: "corr-123",
        entity_name: "Tinh thể zombie",
        entity_type: "Vật phẩm",
        summary: "",
        content: "",
        aliases: ["Tinh thể"],
        evidence: [],
        source: "rag_corrections",
        status: "needs_human_fill",
        human_review_required: true,
        notes: "test notes"
      }
    ];

    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockCandidates,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ok: true, correction_id: "corr-123", status: "approved" }),
      });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminWikiCandidatesPage />);

    await screen.findByText("Tinh thể zombie");

    // Edit summary & content
    const summaryInput = screen.getByPlaceholderText("Nhập tóm tắt một câu của thực thể...");
    fireEvent.change(summaryInput, { target: { value: "Tóm tắt mới từ admin." } });

    const contentInput = screen.getByPlaceholderText("Nhập chi tiết về thực thể, vai trò, thuộc tính...");
    fireEvent.change(contentInput, { target: { value: "Chi tiết đầy đủ từ admin." } });

    // Click Save Draft
    const saveBtn = screen.getByRole("button", { name: "LƯU BẢN NHÁP" });
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(2);
    });

    const patchCall = fetchMock.mock.calls[1];
    expect(patchCall?.[0]).toBe("/api/oracle/corrections/corr-123");

    const options = patchCall?.[1];
    expect(options?.method).toBe("PATCH");

    const body = JSON.parse(options?.body as string);
    expect(body.status).toBe("accepted");
    expect(body.reviewer_note).toBe("wiki candidate edited; not applied to wiki_entries");

    // Verify mapped proposed_content payload details
    const proposed = JSON.parse(body.proposed_content);
    expect(proposed.entity_name).toBe("Tinh thể zombie");
    expect(proposed.entity_type).toBe("item"); // mapped back from "Vật phẩm"
    expect(proposed.summary).toBe("Tóm tắt mới từ admin.");
    expect(proposed.content).toBe("Chi tiết đầy đủ từ admin.");
    expect(proposed.aliases).toEqual(["Tinh thể"]);

    // Success message displayed
    await screen.findByText(/Đã lưu bản nháp của thực thể "Tinh thể zombie" thành công!/);
  });

  it("handles server errors gracefully and displays error message on Save Draft failure", async () => {
    const mockCandidates = [
      {
        correction_id: "corr-123",
        entity_name: "Tinh thể zombie",
        entity_type: "Vật phẩm",
        summary: "",
        content: "",
        aliases: [],
        evidence: [],
        source: "rag_corrections",
        status: "needs_human_fill",
        human_review_required: true,
        notes: "test notes"
      }
    ];

    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockCandidates,
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ error: "Database save error on server" }),
      });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminWikiCandidatesPage />);

    await screen.findByText("Tinh thể zombie");

    // Click Save Draft
    const saveBtn = screen.getByRole("button", { name: "LƯU BẢN NHÁP" });
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(2);
    });

    // Error message displayed
    await screen.findByText("Database save error on server");
  });

  it("checks navigation sidebar contains link to wiki-candidates page", async () => {
    render(<AdminNav />);

    const navLink = screen.getByRole("link", { name: "Ứng viên Wiki" });
    expect(navLink).toBeInTheDocument();
    expect(navLink.getAttribute("href")).toBe("/admin/wiki-candidates");
  });

  it("renders the canon review checkbox and disables it if summary or content is empty", async () => {
    const mockCandidates = [
      {
        correction_id: "corr-123",
        entity_name: "Tinh thể zombie",
        entity_type: "Vật phẩm",
        summary: "",
        content: "",
        aliases: [],
        evidence: [],
        source: "rag_corrections",
        status: "needs_human_fill",
        human_review_required: true,
        notes: "Ghi chú sạch"
      }
    ];

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCandidates,
    });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminWikiCandidatesPage />);

    await screen.findByText("Tinh thể zombie");

    const checkbox = screen.getByLabelText("Tôi xác nhận nội dung này là canon đã duyệt") as HTMLInputElement;
    expect(checkbox).toBeInTheDocument();
    expect(checkbox).toBeDisabled();
    expect(checkbox.checked).toBe(false);
  });

  it("disables the checkbox if content is unsafe", async () => {
    const mockCandidates = [
      {
        correction_id: "corr-123",
        entity_name: "Tinh thể zombie",
        entity_type: "Vật phẩm",
        summary: "SMOKE TEST",
        content: "Chi tiết",
        aliases: [],
        evidence: [],
        source: "rag_corrections",
        status: "ready_for_review",
        human_review_required: true,
        notes: "Ghi chú sạch"
      }
    ];

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCandidates,
    });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminWikiCandidatesPage />);

    await screen.findByText("Tinh thể zombie");

    const checkbox = screen.getByLabelText("Tôi xác nhận nội dung này là canon đã duyệt") as HTMLInputElement;
    expect(checkbox).toBeDisabled();
  });

  it("saves canon_reviewed=true in proposed_content when ticked and content is clean", async () => {
    const mockCandidates = [
      {
        correction_id: "corr-123",
        entity_name: "Tinh thể zombie",
        entity_type: "Vật phẩm",
        summary: "Tóm tắt sạch",
        content: "Nội dung sạch",
        aliases: [],
        evidence: [],
        source: "rag_corrections",
        status: "ready_for_review",
        human_review_required: true,
        notes: "Ghi chú sạch"
      }
    ];

    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockCandidates,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ok: true, correction_id: "corr-123", status: "approved" }),
      });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminWikiCandidatesPage />);

    await screen.findByText("Tinh thể zombie");

    const checkbox = screen.getByLabelText("Tôi xác nhận nội dung này là canon đã duyệt") as HTMLInputElement;
    expect(checkbox).not.toBeDisabled();
    fireEvent.click(checkbox);
    expect(checkbox.checked).toBe(true);

    const saveBtn = screen.getByRole("button", { name: "LƯU BẢN NHÁP" });
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(2);
    });

    const patchCall = fetchMock.mock.calls[1];
    const body = JSON.parse(patchCall?.[1]?.body as string);
    const proposed = JSON.parse(body.proposed_content);
    expect(proposed.canon_reviewed).toBe(true);
    expect(proposed.canon_reviewed_at).toBeDefined();
  });

  it("blocks saving and shows error message if ticked but content is unsafe", async () => {
    const mockCandidates = [
      {
        correction_id: "corr-123",
        entity_name: "Tinh thể zombie",
        entity_type: "Vật phẩm",
        summary: "Tóm tắt sạch",
        content: "Nội dung sạch",
        aliases: [],
        evidence: [],
        source: "rag_corrections",
        status: "ready_for_review",
        human_review_required: true,
        notes: "Ghi chú sạch"
      }
    ];

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCandidates,
    });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminWikiCandidatesPage />);

    await screen.findByText("Tinh thể zombie");

    const checkbox = screen.getByLabelText("Tôi xác nhận nội dung này là canon đã duyệt") as HTMLInputElement;
    fireEvent.click(checkbox);

    // Edit content to make it unsafe
    const contentInput = screen.getByPlaceholderText("Nhập chi tiết về thực thể, vai trò, thuộc tính...");
    fireEvent.change(contentInput, { target: { value: "Nội dung này có chữ MOCK" } });

    const saveBtn = screen.getByRole("button", { name: "LƯU BẢN NHÁP" });
    fireEvent.click(saveBtn);

    await screen.findByText("Nội dung còn chứa dấu hiệu test/placeholder, chưa thể xác nhận canon.");
  });

  it("renders a high-visibility warning when candidate has empty summary/content and human review is required, shows helper text near checkbox, and ensures no apply button or raw token input", async () => {
    const mockCandidates = [
      {
        correction_id: "corr-123",
        entity_name: "Tinh thể zombie",
        entity_type: "Vật phẩm",
        summary: "",
        content: "",
        aliases: [],
        evidence: [],
        source: "rag_corrections",
        status: "needs_human_fill",
        human_review_required: true,
        notes: "Ghi chú"
      }
    ];

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCandidates,
    });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminWikiCandidatesPage />);

    // 1. Wait for candidate to load
    await screen.findByText("Tinh thể zombie");

    // 2. High-visibility warning should be displayed
    const warningText = "Ứng viên này chưa có nội dung canon thật. Không thể xác nhận canon hoặc apply vào Wiki cho đến khi admin/tác giả điền summary và content đã được duyệt.";
    expect(screen.getByText(warningText)).toBeInTheDocument();

    // 3. Checkbox should be disabled
    const checkbox = screen.getByLabelText("Tôi xác nhận nội dung này là canon đã duyệt") as HTMLInputElement;
    expect(checkbox).toBeDisabled();

    // 4. Helper text should be displayed near the checkbox
    const helperText = "Chỉ tick khi nội dung đã được kiểm chứng từ canon truyện/tác giả. Không tick với placeholder, test, hoặc nội dung AI tự viết.";
    expect(screen.getByText(helperText)).toBeInTheDocument();

    // 5. No "Apply to wiki" button should exist
    expect(screen.queryByRole("button", { name: /apply.*wiki/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /áp dụng/i })).not.toBeInTheDocument();

    // 6. No raw token input should exist
    expect(screen.queryByPlaceholderText(/token/i)).not.toBeInTheDocument();
  });
});
