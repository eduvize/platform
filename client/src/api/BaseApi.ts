const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;

abstract class BaseApi {
    private prefix: string;

    constructor(prefix: string) {
        this.prefix = prefix;
    }

    protected get<T>(url: string): Promise<T> {
        return fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
            method: "GET",
            headers: this.get_headers(),
        })
            .then(this.checkUnauthorized)
            .then((response) => response.json());
    }

    protected post<T>(url: string, data: any): Promise<T> {
        return fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
            method: "POST",
            headers: this.get_headers(),
            body: JSON.stringify(data),
        })
            .then(this.checkUnauthorized)
            .then((response) => response.json());
    }

    protected postForm<T>(url: string, data: FormData): Promise<T> {
        return fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
            body: data,
        })
            .then(this.checkUnauthorized)
            .then((response) => response.json());
    }

    protected postWithoutResponse(url: string, data: any): Promise<void> {
        return fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
            method: "POST",
            headers: this.get_headers(),
            body: JSON.stringify(data),
        })
            .then(this.checkUnauthorized)
            .then(() => {});
    }

    protected put<T>(url: string, data: any): Promise<T> {
        return fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
            method: "PUT",
            headers: this.get_headers(),
            body: JSON.stringify(data),
        })
            .then(this.checkUnauthorized)
            .then((response) => response.json());
    }

    protected putWithoutResponse(url: string, data: any): Promise<void> {
        return fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
            method: "PUT",
            headers: this.get_headers(),
            body: JSON.stringify(data),
        })
            .then(this.checkUnauthorized)
            .then(() => {});
    }

    protected delete<T>(url: string): Promise<T> {
        return fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
            method: "DELETE",
            headers: this.get_headers(),
        })
            .then(this.checkUnauthorized)
            .then((response) => response.json());
    }

    protected deleteWithoutResponse(url: string): Promise<void> {
        return fetch(`${apiEndpoint}/${this.prefix}/${url}`, {
            method: "DELETE",
            headers: this.get_headers(),
        })
            .then(this.checkUnauthorized)
            .then(() => {});
    }

    private checkUnauthorized = (response: Response) => {
        if (response.status === 401) {
            localStorage.removeItem("token");
            window.location.reload();
        }

        return response;
    };

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
