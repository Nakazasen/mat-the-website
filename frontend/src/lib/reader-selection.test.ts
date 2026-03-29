import { describe, expect, it } from "vitest";

import { findSelectionBlockText } from "./reader-selection";

describe("findSelectionBlockText", () => {
    it("returns the closest paragraph text for the active selection anchor", () => {
        document.body.innerHTML = `
            <div id="root">
                <p>Alpha line.</p>
                <p><span id="target">Beta fragment</span> inside the selected paragraph.</p>
            </div>
        `;

        const target = document.getElementById("target");
        const blockText = findSelectionBlockText(target, "Beta fragment");

        expect(blockText).toBe("Beta fragment inside the selected paragraph.");
    });

    it("falls back to the selected text when no block is available", () => {
        const blockText = findSelectionBlockText(null, "Loose selection");

        expect(blockText).toBe("Loose selection");
    });
});
