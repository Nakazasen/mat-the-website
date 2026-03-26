import { describe, expect, it } from "vitest";

import { useChapterMeta } from "./useChapterMeta";

describe("useChapterMeta", () => {
  it("detects safe chapters with no major signals", () => {
    const meta = useChapterMeta("Doan nguoi im lang tien vao khu an toan.");

    expect(meta.dangerLevel).toBe(0);
    expect(meta.characterStatus).toBe("NORMAL");
    expect(meta.keywords).toEqual([]);
  });

  it("detects combat and critical status from heavy combat text", () => {
    const content = [
      "Tieng sung vang len giua giao tranh.",
      "Zombie tan cong, mau chay va ai cung lo lang.",
      "Nhan vat chinh hap hoi, sap chet giua chien dau.",
    ].join(" ");

    const meta = useChapterMeta(content);

    expect(meta.dangerLevel).toBe(3);
    expect(meta.characterStatus).toBe("CRITICAL");
    expect(meta.keywords).toEqual(
      expect.arrayContaining(["ALERT", "COMBAT", "CRITICAL"])
    );
  });

  it("detects mutation without escalating to critical by itself", () => {
    const meta = useChapterMeta("He thong kich hoat nang luc dac biet va dot bien bat dau.");

    expect(meta.characterStatus).toBe("MUTATED");
    expect(meta.keywords).toEqual(expect.arrayContaining(["MUTATION"]));
  });
});
