import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, deleteNarrativeUnit, updateNarrativeUnit, errorMessage } from "./api";

/** Builds a minimal fetch Response stub for the given status and body. */
function responseStub(
  status: number,
  body: unknown,
  { jsonThrows = false }: { jsonThrows?: boolean } = {}
): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: "",
    json: async () => {
      if (jsonThrows) throw new SyntaxError("Unexpected token");
      return body;
    },
  } as unknown as Response;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("request error mapping", () => {
  it("throws ApiError carrying status and the German backend message on 404", async () => {
    /** Expects a 404 with {error: "..."} to surface as ApiError with that German message verbatim. */
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(responseStub(404, { error: "Narrativ nicht gefunden" }))
    );

    await expect(deleteNarrativeUnit("missing-id")).rejects.toMatchObject({
      status: 404,
      message: "Narrativ nicht gefunden",
    });
    await expect(deleteNarrativeUnit("missing-id")).rejects.toBeInstanceOf(ApiError);
  });

  it("falls back to a generic German message when the body has no error property", async () => {
    /** Expects an error body without an `error` field to yield a generic German message, status preserved. */
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(responseStub(500, { detail: "boom" })));

    await expect(updateNarrativeUnit("id", { content: "x" })).rejects.toMatchObject({
      status: 500,
      message: "Ein unerwarteter Fehler ist aufgetreten.",
    });
  });

  it("falls back to a generic German message when the error field is not a string", async () => {
    /** Expects a body whose `error` is a non-string (e.g. a number) to fall back to the generic
     *  message — only a string error is safe to surface verbatim, status preserved. */
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(responseStub(400, { error: 42 })));

    await expect(deleteNarrativeUnit("id")).rejects.toMatchObject({
      status: 400,
      message: "Ein unerwarteter Fehler ist aufgetreten.",
    });
  });

  it("falls back to a generic German message when the error field is an object", async () => {
    /** Expects a structured (non-string) `error` payload to not be surfaced raw — generic fallback. */
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(responseStub(422, { error: { code: "X", msg: "boom" } }))
    );

    await expect(updateNarrativeUnit("id", { content: "x" })).rejects.toMatchObject({
      status: 422,
      message: "Ein unerwarteter Fehler ist aufgetreten.",
    });
  });

  it("does not crash when the error body is not JSON", async () => {
    /** Expects a non-JSON error body to be tolerated — generic message, status preserved, no throw from parsing. */
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(responseStub(503, null, { jsonThrows: true }))
    );

    await expect(deleteNarrativeUnit("id")).rejects.toMatchObject({
      status: 503,
      message: "Ein unerwarteter Fehler ist aufgetreten.",
    });
  });

  it("resolves normally on success without throwing", async () => {
    /** Expects requestVoid to resolve undefined and request to return the parsed JSON on a 2xx response. */
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(responseStub(204, undefined)));
    await expect(deleteNarrativeUnit("id")).resolves.toBeUndefined();

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(responseStub(200, { id: "id", title: "T", content: "C" }))
    );
    await expect(updateNarrativeUnit("id", { content: "C" })).resolves.toMatchObject({ id: "id" });
  });
});

describe("errorMessage", () => {
  it("returns the message of an ApiError unchanged", () => {
    /** Expects the German ApiError message to be returned verbatim for display. */
    expect(errorMessage(new ApiError(404, "Narrativ nicht gefunden"))).toBe("Narrativ nicht gefunden");
  });

  it("returns a generic German message for non-ApiError values", () => {
    /** Expects unknown thrown values to map to a safe generic German message instead of leaking raw text. */
    expect(errorMessage(new Error("404 Not Found"))).toBe("Ein unerwarteter Fehler ist aufgetreten.");
    expect(errorMessage("some string")).toBe("Ein unerwarteter Fehler ist aufgetreten.");
  });

  it("returns a generic German message for null and undefined", () => {
    /** Expects nullish caught values (a rejected promise with no reason, etc.) to map to the
     *  generic German message rather than throwing or returning "null"/"undefined". */
    expect(errorMessage(null)).toBe("Ein unerwarteter Fehler ist aufgetreten.");
    expect(errorMessage(undefined)).toBe("Ein unerwarteter Fehler ist aufgetreten.");
  });
});
