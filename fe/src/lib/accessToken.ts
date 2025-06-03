export type AccessToken = string;

import { createContext } from "react";

export type AccessTokenContextType = {
    token?: AccessToken;
    setToken?: React.Dispatch<React.SetStateAction<AccessToken>>;
  }
  
export const AccessTokenContext = createContext<AccessTokenContextType>({});
  