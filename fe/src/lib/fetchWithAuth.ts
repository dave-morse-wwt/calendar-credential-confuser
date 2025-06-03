import { AccessToken, AccessTokenContextType } from "./accessToken";

let inFlightRefreshPromise : Promise<AccessToken> | undefined = undefined; 

async function refreshAccessToken(): Promise<string> {
    let prom = inFlightRefreshPromise;
    if (prom) return prom;
    prom = inFlightRefreshPromise = fetch('/api/v1/refresh', { credentials: 'include' })
        .then(res => {
            if (!res.ok) throw new Error('Failed to refresh token');
            return res.json();
        })
        .then(data => {
            inFlightRefreshPromise = undefined;
            console.log('Access token received:', data.access_token);
            return data.access_token;
        })
        .catch(err => {
            inFlightRefreshPromise = undefined;
            // TODO: Force logout or notify user, etc.
            console.error('Refresh failed:', err);
            throw err;
        });
    return prom;
}

export async function fetchWithAuth({token, setToken}: AccessTokenContextType, input: RequestInfo, init: RequestInit = {}): Promise<Response> {
    const initWithAuth = (token: AccessToken | undefined) => {
        if (token === undefined)
            return init;
        const headers = new Headers(init.headers);
        headers.set("Authorization", `Bearer ${token}`);
        console.log('fetchWithAuth headers:', headers);
        return {...init, headers}
    }
    const response = await fetch(input, initWithAuth(token));
    if (response.status === 401) {
        const newAccessToken = await refreshAccessToken();
        if (setToken) setToken(newAccessToken); // TODO make this test useless - setToken always defined.
        // Retry original request with new token
        return await fetch(input, initWithAuth(newAccessToken));
    }
    else
        return response;
}

// TODO: NEXT: Use this in an authenticated endpoint. Probably write useQueryWithAuth and useMutationWithAuth hooks
