## Eduvize Local Setup Instructions

To get started developing Eduvize in your local environment, follow the steps below.

### **Step 1.** Install Prerequisites

#### Base requirements

Install Docker

You'll need to ensure [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or equivalent such as [Rancher Desktop](https://docs.rancherdesktop.io/)) is installed on your system.

Create an OpenAI Key

If you haven't already, create an OpenAI Platform account by [visiting this link](https://platform.openai.com/signup).

1.  Once signed in, go to the [Project API Keys](https://platform.openai.com/api-keys) page
2.  Click `Create new secret key`
3.  After filling out the details, click `Create secret key`
4.  Copy the key which will be used in the step below

Create a Mailgun API Key

If you need to make an account with Mailgun, [visit this link](https://signup.mailgun.com/new/signup) - it's free to get started.

1.  Once signed in, go to the [API Security](https://app.mailgun.com/settings/api_security) page
2.  Click `Create API key`
3.  Copy the key once created for use in the step below

#### OAuth Authentication

If you intend to use OAuth for sign-in, follow these steps:

Github

1.  Log in to GitHub
2.  At the top right, click your profile icon and select `Settings`
3.  At the very bottom of the left sidebar, click `Developer settings`
4.  Click `OAuth Apps`
5.  On the top right, click `New OAuth App`
6.  Fill out the form, entering the address of the authentication screen (below) into `Authorization callback URL` (it's http://localhost:5173/auth by default)
7.  Once created, copy the `Client ID`, click `Generate new client secret` and copy that as well to be used in the steps below.

Google

1.  Log in to the [Google Cloud Console](https://console.cloud.google.com/)
2.  On the top left, open the hamburger menu and select `APIs &amp; Services -&gt; Credentials`
3.  Click `+ Create credentials` and select `OAuth client ID`
4.  On the next screen, select `Web application`
5.  Enter your `Authorized JavaScript origins` (the domain name you will be hosting from, it's http://localhost:5173 by default)
6.  Enter your `Authorized redirect URI` (the address to the auth screen, it's http://localhost:5173/auth by default)

### Step 2. Configure environment

In `src/backend`, create a `.env` file and add the following:

| Environment Variable     | Description                                                         | Default                    |
| ------------------------ | ------------------------------------------------------------------- | -------------------------- |
| PUBLIC_UI_URL            | The address your UI will be accessible from                         | http://localhost:5173      |
| PUBLIC_URL               | The address that the backend will be accessible from                | http://localhost:8000/api  |
| DASHBOARD_ENDPOINT       | The path segment for the user dashboard                             | dashboard                  |
| PORT                     | The backend port to listen on                                       | 8000                       |
| POSTGRES_HOST            | The hostname of the postgres server                                 | localhost                  |
| POSTGRES_USER            | The app user for connecting to postgres                             |                            |
| POSTGRES_PASSWORD        | The app user password for connecting to postgres                    |                            |
| POSTGRES_DB              | The name of the Eduvize database in postgres                        |                            |
| S3_ENDPOINT              | The base endpoint for MinIO / S3                                    |                            |
| S3_ACCESS_KEY            | The access key to use when making requests to MinIO / S3            |                            |
| S3_SECRET_KEY            | The secret key / password to use when making requests to MinIO / S3 |                            |
| S3_BUCKET                | The bucket to use for blob storage within MinIO / S3                |                            |
| REDIS_HOST               | The hostname and port (colon separated) to use to connect to Redis  | localhost:6379             |
| MAILGUN_API_KEY          | The API key to use with Mailgun for the sending of email            |                            |
| NOREPLY_ADDRESS          | The From address to use when sending email                          |                            |
| OPENAI_KEY               | The API key to use for interacting with the OpenAI API              |                            |
| TOKEN_EXPIRATION_MINUTES | The length of time an access token should be valid, in minutes      | 30                         |
| GITHUB_CLIENT_ID         | A client ID to use for Github authentication                        |                            |
| GITHUB_CLIENT_SECRET     | The secret to use for Github authentication                         |                            |
| GOOGLE_CLIENT_ID         | The client ID to use for Google authentication                      |                            |
| GOOGLE_CLIENT_SECRET     | The secret to use for Google authentication                         |                            |
| AUTH_REDIRECT_URL        | The address to use as a redirect when completing the OAuth flow     | http://localhost:5173/auth |

Additionally, you'll need to navigate to `src/client` and create a `.env.local` file, add the following:

| Environment Variable   | Description                                                     | Default                   |
| ---------------------- | --------------------------------------------------------------- | ------------------------- |
| VITE_API_ENDPOINT      | The address to the API (including `/api` suffix)                | http://localhost:8000/api |
| VITE_SOCKETIO_ENDPOINT | The address to the Socket.IO server                             | http://localhost:8000     |
| VITE_GITHUB_CLIENT_ID  | The client ID to use when redirecting to OAuth login for Github |                           |
| VITE_GOOGLE_CLIENT_ID  | The client ID to use when redirecting to OAuth login for Google |                           |

### Step 3. Start the backend environment

To start up the Eduvize backend environment, navigate to `src/backend` and simply run the following:

```plaintext
docker-compose up -d
```

To shut it down:

```plaintext
docker-compose down
```

### Step 4. Start the client server

Once the backend is ready, navigate to `src/client` and run the following:

```plaintext
npm i
npm start
```

You're done. You can now visit the client in your browser and start using Eduvize locally!

You can log in with the test account:

```plaintext
Email: tester@eduvize.dev
Password: testpassword
```
