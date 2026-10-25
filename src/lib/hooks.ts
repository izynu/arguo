"use client";

import { useEffect, useState, useSyncExternalStore } from "react";
import { basePath } from "@/lib/site-config";

export type Route =
  | { view: "home" }
  | { view: "docs"; slug?: string }
  | { view: "resources" }
  | { view: "stats" }
  | { view: "methodology" }
  | { view: "evals" }
  | { view: "privacy" }
  | { view: "terms" }
  | { view: "not-found" };

export function parseHash(hash: string): Route {
  const clean = hash.replace(/^#\/?/, "").split("?")[0];
  if (!clean) return { view: "home" };
  const [head, rest] = clean.split("/");
  switch (head) {
    case "docs":
      return { view: "docs", slug: rest || undefined };
    case "resources":
      return { view: "resources" };
    case "stats":
      return { view: "stats" };
    case "methodology":
      return { view: "methodology" };
    case "evals":
      return { view: "evals" };
    case "privacy":
      return { view: "privacy" };
    case "terms":
      return { view: "terms" };
    default:
      return { view: "not-found" };
  }
}

export function useHashRoute(): Route {
  // Reading the hash through useSyncExternalStore keeps SSR consistent: the
  // server renders the home view, and React re-renders with the real hash
  // right after hydration instead of failing the hydration comparison.
  useSyncExternalStore(
    subscribeHashQuery,
    getHashQuerySnapshot,
    getHashQueryServerSnapshot
  );
  return parseHash(hashQueryStore.snapshot);
}

export function navigate(path: string) {
  window.location.hash = path;
}

/**
 * Hash-query store: the query string of the current hash route (e.g.
 * #/resources?q=x) as an external store. The address is the single source of
 * truth for view state, so every filter combination is a shareable URL.
 * Listening covers both hashchange events and replaceState writes made by
 * replaceHashQuery, which notifies subscribers explicitly.
 */
const hashQueryStore = {
  snapshot: "",
  listeners: new Set<() => void>(),
};

function notifyHashListeners() {
  hashQueryStore.listeners.forEach((cb) => cb());
}

if (typeof window !== "undefined") {
  hashQueryStore.snapshot = routeHashOf(window.location.hash) ?? "";
  window.addEventListener("hashchange", () => {
    const next = routeHashOf(window.location.hash);
    // In-page anchors (for example #main-content) address an element, not a
    // view; ignoring them keeps the current view mounted.
    if (next === null) return;
    hashQueryStore.snapshot = next;
    notifyHashListeners();
  });
}

/**
 * Returns the hash when it addresses a view route (empty, bare "#", or
 * "#/..."), or null when it is a plain in-page anchor like "#section-2".
 */
function routeHashOf(hash: string): string | null {
  if (hash === "" || hash === "#" || hash.startsWith("#/")) return hash;
  return null;
}

function subscribeHashQuery(cb: () => void): () => void {
  hashQueryStore.listeners.add(cb);
  return () => hashQueryStore.listeners.delete(cb);
}

function getHashQuerySnapshot(): string {
  return hashQueryStore.snapshot;
}

function getHashQueryServerSnapshot(): string {
  return "";
}

export function parseHashQuery(hash: string): URLSearchParams {
  const qIndex = hash.indexOf("?");
  return new URLSearchParams(qIndex >= 0 ? hash.slice(qIndex + 1) : "");
}

/** Reactive URLSearchParams of the current hash route. */
export function useHashQuery(): URLSearchParams {
  useSyncExternalStore(subscribeHashQuery, getHashQuerySnapshot, getHashQueryServerSnapshot);
  return parseHashQuery(hashQueryStore.snapshot);
}

/**
 * Replaces (not pushes) the query string of the current hash route and
 * notifies useHashQuery subscribers. No history entry is created and no
 * hashchange event fires, so per-keystroke filter edits never spam history.
 */
export function replaceHashQuery(params: URLSearchParams) {
  if (typeof window === "undefined") return;
  const raw = window.location.hash;
  const hash = routeHashOf(raw) ?? "#/";
  const qIndex = hash.indexOf("?");
  const base = qIndex >= 0 ? hash.slice(0, qIndex) : hash;
  const qs = params.toString();
  const next = qs ? `${base}?${qs}` : base;
  if (next !== window.location.hash) {
    window.history.replaceState(null, "", next);
    hashQueryStore.snapshot = next;
    notifyHashListeners();
  }
}

/* ---------------- Bookmarks (localStorage, no personal data leaves the browser) ---------------- */

const BOOKMARKS_KEY = "arguo:bookmarks";

type BookmarksStore = {
  ids: string[];
  has: (id: string) => boolean;
  toggle: (id: string) => void;
  subscribe: (cb: () => void) => () => void;
};

function readBookmarks(): string[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(BOOKMARKS_KEY);
    const parsed: unknown = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed.filter((x): x is string => typeof x === "string") : [];
  } catch {
    return [];
  }
}

function writeBookmarks(ids: string[]) {
  try {
    window.localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(ids));
  } catch {
    // Storage can be unavailable (private mode); bookmarks then last for the session only.
  }
}

export const bookmarks: BookmarksStore = {
  ids: [],
  has(id: string) {
    return this.ids.includes(id);
  },
  toggle(id: string) {
    this.ids = this.ids.includes(id) ? this.ids.filter((x) => x !== id) : [...this.ids, id];
    writeBookmarks(this.ids);
    this.snapshot = this.ids.join("\u0000");
    this.listeners.forEach((cb) => cb());
  },
  subscribe(cb: () => void) {
    this.listeners.add(cb);
    return () => this.listeners.delete(cb);
  },
  listeners: new Set<() => void>(),
  snapshot: "",
};

if (typeof window !== "undefined") {
  bookmarks.ids = readBookmarks();
  bookmarks.snapshot = bookmarks.ids.join("\u0000");
  window.addEventListener("storage", (e) => {
    if (e.key === BOOKMARKS_KEY) {
      bookmarks.ids = readBookmarks();
      bookmarks.snapshot = bookmarks.ids.join("\u0000");
      bookmarks.listeners.forEach((cb) => cb());
    }
  });
}

/** Snapshot function for useSyncExternalStore; stable across renders. */
function bookmarksSnapshot(): string {
  return bookmarks.snapshot;
}

export function useBookmarks(): { ids: string[]; has: (id: string) => boolean; toggle: (id: string) => void } {
  useSyncExternalStore(
    (cb) => bookmarks.subscribe(cb),
    bookmarksSnapshot,
    () => ""
  );
  return { ids: bookmarks.ids, has: bookmarks.has.bind(bookmarks), toggle: bookmarks.toggle.bind(bookmarks) };
}

/** Fetch JSON data relative to the configured base path. */
export function useJson<T>(path: string): { data: T | null; error: string | null; loading: boolean } {
  const [result, setResult] = useState<{ path: string; data: T | null; error: string | null } | null>(null);
  useEffect(() => {
    let cancelled = false;
    fetch(`${basePath}${path}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data: T) => {
        if (!cancelled) setResult({ path, data, error: null });
      })
      .catch((err: Error) => {
        if (!cancelled) setResult({ path, data: null, error: err.message });
      });
    return () => {
      cancelled = true;
    };
  }, [path]);
  const current = result && result.path === path ? result : null;
  return { data: current?.data ?? null, error: current?.error ?? null, loading: current === null };
}

export const groupLabels: Record<string, string> = {
  "getting-started": "Getting Started",
  "core-concepts": "Core Concepts",
  handbook: "Research Handbook",
  "resource-library": "Resource Library",
  "developer-guide": "Developer Guide",
  "skill-guide": "Skill Guide",
  "quality-safety": "Quality and Safety",
  project: "Project",
};

export const groupOrder = [
  "getting-started",
  "core-concepts",
  "handbook",
  "resource-library",
  "developer-guide",
  "skill-guide",
  "quality-safety",
  "project",
];