![Eduvize Logo](https://github.com/user-attachments/assets/30ac9425-b080-42ce-8c98-ef0a0eed8b3b)
## Introduction
**Eduvize** is an open-source platform built to enhance developers' skills using AI-driven personalized learning. By contributing to Eduvize, you'll be helping to create a tool that empowers engineers to stay ahead in the rapidly evolving tech landscape through a tailored, interactive experience.

You can access the live platform by going to [eduvize.dev](https://eduvize.dev).

## Project Overview

Eduvize is more than just a learning platform—it's a developer's companion designed to provide a hands-on, practical approach to mastering modern software development skills. The platform leverages AI to generate personalized content, allowing users to focus on what they need to grow, whether that's understanding new frameworks, improving coding proficiency, or exploring advanced concepts in software engineering.

### Tech Stack

#### Frontend

- **Language**: TypeScript
- **Framework**: React
- **Build Tooling**: Vite
- **Core Dependencies**:
  - **Mantine** - UI Library
  - **Monaco** - IDE library, the same one that powers VSCode
  - **react-router-dom** - In-app routing
  - **react-markdown** - Markdown rendering library
  - **xterm.js** - Library for rendering realistic terminal interfaces

#### Backend

- **Language**: Python
- **Framework**: FastAPI
- **Core Dependencies**:
  - **SQLModel** - Abstraction over Pydantic and SQLAlchemy for database and ORM procedures
  - **Socket.IO** - Websocket abstraction library
  - **PDF2Image** - Library for converting PDF files to images
  - **OpenAI** - Library for interfacing with the OpenAI API
  - **Confluent Kafka** - Library for creating consumers and producers
  - **Boto3** - Library supporting the Amazon S3 object storage protocol


#### Infrastructure

- **Apache Kafka**: A real-time messaging service for streaming events across backend services
- **MinIO**: An open source object storage service replicating most of Amazon S3's capabilities
- **Postgres**: DBMS
- **Redis**: Cache

### Getting Started

To get involved with Eduvize, follow these steps:

1. **Clone the Repository**: Start by cloning the repository to your local development environment.

   ```
   git clone https://github.com/cameron5906/eduvize-ai.git
   cd eduvize-ai
   ```

2. **Set Up the Environment**: Check out [SETUP.md](#SETUP.md) for more information about getting the platform running in your local development environment.

4. **Start Contributing**: Check out the `issues` section for tasks that need attention. Whether you're interested in squashing bugs, adding new features, or improving documentation, there's plenty to do.

### Technical Details

Take a look at the `docs/` directory for technical information including architecture, primary user flows, and data flow.

### Why  Contribute?

Eduvize is more than a project—it's a mission to democratize learning and make advanced software development skills accessible to all. By contributing, you'll have the opportunity to:

- **Shape the Future of Developer Education**: Your work will directly impact how developers learn and grow, helping them stay competitive in an ever-changing industry.
- **Collaborate with a Global Community**: Engage with other passionate developers, share knowledge, and learn from each other.
- **Build Your Portfolio**: Showcase your skills by contributing to a project that's making a real difference.

## License

Eduvize is licensed under the Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0). See the [LICENSE](LICENSE) file for details.

## Contributing

We welcome all kinds of contributions. Check out our [Contributing Guidelines](CONTRIBUTING.md) to get started.