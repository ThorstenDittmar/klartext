/** Counts the number of words in a text string. Splits on whitespace, filters empty tokens. */
export function countWords(text: string): number {
  return text.trim().split(/\s+/).filter((token) => token.length > 0).length;
}
