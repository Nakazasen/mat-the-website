/**
 * useChapterMeta
 * Scans chapter content for keywords to derive:
 * - dangerLevel (0 = safe, 1 = tense, 2 = combat, 3 = extreme)
 * - characterStatus (for main character display on HUD)
 * No API calls — pure client-side logic.
 */

export type DangerLevel = 0 | 1 | 2 | 3;
export type CharacterStatus = "BÌNH THƯỜNG" | "BỊ THƯƠNG" | "DỊ BIẾN" | "NGUY KỊCH";

export interface ChapterMeta {
  dangerLevel: DangerLevel;
  characterStatus: CharacterStatus;
  dangerLabel: string;
  dangerColor: string;
}

// Keyword lists — matching story context
const EXTREME_KEYWORDS = [
  "hấp hối", "cận kề cái chết", "sắp chết", "không còn sức",
  "tuyệt vọng", "mất đi ý thức", "ngã xuống", "thở hào hển",
];

const COMBAT_KEYWORDS = [
  "xác sống", "thây ma", "zombie", "tiếng súng", "chiến đấu",
  "tấn công", "máu", "bắn", "chém", "đâm", "bạo lực",
  "giết", "xông vào", "vây hãm", "giao tranh",
];

const TENSE_KEYWORDS = [
  "cảnh giác", "nguy hiểm", "rình rập", "lo lắng", "sợ hãi",
  "tiếng động", "bóng tối", "im lặng đáng sợ", "mùi máu",
  "không an toàn", "trốn thoát",
];

const INJURED_KEYWORDS = [
  "bị thương", "vết thương", "đau đớn", "chảy máu", "băng bó",
  "gãy xương", "sưng tấy",
];

const MUTATED_KEYWORDS = [
  "dị biến", "biến đổi gen", "tiến hóa", "năng lực đặc biệt",
  "hệ thống", "cấp độ tăng", "kỹ năng mới", "mutation",
];

function countKeywords(text: string, keywords: string[]): number {
  const lower = text.toLowerCase();
  return keywords.reduce((acc, kw) => {
    const regex = new RegExp(kw, "g");
    return acc + (lower.match(regex)?.length ?? 0);
  }, 0);
}

export function useChapterMeta(content: string): ChapterMeta {
  const extremeCount = countKeywords(content, EXTREME_KEYWORDS);
  const combatCount = countKeywords(content, COMBAT_KEYWORDS);
  const tenseCount = countKeywords(content, TENSE_KEYWORDS);
  const injuredCount = countKeywords(content, INJURED_KEYWORDS);
  const mutatedCount = countKeywords(content, MUTATED_KEYWORDS);

  // Derive danger level
  let dangerLevel: DangerLevel = 0;
  if (extremeCount >= 2 || combatCount >= 8) {
    dangerLevel = 3;
  } else if (combatCount >= 3) {
    dangerLevel = 2;
  } else if (tenseCount >= 2 || combatCount >= 1) {
    dangerLevel = 1;
  }

  // Derive character status
  let characterStatus: CharacterStatus = "BÌNH THƯỜNG";
  if (extremeCount >= 1) {
    characterStatus = "NGUY KỊCH";
  } else if (mutatedCount >= 1) {
    characterStatus = "DỊ BIẾN";
  } else if (injuredCount >= 1) {
    characterStatus = "BỊ THƯƠNG";
  }

  const DANGER_CONFIG = [
    { label: "AN TOÀN", color: "#39FF14" },
    { label: "CẢNH BÁO", color: "#f59e0b" },
    { label: "CHIẾN ĐẤU", color: "#ef4444" },
    { label: "CỰC KỲ NGUY HIỂM", color: "#dc2626" },
  ] as const;

  return {
    dangerLevel,
    characterStatus,
    dangerLabel: DANGER_CONFIG[dangerLevel].label,
    dangerColor: DANGER_CONFIG[dangerLevel].color,
  };
}
