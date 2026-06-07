import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import AdminLoginPage from "./page";

// Mock next/navigation
const mockPush = vi.fn();
const mockRefresh = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter() {
    return {
      push: mockPush,
      refresh: mockRefresh,
    };
  },
}));

// Mock Supabase
const mockSignInWithPassword = vi.fn();
const mockResetPasswordForEmail = vi.fn();
const mockUpdateUser = vi.fn();
const mockSignOut = vi.fn();
const mockOnAuthStateChange = vi.fn().mockReturnValue({
  data: {
    subscription: {
      unsubscribe: vi.fn(),
    },
  },
});

vi.mock("@/lib/supabase-admin", () => ({
  createAdminClient() {
    return {
      auth: {
        signInWithPassword: mockSignInWithPassword,
        resetPasswordForEmail: mockResetPasswordForEmail,
        updateUser: mockUpdateUser,
        signOut: mockSignOut,
        onAuthStateChange: mockOnAuthStateChange,
      },
    };
  },
}));

describe("AdminLoginPage Login & Recovery Flow", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    if (typeof window !== "undefined") {
      window.location.hash = "";
    }
  });

  it("renders login form by default", () => {
    render(<AdminLoginPage />);
    expect(screen.getByRole("heading", { name: "ADMIN ACCESS" })).toBeInTheDocument();
    expect(screen.getByPlaceholderText("admin@example.com")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("••••••••")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ĐĂNG NHẬP" })).toBeInTheDocument();
  });

  it("switches to forgot password mode and triggers password reset email", async () => {
    mockResetPasswordForEmail.mockResolvedValue({ error: null });

    render(<AdminLoginPage />);
    
    // Switch mode
    const forgotBtn = screen.getByText("Quên mật khẩu?");
    fireEvent.click(forgotBtn);

    expect(screen.getByRole("heading", { name: "KHÔI PHỤC MẬT KHẨU" })).toBeInTheDocument();
    
    const emailInput = screen.getByPlaceholderText("admin@example.com");
    fireEvent.change(emailInput, { target: { value: "admin@test.com" } });
    
    const submitBtn = screen.getByRole("button", { name: "GỬI EMAIL KHÔI PHỤC" });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(mockResetPasswordForEmail).toHaveBeenCalledWith("admin@test.com", {
        redirectTo: expect.stringContaining("/admin/login"),
      });
    });

    await screen.findByText("Đã gửi email khôi phục mật khẩu! Kiểm tra hộp thư (và cả Spam) nhé.");
  });

  it("displays password update form when hash contains recovery type", () => {
    if (typeof window !== "undefined") {
      window.location.hash = "#access_token=test&type=recovery";
    }

    render(<AdminLoginPage />);

    expect(screen.getByRole("heading", { name: "CẬP NHẬT MẬT KHẨU" })).toBeInTheDocument();
    const inputs = screen.getAllByPlaceholderText("••••••••");
    expect(inputs).toHaveLength(2); // new password and confirm password inputs
  });

  it("displays password mismatch error on recovery update attempt", async () => {
    if (typeof window !== "undefined") {
      window.location.hash = "#access_token=test&type=recovery";
    }

    render(<AdminLoginPage />);

    const inputs = screen.getAllByPlaceholderText("••••••••");
    const newPassInput = inputs[0];
    const confirmPassInput = inputs[1];

    expect(newPassInput).toBeInTheDocument();
    expect(confirmPassInput).toBeInTheDocument();

    fireEvent.change(newPassInput!, { target: { value: "password123" } });
    fireEvent.change(confirmPassInput!, { target: { value: "password456" } });

    const updateBtn = screen.getByRole("button", { name: "CẬP NHẬT MẬT KHẨU" });
    fireEvent.click(updateBtn);

    await screen.findByText("Mật khẩu nhập lại không khớp.");
  });

  it("requires minimum 8 characters for recovery password", async () => {
    if (typeof window !== "undefined") {
      window.location.hash = "#access_token=test&type=recovery";
    }

    render(<AdminLoginPage />);

    const inputs = screen.getAllByPlaceholderText("••••••••");
    fireEvent.change(inputs[0]!, { target: { value: "short" } });
    fireEvent.change(inputs[1]!, { target: { value: "short" } });

    const updateBtn = screen.getByRole("button", { name: "CẬP NHẬT MẬT KHẨU" });
    fireEvent.click(updateBtn);

    await screen.findByText("Mật khẩu phải chứa ít nhất 8 ký tự.");
  });

  it("submits password update successfully and signs out", async () => {
    if (typeof window !== "undefined") {
      window.location.hash = "#access_token=test&type=recovery";
    }
    mockUpdateUser.mockResolvedValue({ error: null });
    mockSignOut.mockResolvedValue({});

    render(<AdminLoginPage />);

    const inputs = screen.getAllByPlaceholderText("••••••••");
    fireEvent.change(inputs[0]!, { target: { value: "validpassword123" } });
    fireEvent.change(inputs[1]!, { target: { value: "validpassword123" } });

    const updateBtn = screen.getByRole("button", { name: "CẬP NHẬT MẬT KHẨU" });
    fireEvent.click(updateBtn);

    await waitFor(() => {
      expect(mockUpdateUser).toHaveBeenCalledWith({ password: "validpassword123" });
      expect(mockSignOut).toHaveBeenCalled();
    });

    await screen.findByText("Đã cập nhật mật khẩu thành công. Vui lòng đăng nhập lại.");
    expect(screen.getByRole("heading", { name: "ADMIN ACCESS" })).toBeInTheDocument();
  });
});
