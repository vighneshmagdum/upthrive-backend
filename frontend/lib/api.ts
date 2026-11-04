export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

type ApiOptions = {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
};

const API_PREFIX = "/api/v1";
const UNSAFE_METHODS = new Set(["POST", "PATCH", "DELETE"]);
const AUTH_ROUTES = new Set(["/auth/login", "/auth/register", "/auth/refresh"]);

function readCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const prefix = name + "=";
  const part = document.cookie.split("; ").find((entry) => entry.startsWith(prefix));
  return part ? decodeURIComponent(part.slice(prefix.length)) : null;
}

async function getCsrfToken(): Promise<string> {
  const existing = readCookie("upthrive_csrf");
  if (existing) return existing;

  const response = await fetch(API_PREFIX + "/auth/csrf", {
    method: "GET",
    credentials: "same-origin",
    cache: "no-store"
  });
  if (!response.ok) throw new ApiError("Could not start a secure session.", response.status);
  const payload = (await response.json()) as { csrf_token: string };
  return payload.csrf_token;
}

async function send<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const method = options.method || "GET";
  const headers: Record<string, string> = { Accept: "application/json" };

  if (options.body !== undefined) headers["Content-Type"] = "application/json";
  if (UNSAFE_METHODS.has(method)) headers["X-CSRF-Token"] = await getCsrfToken();

  const response = await fetch(API_PREFIX + path, {
    method,
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
    credentials: "same-origin",
    cache: "no-store"
  });

  if (response.status === 204) return undefined as T;
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof payload.detail === "string" ? payload.detail : "Request failed.";
    throw new ApiError(detail, response.status);
  }
  return payload as T;
}

export async function apiRequest<T>(path: string, options: ApiOptions = {}): Promise<T> {
  try {
    return await send<T>(path, options);
  } catch (error) {
    const authRoute = AUTH_ROUTES.has(path);
    if (!(error instanceof ApiError) || error.status !== 401 || authRoute) throw error;

    try {
      await send("/auth/refresh", { method: "POST" });
    } catch {
      throw error;
    }
    return send<T>(path, options);
  }
}
