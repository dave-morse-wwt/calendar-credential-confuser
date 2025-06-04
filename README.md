# Calendar Credential Confuser

Practice OAuth2 flows using a React web page and a BE written in Python FastAPI, 
running on Kubernetes, and stored in azure-provisioned resources.

- [be/README-BE.md](./be/README-BE.md)
- [fe/README-FE.md](./fe/README-FE.md)
- [k8s/README-K8S.md](./k8s/README-K8S.md)

# WISHLIST

- move BE endpoints into the file hierarchy recently prepared for them.
- use something like orval to automatically type-check open api from React-side. 
- revisit google perms - print users calendars!
- make some deployment pipelines using azure pipelines!
- try out python typing, like `ty`.
- write some tests

# OAUTH2 & JWT Auth Flows

This project uses the common pattern of Oath2 login flows for a web api. 
When a user logs in, they get two tokens back.
- Short lived access token, returned via a json http response body
- Longer lived refresh token, returned via a http-only cookie. The cookie only gets sent back when accessing the /api/v1/refresh endpoint. 
When the user hits an endpoint requiring authorization (`/api/v1/users/me`), it has to send an access token in the http headers. Then:
- If the access token is valid: the request is serviced
- If the access token is invalid or expired: 
  - the request gets 401ed
  - the Front End handles this by requesting a new access token at the `/api/v1/refresh` endpoint
    - If that works, then the new access token is stored in react state, and a new refresh token is stored in the cookie (for marginal security gain), and the original http request is transparently retried
    - If it didn't work, we crash out, and the user has to realize they're logged out and log in again. A more serious app would would handle this on the React side, remember the users' page and state, etc. 

# Google Auth Flow

Originally I wanted to login and view users google calendars. To wit there's some functionality around users authorizing their google account details to be shared with this app. However, this is kinda old and there are no actual features associated with it. 