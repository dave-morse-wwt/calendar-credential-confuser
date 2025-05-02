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
Feed them into the helm values.yaml as inputs.

Scripts for creating the secrets from One Password are in [ccc/secrets/](./ccc/secrets/). Tweak them as needed and then pipe them into `kubectl apply -f -`

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

## Optional: access the DB like it's running on your dev machine's `localhost:5432`

This port forwards from `localhost:5432` into the cluster's postgres: 
```
kubectl apply -f ./dev-load-balancer.yaml
```
This also worked, but wasn't as permanent - it took up a terminal tab:
```
kubectl port-forward -n confusedb svc/confusedb-postgresql 5432:5432
```