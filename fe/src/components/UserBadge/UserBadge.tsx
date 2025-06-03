import { useContext } from "react";
import { fetchWithAuth } from "../../lib/fetchWithAuth";
import { AccessTokenContext } from "../../lib/accessToken";
import { useQuery } from "@tanstack/react-query";

export const UserBadge: React.FC = () => {
    const accessTokenPlace = useContext(AccessTokenContext);
    const {isLoading, isError, data, error} = useQuery({
        queryKey: ['users-me'],
        queryFn: async () => {
            if (!accessTokenPlace.token) return undefined;
            const response = await fetchWithAuth(accessTokenPlace, '/api/v1/users/me');
            if (!response.ok) {
                throw new Error('Failed to fetch user data');
            }
            return response.json();
        },
    })
    if (isLoading)
        return (<div>Loading...</div>);
    if (isError)
        return (<div>Error loading user data: {String(error)} | {accessTokenPlace.token}</div>);
    return (<div>user: {JSON.stringify(data)}</div>);
  };