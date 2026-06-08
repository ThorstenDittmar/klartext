import { describe, it, expect } from "vitest";
import { countWords } from "./wordCount";

describe("countWords", () => {
  it("returns 0 for empty string", () => {
    /** Expects: empty input yields zero words. */
    expect(countWords("")).toBe(0);
  });

  it("returns 0 for whitespace-only string", () => {
    /** Expects: a string of only spaces/newlines is not counted as words. */
    expect(countWords("   \n\t  ")).toBe(0);
  });

  it("counts single word", () => {
    /** Expects: a single word returns 1. */
    expect(countWords("Hallo")).toBe(1);
  });

  it("counts multiple words separated by spaces", () => {
    /** Expects: words split by single spaces are each counted. */
    expect(countWords("Hallo Welt")).toBe(2);
  });

  it("counts words separated by multiple spaces", () => {
    /** Expects: multiple consecutive spaces between words don't create phantom words. */
    expect(countWords("Hallo   Welt")).toBe(2);
  });

  it("counts words separated by newlines", () => {
    /** Expects: newlines between words are treated as whitespace separators. */
    expect(countWords("Hallo\nWelt")).toBe(2);
  });

  it("counts hyphenated words as one word", () => {
    /** Expects: a hyphenated compound is one token. */
    expect(countWords("Wirkgefüge-Editor")).toBe(1);
  });

  it("counts a longer prose passage", () => {
    /** Expects: a realistic prose fragment is counted correctly. */
    const text = "Im Jahr 2026 begann eine neue Ära der epistemischen Transparenz in Deutschland.";
    expect(countWords(text)).toBe(12);
  });
});
