import { describe, expect, it } from "vitest";

import {
  getLocaleFromPath,
  normalizeLocale,
  replaceLocaleInPath,
  stripLocaleFromPath,
  withLocalePath,
} from "./config";

describe("i18n config helpers", () => {
  it("normalizes browser locales into supported locales", () => {
    expect(normalizeLocale("en-US")).toBe("en");
    expect(normalizeLocale("zh")).toBe("zh-CN");
    expect(normalizeLocale("ja-JP")).toBe("ja");
    expect(normalizeLocale(undefined)).toBe("vi");
  });

  it("extracts and strips locale prefixes", () => {
    expect(getLocaleFromPath("/en/chapters/1")).toBe("en");
    expect(stripLocaleFromPath("/en/chapters/1")).toBe("/chapters/1");
    expect(stripLocaleFromPath("/vi")).toBe("/");
  });

  it("rebuilds localized paths", () => {
    expect(withLocalePath("ja", "/chapters/1")).toBe("/ja/chapters/1");
    expect(replaceLocaleInPath("/vi/wiki/test", "zh-CN")).toBe("/zh-CN/wiki/test");
  });
});
