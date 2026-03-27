"use client";

import SystemHUD from "@/components/SystemHUD";

export default function TestHUDPage() {
  return (
    <div className="bg-ash-dark min-h-screen p-10" translate="no">
      <h1 className="text-white mb-10 text-2xl font-mono">TEST HUD LOCALIZATION</h1>
      <SystemHUD
        chapterNumber={817}
        totalChapters={1000}
        readingProgress={45.5}
        dangerLevel={1}
        dangerLabel="CAUTION"
        dangerColor="#f59e0b"
        characterStatus="MUTATED"
        keywords={["ALERT", "COMBAT", "MUTATION"]}
      />
      <div className="text-gray-500 mt-20 font-mono text-sm">
        Change URL to /vi/test-hud, /en/test-hud, etc. to test localization.
        (Auto-translate is disabled for this page)
      </div>
    </div>
  );
}
