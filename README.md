# Creative AI Assistant

A modern web application that allows users to interact with three different AI assistants:

- 🎨 **Imaginary Tool Inventor** - Generates magical or futuristic products based on everyday problems
- 🧠 **Unspoken Feelings Translator** - Interprets the hidden emotional meaning behind ambiguous messages
- 🌙 **Dream Curator** - Transforms surreal dream descriptions into artwork and micro-stories

## Project Structure

```
cisco-text/
├── client/               # Frontend React application
│   ├── public/           # Static assets
│   └── src/              # React source code
│       ├── App.js        # Main application component
│       ├── App.css       # Application styles
│       ├── index.js      # Entry point
│       └── setupProxy.js # Development proxy configuration
└── src/                  # Backend FastAPI application
    ├── app/              # API modules and routers
    │   ├── core/         # Core interfaces and abstractions
    │   ├── middleware/   # Request/response logging middleware
    │   ├── routers/      # API routes
    │   └── services/     # Service implementations
    └── main.py           # FastAPI entry point
```

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Installation

#### With Docker (Recommended)

1. Clone the repository
2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
3. Edit the `.env` file with your OpenAI API key
4. Run the Docker Compose setup:
   ```bash
   # On Linux/macOS
   ./start-docker.sh
   
   # On Windows
   start-docker.bat
   ```

This will start:
- The backend API on http://localhost:8000
- The frontend on http://localhost
- Redis for logging on port 6379
- Redis Commander UI on http://localhost:8081

#### Manual Setup (Development)

1. Clone the repository
2. Set up the backend:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the frontend:
   ```bash
   cd client
   npm install
   ```
4. Run Redis (either locally or with Docker):
   ```bash
   docker run -d -p 6379:6379 --name cisco-redis redis:alpine
   ```

### Running the Application Manually

For Windows users, simply run:
```
start-all.bat
```

This will start both the backend server (on port 8000) and the frontend development server (on port 3000).

Alternatively, you can run them separately:

1. Start the backend:
   ```
   start-backend.bat
   ```
2. Start the frontend:
   ```
   cd client
   start-frontend.bat
   ```

## API Logging System

The application includes a comprehensive logging system that:

1. Captures all API requests and responses
2. Stores logs in Redis with configurable TTL (default: 7 days)
3. Provides an API endpoint to query logs at `/logs`
4. Offers filtering by request ID or API path