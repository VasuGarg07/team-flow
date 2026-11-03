type ErrorDetail = { field: string; message: string };

type ErrorBody = {
  error: { code: string; message: string; details?: ErrorDetail[] };
};

export class ApiError extends Error {
  status: number;
  code: string;
  details: ErrorDetail[];
  retryAfterSeconds: number | null;

  constructor(
    status: number,
    code: string,
    message: string,
    details: ErrorDetail[],
    retryAfterSeconds: number | null,
  ) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
    this.retryAfterSeconds = retryAfterSeconds;
  }
}

type RequestOptions = {
  method?: string;
  body?: unknown;
};

let accessToken: string | null = null;
let refreshInFlight: Promise<string | null> | null = null;
let onSessionExpired: (() => void) | null = null;

export function setSessionExpiredHandler(handler: (() => void) | null): void {
  onSessionExpired = handler;
}

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

function readRetryAfter(response: Response): number | null {
  const header = response.headers.get("Retry-After");
  if (header === null) {
    return null;
  }
  const seconds = Number(header);
  return Number.isFinite(seconds) ? seconds : null;
}

async function readError(response: Response): Promise<ApiError> {
  const retryAfter = readRetryAfter(response);
  try {
    const body = (await response.json()) as ErrorBody;
    return new ApiError(response.status, body.error.code, body.error.message, body.error.details ?? [], retryAfter);
  } catch {
    return new ApiError(response.status, "UNKNOWN", "Something went wrong", [], retryAfter);
  }
}

async function sendRequest(path: string, options: RequestOptions): Promise<Response> {
  const headers: Record<string, string> = {};
  const isFormData = options.body instanceof FormData;
  if (options.body !== undefined && !isFormData) {
    headers["Content-Type"] = "application/json";
  }
  if (accessToken !== null) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }
  let body: BodyInit | undefined;
  if (options.body instanceof FormData) {
    body = options.body;
  } else if (options.body !== undefined) {
    body = JSON.stringify(options.body);
  }
  return fetch(path, { method: options.method ?? "GET", headers, body });
}

export async function refreshAccessToken(): Promise<string | null> {
  if (refreshInFlight !== null) {
    return refreshInFlight;
  }
  refreshInFlight = (async () => {
    const response = await fetch("/auth/refresh", { method: "POST" });
    if (!response.ok) {
      accessToken = null;
      return null;
    }
    const body = (await response.json()) as { access_token: string };
    accessToken = body.access_token;
    return accessToken;
  })();
  try {
    return await refreshInFlight;
  } finally {
    refreshInFlight = null;
  }
}

async function fetchWithRefresh(path: string, options: RequestOptions): Promise<Response> {
  let response = await sendRequest(path, options);

  const sentToken = accessToken !== null;
  if (response.status === 401 && sentToken) {
    const newToken = await refreshAccessToken();
    if (newToken !== null) {
      response = await sendRequest(path, options);
    } else if (onSessionExpired !== null) {
      onSessionExpired();
    }
  }

  if (!response.ok) {
    throw await readError(response);
  }
  return response;
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetchWithRefresh(path, options);
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export async function apiBlob(path: string): Promise<Blob> {
  const response = await fetchWithRefresh(path, {});
  return response.blob();
}
