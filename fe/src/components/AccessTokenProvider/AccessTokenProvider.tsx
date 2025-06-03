import { useState } from "react";
import { AccessToken, AccessTokenContext } from "../../lib/accessToken";

export const AccessTokenProvider: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
    const [token, setToken] = useState<AccessToken>("");
    return <AccessTokenContext.Provider value={{ token, setToken }}>{children}</AccessTokenContext.Provider>;
}