# Calendar Credential Confuser

Share google oauth credentials between a web page and a BE written in Python FastAPI, 
running on Kubernetes, and stored in azure-provisioned resources.

- [be/README-BE.md](./be/README-BE.md)
- [fe/README-FE.md](./fe/README-FE.md)
- [k8s/README-K8S.md](./k8s/README-K8S.md)

# TODO

- I am trying to get refresh tokens working. I went through a major contortion to get the FE nginx to proxy the BE. This is the best way to make cookies happy and all from the same site. The refresh token is stored in a http-only cookie. The next thing to do is work on the /api/v1/refresh endpoint. Http requests that discover an expired access token need to transparently (through a fetch wrapper) get a new one and retry. I think I have a GPT session about this...maybe [this one](https://chatgpt.com/c/681a2138-389c-800a-8940-b2cd58c573ca)?
- move endpoints into the file hierarchy recently prepared for them.
- use something like orval to automatically type-check open api from React-side. 
- revisit google perms - print users calendars!
- make some deployment pipelines using azure pipelines!
- try out python typing, like `ty`.
- write some tests