# Running
```
cd be
./dev-server
```
This will fetch my (Dave's) OnePassword credential and pass it to the web server via the environment.

# Adding packages with UV

Do something like:
```
$ cd be
$ uv add google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```

# Deployment

No pipeline exists. Instead proc this doc.

```
cd be
op read op://Private/dockerhub/read-write-dave-pat | docker login -u davemorse981 --password-stdin
docker build -t davemorse981/ccc-web-api:0.0.1 .
docker push davemorse981/ccc-web-api:0.0.1
```