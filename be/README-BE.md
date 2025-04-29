# Running
```
cd be
./dev-server
```
This will fetch my (Dave's) OnePassword credential and pass it to the web server via the environment.

# Venv vagaries

This project uses `uv` by Astral. I'm fuzzy on exactly how it's working. At one point I discovered it was using the wrong venv, and I had to do this:
```
cd be
uv export > /tmp/requirements.txt
uv venv .venv
source .venv/bin/activate
uv pip install --requirements /tmp/requirements.txt
```
Several restarts of ms vs code later, I finally got rid of yonder yellow squiglies on all my imports. 

# Adding packages with UV

Do something like:
```
$ cd be
$ uv add google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```
Never use `uv pip install`, it doesn't update `uv.lock`, it won't persist. 

# Deployment

No pipeline exists. Instead proc this doc.

```
cd be
op read op://Private/dockerhub/read-write-dave-pat | docker login -u davemorse981 --password-stdin
docker build -t davemorse981/ccc-web-api:0.0.1 .
docker push davemorse981/ccc-web-api:0.0.1
```