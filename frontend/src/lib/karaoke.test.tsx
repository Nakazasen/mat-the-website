import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { LocaleProvider } from "@/context/LocaleContext";

import { renderRichKaraoke } from "./karaoke";

describe("renderRichKaraoke", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("turns annotated character spans into interactive quick scan tooltips", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        name: "Han Phong",
        faction: "Tram Chi Huy",
      }),
    });
    global.fetch = fetchMock as typeof fetch;

    const html = "<p><span data-character-name=\"Han Phong\" class=\"char-highlight\">Han Phong</span> tien vao can cu.</p>";
    const { nodes } = renderRichKaraoke(html, null, "dark", 12);

    render(<LocaleProvider locale="vi"><div>{nodes}</div></LocaleProvider>);

    fireEvent.mouseEnter(screen.getByText("Han Phong"));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });
    expect(await screen.findByText("Tram Chi Huy")).toBeInTheDocument();
  });
});
