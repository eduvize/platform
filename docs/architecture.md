## High-Level Architecture

Eduvize is divided up into several high level components and is designed to run in either a Kubernetes or Docker Compose environment.

### Application components

- **Frontend**: A React single-page application
- **Backend API**: Python API built on top of FastAPI and Socket.IO
- **Course Generator**: A Python application that generates course content in the background, invoked with Kafka events
- **Playground Orchestrator**: A Python job that monitors sessions in the database, as well as running pod instances in a Kubernetes environment
- **Playground Controller**: A Python program that connects to the backend over Socket.IO and initializes a shell session into a volume shared with a sandboxed environment

### Infrastructure components

- **Kafka**: Realtime transport layer for communicating events between decoupled services
- **MinIO**: A blob storage system based on the AWS S3 API
- **Postgres**: Primary database engine 
- **Redis**: Caching layer for both key/value pairs and a backend for Socket.IO when operating multiple replicas

![Blank diagram - Page 1 (2)](C:\Users\camer\Downloads\Blank diagram - Page 1 (2).png)

## Frontend

The frontend is a React single page application built with [Vite](https://vitejs.dev/). The primary UI framework is [Mantine](https://mantine.dev/).

## Backend

The backend is a monolithic Python API built around [FastAPI](https://fastapi.tiangolo.com/). It uses [SQLModel](https://sqlmodel.tiangolo.com/) within the data layer. 

The backend server exposes both a REST-based API, as well as a [Socket.IO](https://socket.io) endpoint for dealing with bi-directional, real-time workloads like the playground.

## Course Generator

The course generator is a Kafka consumer that listens for new course generation events that get produced from the API. It processes the course outline in the message and iterates over each learning module to create reading material. Once complete, it stores all of this content in the database.

## Playground Orchestrator

The orchestrator is a single replica job that monitors a `sessions` table in the database (maintained by the API) and pods of a specific `app` label in Kubernetes. Every few seconds, the lists are reconciled and it determines which pods are no longer needed, or how many new ones to scale up to. Once a pod is created, the orchestrator will update the session's row in the database with the pod hostname.

## Playground

The playground is a pod that runs two containers: the Python controller script and the actual sandbox environment that will execute the user's inputs. These containers share a single volume.

The controller script connects to the backend API via Socket.IO and exposes a shell process. While the playground is only internally accessible within the cluster, the user is able to send Socket.IO messages to the backend API which will then relay to the controller, and vice versa.