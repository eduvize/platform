const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;

abstract class BaseApi {
    protected get<T>(url: string): Promise<T> {
        return fetch(`${apiEndpoint}${url}`, {
            method: "GET",
            headers: this.get_headers(),
        }).then((response) => response.json());
    }

    protected post<T>(url: string, data: any): Promise<T> {
        return fetch(`${apiEndpoint}${url}`, {
            method: "POST",
            headers: this.get_headers(),
            body: JSON.stringify(data),
        }).then((response) => response.json());
    }

    protected postWithoutResponse(url: string, data: any): Promise<void> {
        return fetch(`${apiEndpoint}${url}`, {
            method: "POST",
            headers: this.get_headers(),
            body: JSON.stringify(data),
        }).then(() => {});
    }

    protected put<T>(url: string, data: any): Promise<T> {
        return fetch(`${apiEndpoint}${url}`, {
            method: "PUT",
            headers: this.get_headers(),
            body: JSON.stringify(data),
        }).then((response) => response.json());
    }

    protected putWithoutResponse(url: string, data: any): Promise<void> {
        return fetch(`${apiEndpoint}${url}`, {
            method: "PUT",
            headers: this.get_headers(),
            body: JSON.stringify(data),
        }).then(() => {});
    }

    protected delete<T>(url: string): Promise<T> {
        return fetch(`${apiEndpoint}${url}`, {
            method: "DELETE",
            headers: this.get_headers(),
        }).then((response) => response.json());
    }

    protected deleteWithoutResponse(url: string): Promise<void> {
        return fetch(`${apiEndpoint}${url}`, {
            method: "DELETE",
            headers: this.get_headers(),
        }).then(() => {});
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
