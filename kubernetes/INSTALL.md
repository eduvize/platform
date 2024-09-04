## Installing Eduvize on Kubernetes

### Prerequisites

- Ensure you have a namespace created within your cluster.
- Install the `bitnami/kafka` chart to this namespace.
- If you haven't already, install `cert-manager` to your cluster.

**Step 1. Stand up a Kubernetes Cluster**

If you've already got a cluster running, great! You can skip this step.

If you're new to Kubernetes, we recommend [MicroK8s](https://microk8s.io/) for simplicity.

### Step 2. Configure your values.yaml

Open up `kubernetes/eduvize/values.yaml`, we will be looking over a few different items here.

You can read more about specific environment variables and other settings in `SETUP.md`

#### Ingress

In order to serve the Eduvize frontend and API, you will need to ensure the following are set properly:

- **Hostname**: This will be the domain name of your Eduvize instance.
- **Ingress Class**: Set this to whichever ingress class you want to use in your cluster.
  - If you're using microk8s, this will likely be `public`
- **TLS**: If you plan to use https, make sure `enabled` is set to `true`
  - **Cluster Issuer**: Set the `clusterIssuer` field to the name of your `cert-manager` issuer.

#### Frontend

Build and push the `client` docker image to a repository that is accessible from within your cluster.

- **Image**: Set the `image` field to the repository and tag you want to use for the frontend

#### Database

Build and push the `backend/database.Dockerfile` image to a repository that is accessible from within your cluster.

**Name**: The `name` field is used to create a new database on the Postgres server

**Size**: The size allocated to the Postgres server

**User**: The postgres user that will be used by Eduvize

**Password**: Mapped to a secret - adjust `name`, `secret`, and `key` accordingly

#### Storage

By default, the bitnami flavor of MinIO is used. Feel free to use any variant images.

**Bucket Name**: The name of the bucket that is created in MinIO to use for object storage

**Size**: How much space to allocate to object storage

#### API

Build and push the `backend/api.Dockerfile` image to a repository that is accessible from within your cluster.

**Image**: Set the `image` field to the repository and tag you want to use for the API

Environment Variables

| Name                 | Description                                                        |
| -------------------- | ------------------------------------------------------------------ |
| PUBLIC_UI_URL        | The public address to the frontend                                 |
| PUBLIC_URL           | The public address to the API                                      |
| DASHBOARD_ENDPOINT   | The path segment name for the frontend dashboard                   |
| NOREPLY_ADDRESS      | The email address to use as the `From` address when sending emails |
| AUTH_REDIRECT_URL    | The public address to the authentication screen                    |
| S3_ACCESS_KEY        | The MinIO root username                                            |
| S3_SECRET_KEY        | The MinIO root password                                            |
| OPENAI_KEY           | The API key to use for OpenAI transactions                         |
| MAILGUN_API_KEY      | The API key to use for Mailgun transactions                        |
| GITHUB_CLIENT_ID     | The OAuth client ID to use for Github authentication               |
| GITHUB_CLIENT_SECRET | The OAuth client secret to use for Github authentication           |
| GOOGLE_CLIENT_ID     | The OAuth client ID to use for Google authentication               |
| GOOGLE_CLIENT_SECRET | The OAuth client secret to use for Google authentication           |

#### Course Generator

Build and push the `backend/jobs/Dockerfile` image with the build argument `JOB_NAME` set to `course_generator` to a repository that is accessible within your cluster.

**Image:**: Set the `image` field to the repository and tag you want to use

Environment Variables

| Name       | Description                                |
| ---------- | ------------------------------------------ |
| OPENAI_KEY | The API key to use for OpenAI transactions |

#### Playground

Build and push the following images to a repository accessible from within your cluster:

**Controller Image**: `playground/Dockerfile`

**Environment Images**: `playground/environment.Dockerfile`

**Orchestrator Image**: `playground-orchestrator/Dockerfile`

#### Kafka

Set the `bootstrapServers` field to the service name of your `Kafka` deployment with the port of your assigned listener (i.e `9092`)

#### Redis

By default, the official `redis` image is used. Set this to any variant you wish.

#### Persistence

Set `storageClass` to whichever works best for your setup. If you're using microk8s, this would probably be `microk8s-hostpath`.

#### Bearer Auth

This maps the secret keys used to sign json web tokens for both users and playground sessions. Ensure these are created before chart deployment.

#### Private Registry

If you're using a private registry hosted within your cluster for docker images, set `enabled` to `true`. You'll need to make a Secret with the credentials ([read this](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/) for more info) so Kubernetes knows how to authenticate.

### Step 3. Deploy Eduvize

Navigate to the `kubernetes/eduvize` folder in this repository and simply run the following command:

```plaintext
helm install eduvize . --namespace {YOUR_NAMESPACE}
```

If everything was configured correctly, you should be able to access your Eduvize instance after a short duration!
