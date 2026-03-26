import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { LocaleProvider } from "@/context/LocaleContext";

import CharacterTooltip from "./CharacterTooltip";

function renderWithLocale(ui: React.ReactNode) {
  return render(<LocaleProvider locale="vi">{ui}</LocaleProvider>);
}

describe("CharacterTooltip", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("fetches and renders quick scan data on hover", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        name: "Han Phong",
        faction: "Tram Chi Huy",
        status: "Dang chien dau",
        ability: "Thong tri he thong",
        first_appearance: 5,
      }),
    });
    global.fetch = fetchMock as typeof fetch;

    renderWithLocale(
      <CharacterTooltip name="Han Phong" chapterProgress={10}>
        Han Phong
      </CharacterTooltip>,
    );

    fireEvent.mouseEnter(screen.getAllByText("Han Phong")[0]!);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });
    await screen.findByText("Tram Chi Huy");

    expect(fetchMock.mock.calls[0]?.[0]).toContain("/api/wiki/character?");
    expect(fetchMock.mock.calls[0]?.[0]).toContain("name=Han+Phong");
    expect(fetchMock.mock.calls[0]?.[0]).toContain("chapter=10");
    expect(fetchMock.mock.calls[0]?.[0]).toContain("locale=vi");
    expect(screen.getByText("Tram Chi Huy")).toBeInTheDocument();
    expect(screen.getByText("Thong tri he thong")).toBeInTheDocument();
  });

  it("hides tooltip content on mouse leave", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ name: "Han Phong" }),
    });
    global.fetch = fetchMock as typeof fetch;

    renderWithLocale(
      <CharacterTooltip name="Han Phong" chapterProgress={10}>
        Han Phong
      </CharacterTooltip>,
    );

    const trigger = screen.getAllByText("Han Phong")[0]!;
    fireEvent.mouseEnter(trigger);
    await screen.findByText("Han Phong", { selector: "div span" });

    fireEvent.mouseLeave(trigger);

    await waitFor(() => {
      expect(screen.queryByText("Tên: ", { selector: "div span" })).not.toBeInTheDocument();
    });
  });

  it("only fetches once across repeated hover events", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ name: "Han Phong" }),
    });
    global.fetch = fetchMock as typeof fetch;

    renderWithLocale(
      <CharacterTooltip name="Han Phong" chapterProgress={10}>
        Han Phong
      </CharacterTooltip>,
    );

    const trigger = screen.getAllByText("Han Phong")[0]!;
    fireEvent.mouseEnter(trigger);
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    fireEvent.mouseLeave(trigger);
    fireEvent.mouseEnter(trigger);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });
  });
});
