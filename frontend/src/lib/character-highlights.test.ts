import { describe, expect, it } from "vitest";

import { annotateCharacterNames } from "./character-highlights";

describe("annotateCharacterNames", () => {
  it("wraps known character names with data-character-name markers", () => {
    const html = "<p>Han Phong gap Tran Phong tai doanh trai.</p>";

    const result = annotateCharacterNames(html, ["Han Phong", "Tran Phong"]);
    const doc = new DOMParser().parseFromString(result, "text/html");
    const markers = Array.from(doc.querySelectorAll("[data-character-name]"));

    expect(markers).toHaveLength(2);
    expect(markers.map((marker) => marker.getAttribute("data-character-name"))).toEqual([
      "Han Phong",
      "Tran Phong",
    ]);
  });

  it("does not inject markers inside links or partial words", () => {
    const html = "<p><a href='/wiki/han-phong'>Han Phong</a> va Han PhongX dang di tuan.</p>";

    const result = annotateCharacterNames(html, ["Han Phong"]);
    const doc = new DOMParser().parseFromString(result, "text/html");

    expect(doc.querySelector("a [data-character-name]")).toBeNull();
    expect(doc.querySelectorAll("[data-character-name]")).toHaveLength(0);
  });

  it("prefers longest names first to avoid nested partial matches", () => {
    const html = "<p>Han Phong doi dau voi Han.</p>";

    const result = annotateCharacterNames(html, ["Han", "Han Phong"]);
    const doc = new DOMParser().parseFromString(result, "text/html");
    const markers = Array.from(doc.querySelectorAll("[data-character-name]"));

    expect(markers).toHaveLength(2);
    expect(markers[0]?.textContent).toBe("Han Phong");
    expect(markers[1]?.textContent).toBe("Han");
  });
});
