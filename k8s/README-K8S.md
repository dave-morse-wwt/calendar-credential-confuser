# Deploying a dev-like environment

```
cd k8s/ccc
```
Let's assume we're targeting the namespace `ccc-dev`. 

## Create the namespace
```
kubectl create namespace ccc-dev
```
## Create External Secrets

- `docker-registry` - Examine the shell script [make-docker-registry-secret](./ccc/make-docker-registry-secret), make any needed tweaks, and pipe it into `kubectl apply -f -`.
- `google-oauth-json` - Examine the shell script [make-google-oauth-json-secret](./ccc/make-google-oauth-json-secret), make any needed tweaks, and pipe it into `kubectl apply -f -`. 

## Deploy the helm chart

```
helm install ccc-dev . --namespace ccc-dev --values values.yaml
```
or if you've done this before:
```
helm upgrade ccc-dev . --namespace ccc-dev --values values.yaml
```

# Deploying Postgres SQL

Postgres is a peer dependency of the `ccc` helm chart. The thinking is that in non-dev envs we'll use a hosted db, so nothing done on that front yet.

But in dev, we'll use helm to build our own. 
See the [postgres/install](./postgres/install) script.
Worked for me with Rancher Desktop.