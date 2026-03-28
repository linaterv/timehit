const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data: unknown
  ) {
    super(`API Error ${status}: ${statusText}`);
    this.name = "ApiError";
  }
}

// In-memory token storage (not localStorage — safer)
let accessToken: string | null = null;
let refreshToken: string | null = null;

export function getAccessToken(): string | null {
  return accessToken;
}

export function setTokens(access: string, refresh?: string): void {
  accessToken = access;
  if (refresh) {
    refreshToken = refresh;
  }
}

export function clearTokens(): void {
  accessToken = null;
  refreshToken = null;
}

function redirectToLogin(): void {
  if (typeof window !== "undefined") {
    window.location.href = "/login";
  }
}

async function refreshAccessToken(): Promise<string | null> {
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      clearTokens();
      return null;
    }

    const data = await response.json();
    accessToken = data.access;
    return data.access;
  } catch {
    clearTokens();
    return null;
  }
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }

  let response = await fetch(url, { ...options, headers });

  // Token refresh on 401
  if (response.status === 401 && accessToken) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      headers["Authorization"] = `Bearer ${newToken}`;
      response = await fetch(url, { ...options, headers });
    } else {
      redirectToLogin();
      throw new ApiError(401, "Unauthorized", null);
    }
  }

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new ApiError(response.status, response.statusText, data);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}
