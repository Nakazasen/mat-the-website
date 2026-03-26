/**
 * Client-side chapter scanner for the reader HUD.
 */

export type DangerLevel = 0 | 1 | 2 | 3;
export type CharacterStatus = "NORMAL" | "INJURED" | "MUTATED" | "CRITICAL";

export interface ChapterMeta {
  dangerLevel: DangerLevel;
  characterStatus: CharacterStatus;
  dangerLabel: string;
  dangerColor: string;
  keywords: string[];
}

const EXTREME_KEYWORDS = [
  "hap hoi",
  "can ke cai chet",
  "sap chet",
  "khong con suc",
  "tuyet vong",
  "mat y thuc",
  "nga xuong",
  "thao hao",
];

const COMBAT_KEYWORDS = [
  "xac song",
  "thay ma",
  "zombie",
  "tieng sung",
  "chien dau",
  "tan cong",
  "mau",
  "ban",
  "dam",
  "bao luc",
  "giet",
  "giao tranh",
];

const TENSE_KEYWORDS = [
  "canh giac",
  "nguy hiem",
  "lo lang",
  "so hai",
  "khong an toan",
  "truy thoat",
];

const INJURED_KEYWORDS = [
  "bi thuong",
  "vet thuong",
  "chay mau",
  "gay xuong",
];

const MUTATED_KEYWORDS = [
  "dot bien",
  "tien hoa",
  "nang luc dac biet",
  "he thong",
  "mutation",
];

function normalizeContent(text: string): string {
  return text
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function countKeywords(text: string, keywords: string[]): number {
  const lower = normalizeContent(text);
  return keywords.reduce((acc, kw) => {
    const regex = new RegExp(kw, "g");
    return acc + (lower.match(regex)?.length ?? 0);
  }, 0);
}

export function useChapterMeta(content: string, _chapterNumber?: number): ChapterMeta {
  const extremeCount = countKeywords(content, EXTREME_KEYWORDS);
  const combatCount = countKeywords(content, COMBAT_KEYWORDS);
  const tenseCount = countKeywords(content, TENSE_KEYWORDS);
  const injuredCount = countKeywords(content, INJURED_KEYWORDS);
  const mutatedCount = countKeywords(content, MUTATED_KEYWORDS);

  let dangerLevel: DangerLevel = 0;
  if (extremeCount >= 2 || combatCount >= 8) {
    dangerLevel = 3;
  } else if (combatCount >= 3) {
    dangerLevel = 2;
  } else if (tenseCount >= 2 || combatCount >= 1) {
    dangerLevel = 1;
  }

  let characterStatus: CharacterStatus = "NORMAL";
  if (extremeCount >= 1) {
    characterStatus = "CRITICAL";
  } else if (mutatedCount >= 1) {
    characterStatus = "MUTATED";
  } else if (injuredCount >= 1) {
    characterStatus = "INJURED";
  }

  const dangerConfig = [
    { label: "SAFE", color: "#39FF14" },
    { label: "ALERT", color: "#f59e0b" },
    { label: "COMBAT", color: "#ef4444" },
    { label: "CRITICAL", color: "#dc2626" },
  ] as const;

  const keywords: string[] = [];
  if (tenseCount > 0) keywords.push("ALERT");
  if (combatCount > 0) keywords.push("COMBAT");
  if (injuredCount > 0) keywords.push("INJURED");
  if (mutatedCount > 0) keywords.push("MUTATION");
  if (extremeCount > 0) keywords.push("CRITICAL");

  return {
    dangerLevel,
    characterStatus,
    dangerLabel: dangerConfig[dangerLevel].label,
    dangerColor: dangerConfig[dangerLevel].color,
    keywords,
  };
}
