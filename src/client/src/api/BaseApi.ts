import { TokenResponse } from "@contracts";

const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;

abstract class BaseApi {
    private prefix: string;

    constructor(prefix: string) {
        this.prefix = prefix;
    }

    protected get<T>(url: string): Promise<T> {
        return this.wrapAuthorization(() =>
            fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
                method: "GET",
                headers: this.get_headers(),
            })
        ).then((r) => r.json());
    }

    protected post<T>(url: string, data: any): Promise<T> {
        return this.wrapAuthorization(() =>
            fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
                method: "POST",
                headers: this.get_headers(),
                body: JSON.stringify(data),
            })
        ).then((r) => r.json());
    }

    protected async postEventStream<T>(
        url: string,
        data: any,
        onData: (data: T) => void,
        onComplete?: () => void
    ) {
        const response = await fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
            method: "POST",
            headers: this.get_headers(),
            body: JSON.stringify(data),
        });

        const reader = response.body!.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                onComplete?.();
                break;
            }

            buffer += decoder.decode(value, { stream: true });

            let boundary = buffer.indexOf("\n");

            while (boundary !== -1) {
                const completeChunk = buffer.slice(0, boundary);
                buffer = buffer.slice(boundary + 1);

                if (completeChunk.trim()) {
                    try {
                        const json = JSON.parse(completeChunk);
                        onData(json);
                    } catch (e) {
                        onData(completeChunk as any);
                    }
                }

                boundary = buffer.indexOf("\n");
            }
        }
    }

    protected postForm<T>(url: string, data: FormData): Promise<T> {
        return this.wrapAuthorization(() =>
            fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`,
                },
                body: data,
            })
        ).then((r) => r.json());
    }

    protected postWithoutResponse(url: string, data: any): Promise<void> {
        return this.wrapAuthorization(() =>
            fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
                method: "POST",
                headers: this.get_headers(),
                body: JSON.stringify(data),
            })
        ).then(() => {});
    }

    protected put<T>(url: string, data: any): Promise<T> {
        return this.wrapAuthorization(() =>
            fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
                method: "PUT",
                headers: this.get_headers(),
                body: JSON.stringify(data),
            })
        ).then((r) => r.json());
    }

    protected putWithoutResponse(url: string, data: any): Promise<void> {
        return this.wrapAuthorization(() =>
            fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
                method: "PUT",
                headers: this.get_headers(),
                body: JSON.stringify(data),
            })
        ).then(() => {});
    }

    protected delete<T>(url: string): Promise<T> {
        return this.wrapAuthorization(() =>
            fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
                method: "DELETE",
                headers: this.get_headers(),
            })
        ).then((r) => r.json());
    }

    protected deleteWithPayload(url: string, data: any): Promise<void> {
        return this.wrapAuthorization(() =>
            fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
                method: "DELETE",
                headers: this.get_headers(),
                body: JSON.stringify(data),
            })
        ).then(() => {});
    }

    protected deleteWithoutResponse(url: string): Promise<void> {
        return this.wrapAuthorization(() =>
            fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
                method: "DELETE",
                headers: this.get_headers(),
            })
        ).then(() => {});
    }

    /**
     * Calls the request function and checks for a 401 response. If a 401 is received, access token is refreshed and the request is retried.
     * @param request
     */
    private wrapAuthorization(
        request: () => Promise<Response>
    ): Promise<Response> {
        return request().then((response) => {
            if (response.status === 401) {
                return this.refreshToken().then(() => request());
            }

            return response;
        });
    }

    private refreshToken(): Promise<void> {
        const refreshToken = localStorage.getItem("refreshToken");

        if (!refreshToken) {
            return Promise.reject("No refresh token");
        }

        return this.getRefreshedToken(refreshToken).then(
            ({ access_token, refresh_token }) => {
                localStorage.setItem("token", access_token);
                localStorage.setItem("refreshToken", refresh_token);
            }
        );
    }

    getRefreshedToken(refreshToken: string): Promise<TokenResponse> {
        return fetch(`${apiEndpoint}/auth/refresh`, {
            method: "POST",
            headers: this.get_headers(),
            body: JSON.stringify({
                refresh_token: refreshToken,
            }),
        })
            .then((r) => r.json())
            .catch(() => {
                if (localStorage.getItem("token")) {
                    localStorage.removeItem("token");
                    localStorage.removeItem("refreshToken");
                    window.location.reload();
                }
            });
    }

    private get_headers = () => {
        const token = localStorage.getItem("token");
        const headers: any = {
            "Content-Type": "application/json",
        };

        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        return headers;
    };
}

export default BaseApi;
