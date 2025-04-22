# Running
```
cd be
./RUN_SERVER
```
This will fetch my (Dave's) OnePassword credential and pass it to the web server via the environment.

# Adding packages with UV

Do something like:
```
$ cd be
$ uv add google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```