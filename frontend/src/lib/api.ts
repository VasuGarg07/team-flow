type ErrorDetail = { field: string; message: string };

type ErrorBody = {
  error: { code: string; message: string; details?: ErrorDetail[] };
};

export class ApiError extends Error {
  status: number;
  code: string;
  details: ErrorDetail[];

  constructor(status: number, code: string, message: string, details: ErrorDetail[]) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

type RequestOptions = {
  method?: string;
  body?: unknown;
};

let accessToken: string | null = null;
let refreshInFlight: Promise<string | null> | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

async function readError(response: Response): Promise<ApiError> {
  try {
    const body = (await response.json()) as ErrorBody;
    return new ApiError(response.status, body.error.code, body.error.message, body.error.details ?? []);
  } catch {
    return new ApiError(response.status, "UNKNOWN", "Something went wrong", []);
  }
}

async function sendRequest(path: string, options: RequestOptions): Promise<Response> {
  const headers: Record<string, string> = {};
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (accessToken !== null) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }
  return fetch(path, {
    method: options.method ?? "GET",
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });
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

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  let response = await sendRequest(path, options);

  const sentToken = accessToken !== null;
  if (response.status === 401 && sentToken) {
    const newToken = await refreshAccessToken();
    if (newToken !== null) {
      response = await sendRequest(path, options);
    }
  }

  if (!response.ok) {
    throw await readError(response);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}
