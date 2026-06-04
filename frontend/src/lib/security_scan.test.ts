import { describe, expect, it } from "vitest";
import * as fs from "fs";
import * as path from "path";

// Helpers to get all files recursively
function getFiles(dir: string): string[] {
    const subdirs = fs.readdirSync(dir);
    const files = subdirs.map((subdir) => {
        const res = path.resolve(dir, subdir);
        return fs.statSync(res).isDirectory() ? getFiles(res) : [res];
    });
    return files.reduce((a, f) => a.concat(f), []);
}

describe("Security Scanner", () => {
    it("ensures no secrets are hardcoded or leaked in frontend source and static build bundles", () => {
        // Define secret prefixes/keys dynamically to avoid self-matching
        const forbiddenPatterns = [
            "GEMINI_" + "API_KEY",
            "SUPABASE_" + "SERVICE_ROLE",
            "R2_" + "SECRET_ACCESS_KEY",
            "AI" + "zaSy",
            "s" + "k-"
        ];

        const srcDir = path.resolve(__dirname, "../../src");
        const nextStaticDir = path.resolve(__dirname, "../../../.next/static");

        const filesToScan: string[] = [];

        // Scan frontend/src files
        if (fs.existsSync(srcDir)) {
            const allSrcFiles = getFiles(srcDir);
            for (const file of allSrcFiles) {
                // Ignore this scanner test file and its build artifacts to avoid self-triggering
                if (file.endsWith("security_scan.test.ts") || file.endsWith("security_scan.test.tsx")) {
                    continue;
                }
                filesToScan.push(file);
            }
        }

        // Scan compiled static Next.js bundle if it exists
        if (fs.existsSync(nextStaticDir)) {
            const allStaticFiles = getFiles(nextStaticDir);
            for (const file of allStaticFiles) {
                if (file.endsWith(".js") || file.endsWith(".json")) {
                    filesToScan.push(file);
                }
            }
        }

        const violations: { file: string; pattern: string; line: number }[] = [];

        for (const file of filesToScan) {
            const isApiRoute = file.includes(path.join("app", "api"));
            const content = fs.readFileSync(file, "utf8");
            
            // Check each forbidden pattern
            for (const pattern of forbiddenPatterns) {
                // Special case: API routes are allowed to contain reference to the env var name itself (e.g. process.env.GEMINI_API_KEY)
                // but are NOT allowed to contain actual hardcoded keys (like AIza... or sk-...)
                if (isApiRoute && (pattern.includes("API_KEY") || pattern.includes("ROLE") || pattern.includes("SECRET"))) {
                    continue;
                }

                // Check for hardcoded API keys or env vars
                if (content.includes(pattern)) {
                    // Let's find the line number
                    const lines = content.split("\n");
                    for (let idx = 0; idx < lines.length; idx++) {
                        if (lines[idx].includes(pattern)) {
                            violations.push({
                                file: path.basename(file),
                                pattern,
                                line: idx + 1
                            });
                        }
                    }
                }
            }

            // Check using regex for typical key shapes
            const geminiRegex = /AIzaSy[A-Za-z0-9_-]{35}/g;
            const openAiRegex = /sk-[A-Za-z0-9]{32,}/g;

            const geminiMatches = content.match(geminiRegex);
            if (geminiMatches) {
                violations.push({
                    file: path.basename(file),
                    pattern: `RegEx: ${geminiMatches[0].substring(0, 10)}...`,
                    line: 1
                });
            }

            const openAiMatches = content.match(openAiRegex);
            if (openAiMatches) {
                violations.push({
                    file: path.basename(file),
                    pattern: `RegEx: ${openAiMatches[0].substring(0, 10)}...`,
                    line: 1
                });
            }
        }

        expect(violations, `Found secret key references in frontend source/bundle:\n${JSON.stringify(violations, null, 2)}`).toEqual([]);
    });
});
