import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import AdminFeedbackPolicyDashboard from "./page";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useRouter() {
    return {
      push: vi.fn(),
      refresh: vi.fn(),
    };
  },
  usePathname() {
    return "/admin/feedback-policy";
  }
}));

describe("AdminFeedbackPolicyDashboard Page", () => {
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

    render(<AdminFeedbackPolicyDashboard />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled();
    });

    // Displays authorization request
    await screen.findByText("YÊU CẦU XÁC THỰC ADMIN");
    expect(screen.getByText("Bạn cần đăng nhập bằng tài khoản Admin để truy cập trang này.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ĐẾN TRANG ĐĂNG NHẬP" })).toBeInTheDocument();
  });

  it("loads and renders dashboard stats, recent feedback, summaries, and patches when API call succeeds", async () => {
    const mockData = {
      feedback_recent: [
        {
          id: "feed-111",
          provisional_id: "prov-123",
          record_name: "Tinh thể zombie",
          feedback_type: "wrong_info",
          user_comment: "Tinh thể này xuất hiện ở chương 69 chứ không phải chương 49",
          suggested_correction: "Chỉnh sửa sang chương 69",
          page_url: "https://matthesinhhoa.vercel.app/vi/library",
          user_agent: "Mozilla/5.0",
          status: "pending",
          created_at: "2026-06-07T12:00:00Z"
        }
      ],
      summaries: [
        {
          provisional_id: "prov-456",
          record_name: "Phá Tâm Linh",
          total_feedback: 4,
          wrong_info_count: 3,
          wrong_type_count: 0,
          wrong_evidence_count: 1,
          duplicate_count: 0,
          spoiler_count: 0,
          missing_info_count: 0,
          other_count: 0,
          unique_user_agent_count: 3,
          dispute_score: 3.5,
          effective_status: "disputed",
          oracle_policy: "warn",
          top_comments: [
            { comment: "Sai chương xuất hiện", type: "wrong_info" }
          ],
          updated_at: "2026-06-07T12:30:00Z"
        }
      ],
      patches: [
        {
          id: "patch-999",
          target_type: "query",
          target_id: null,
          target_name: "Hàn Phong",
          query_pattern: "Hàn Phong là ai?",
          patch_type: "suppress_related_for_identity_query",
          effective_status: "active",
          oracle_policy: "allow",
          effective_summary: null,
          effective_content: null,
          effective_type: null,
          evidence: [],
          feedback_ids: ["feed-222"],
          confidence: 1.0,
          reason: "Ẩn các bản ghi gây nhiễu Hàn Phong đang, đệ Hàn Phong",
          created_by: "community_rag_policy_engine",
          created_at: "2026-06-07T13:00:00Z"
        }
      ],
      stats: {
        feedback_total: 45,
        summary_total: 8,
        patch_active: 5,
        warn_count: 3,
        block_count: 2
      }
    };

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockData
    });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminFeedbackPolicyDashboard />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled();
    });

    // 1. Title verification
    await screen.findByText("VÒNG TỰ HỌC CỘNG ĐỒNG (SELF-LEARNING)");
    expect(screen.getByText(/GIÁM SÁT VÒNG TỰ HỌC \(READ-ONLY\):/)).toBeInTheDocument();

    // 2. Stats cards check
    expect(screen.getByText("45")).toBeInTheDocument(); // total feedback
    expect(screen.getByText("8")).toBeInTheDocument();  // dispute summaries
    expect(screen.getByText("5")).toBeInTheDocument();  // active patches
    expect(screen.getByText("3")).toBeInTheDocument();  // warn count
    expect(screen.getByText("2")).toBeInTheDocument();  // block count

    // 3. TAB 1: Recent feedback list
    expect(screen.getByText("Tinh thể zombie")).toBeInTheDocument();
    expect(screen.getByText("Sai thông tin")).toBeInTheDocument();
    expect(screen.getByText(/"Tinh thể này xuất hiện ở chương 69 chứ không phải chương 49"/)).toBeInTheDocument();
    expect(screen.getByText(/"Chỉnh sửa sang chương 69"/)).toBeInTheDocument();

    // 4. Tab switching: summaries
    const summariesTab = screen.getByRole("button", { name: /Tranh chấp tổng hợp/ });
    fireEvent.click(summariesTab);
    expect(screen.getByText("Phá Tâm Linh")).toBeInTheDocument();
    expect(screen.getByText("Disputed (Tranh chấp)")).toBeInTheDocument();
    expect(screen.getByText("Warn (Cảnh báo)")).toBeInTheDocument();
    expect(screen.getByText(/Sai thông tin:/)).toBeInTheDocument();
    expect(screen.getByText(/Dispute Score:/)).toBeInTheDocument();

    // 5. Tab switching: patches
    const patchesTab = screen.getByRole("button", { name: /Bản vá kiến thức/ });
    fireEvent.click(patchesTab);
    expect(screen.getByText("Hàn Phong")).toBeInTheDocument();
    expect(screen.getByText("suppress_related_for_identity_query")).toBeInTheDocument();
    expect(screen.getByText("Lý do tạo:")).toBeInTheDocument();
    expect(screen.getByText(/Ẩn các bản ghi gây nhiễu Hàn Phong đang, đệ Hàn Phong/)).toBeInTheDocument();

    // 6. Safeguards: No "Apply to wiki" or token overrides
    expect(screen.queryByRole("button", { name: /apply.*wiki/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /áp dụng/i })).not.toBeInTheDocument();
    expect(screen.queryByPlaceholderText(/token/i)).not.toBeInTheDocument();
  });

  it("allows admin to disable and restore patches with a reviewer note", async () => {
    const mockData = {
      feedback_recent: [],
      summaries: [],
      patches: [
        {
          id: "patch-111",
          target_type: "query",
          target_id: null,
          target_name: "Hàn Phong",
          query_pattern: "Hàn Phong là ai?",
          patch_type: "suppress_related_for_identity_query",
          effective_status: "active",
          oracle_policy: "allow",
          effective_summary: null,
          effective_content: null,
          effective_type: null,
          evidence: [],
          feedback_ids: ["feed-222"],
          confidence: 1.0,
          reason: "Ẩn các bản ghi gây nhiễu Hàn Phong đang, đệ Hàn Phong",
          created_by: "community_rag_policy_engine",
          created_at: "2026-06-07T13:00:00Z"
        },
        {
          id: "patch-222",
          target_type: "query",
          target_id: null,
          target_name: "Zombie",
          query_pattern: "Zombie",
          patch_type: "suppress_related_for_identity_query",
          effective_status: "disabled",
          oracle_policy: "allow",
          effective_summary: null,
          effective_content: null,
          effective_type: null,
          evidence: [],
          feedback_ids: ["feed-333"],
          confidence: 1.0,
          reason: "Sai lệch tóm tắt",
          created_by: "community_rag_policy_engine",
          created_at: "2026-06-07T13:00:00Z"
        }
      ],
      stats: {
        feedback_total: 0,
        summary_total: 0,
        patch_active: 1,
        warn_count: 0,
        block_count: 0
      }
    };

    let fetchCount = 0;
    const fetchMock = vi.fn().mockImplementation(async (url, init) => {
      fetchCount++;
      // Initial load or refresh load
      if (url === "/api/oracle/feedback-policy-dashboard") {
        return {
          ok: true,
          json: async () => JSON.parse(JSON.stringify(mockData))
        };
      }
      // Mutation PATCH call
      if (url.startsWith("/api/oracle/feedback-policy-dashboard/patches/")) {
        const body = JSON.parse(init.body);
        expect(init.method).toBe("PATCH");
        expect(body.reviewer_note).toBe("Sai thông tin thực tế");
        if (body.action === "disable") {
          mockData.patches[0].effective_status = "disabled";
        } else if (body.action === "restore") {
          mockData.patches[1].effective_status = "active";
        }
        return {
          ok: true,
          json: async () => ({ ok: true, patch_id: "patch-xxx", status: "success", cache_cleared_count: 1 })
        };
      }
      return { ok: false, status: 500 };
    });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminFeedbackPolicyDashboard />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled();
    });

    // Switch to patches tab
    const patchesTab = screen.getByRole("button", { name: /Bản vá kiến thức/ });
    fireEvent.click(patchesTab);

    // Verify filter dropdown/buttons render
    expect(screen.getByText("Tất cả")).toBeInTheDocument();
    expect(screen.getByText("Hoạt động")).toBeInTheDocument();
    expect(screen.getByText("Đã tắt")).toBeInTheDocument();

    // Verify active patch render with "TẮT BẢN VÁ" button
    expect(screen.getByText("Hàn Phong")).toBeInTheDocument();
    const disableBtn = screen.getByRole("button", { name: "TẮT BẢN VÁ" });
    expect(disableBtn).toBeInTheDocument();

    // Verify disabled patch render with "KHÔI PHỤC BẢN VÁ" button
    expect(screen.getByText("Zombie")).toBeInTheDocument();
    const restoreBtn = screen.getByRole("button", { name: "KHÔI PHỤC BẢN VÁ" });
    expect(restoreBtn).toBeInTheDocument();

    // Click "TẮT BẢN VÁ" to reveal input and confirmation
    fireEvent.click(disableBtn);
    const inputField = screen.getByPlaceholderText("Nhập lý do ngắn (bắt buộc)...");
    expect(inputField).toBeInTheDocument();

    // Fill in reviewer note and confirm
    fireEvent.change(inputField, { target: { value: "Sai thông tin thực tế" } });
    const confirmBtn = screen.getByRole("button", { name: "XÁC NHẬN TẮT" });
    fireEvent.click(confirmBtn);

    // Verify patch update status call
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/oracle/feedback-policy-dashboard/patches/patch-111"),
        expect.objectContaining({
          method: "PATCH"
        })
      );
    });

    // Verify alert message
    await screen.findByText(/Đã tắt bản vá thành công/);
  });

  it("renders pipeline observability health panel, stale warning, and failure messages correctly", async () => {
    const mockHealthData = {
      feedback_recent: [],
      summaries: [],
      patches: [],
      stats: {
        feedback_total: 10,
        summary_total: 2,
        patch_active: 1,
        warn_count: 1,
        block_count: 0
      },
      health: {
        last_run_at: "2026-06-08T01:00:00Z",
        last_run_ok: false,
        last_run_errors: ["Database timeout error", "API connection refused"],
        hours_since_last_run: 4.5,
        pipeline_stale: true,
        recent_failures: 2,
        pending_feedbacks: 5,
        last_run_feedback_read: 15,
        last_run_summaries_written: 3,
        last_run_patches_written: 1,
        last_run_cache_deleted: 2,
        last_run_dry_run: false
      }
    };

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockHealthData
    });
    global.fetch = fetchMock as typeof fetch;

    render(<AdminFeedbackPolicyDashboard />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled();
    });

    // Verify Observability Header and state card renders
    await screen.findByText("Tình trạng pipeline tự học");
    expect(screen.getByText("FAIL")).toBeInTheDocument();

    // Verify Stale Warning renders with elapsed hours
    expect(screen.getByText(/CẢNH BÁO PIPELINE BỊ ĐÌNH TRỆ:/)).toBeInTheDocument();
    expect(screen.getByText(/4.5 giờ qua/)).toBeInTheDocument();

    // Verify Failure Warning renders and lists logs
    expect(screen.getByText(/LỖI PIPELINE GẦN NHẤT:/)).toBeInTheDocument();
    expect(screen.getByText("Database timeout error")).toBeInTheDocument();
    expect(screen.getByText("API connection refused")).toBeInTheDocument();

    // Verify detail stats grid elements
    expect(screen.getByText("15 rows")).toBeInTheDocument(); // feedback read
    expect(screen.getByText("3 rows")).toBeInTheDocument();  // summaries written
    expect(screen.getByText("+1 patches")).toBeInTheDocument(); // patches written
    expect(screen.getByText("Đã xóa 2")).toBeInTheDocument(); // cache cleared

    // Verify safeguards: no Apply to Wiki or token inputs
    expect(screen.queryByRole("button", { name: /apply.*wiki/i })).not.toBeInTheDocument();
    expect(screen.queryByPlaceholderText(/token/i)).not.toBeInTheDocument();
  });
});
