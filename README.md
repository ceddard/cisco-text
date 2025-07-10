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

## AI Assistant System Prompts

Each AI assistant is defined by a specialized system prompt that shapes its responses:

**Imaginary Tool Inventor** - Located in `src/app/services/chat/inventor_chat_service.py`
   - Creates whimsical inventions with names, descriptions, and taglines
   - Structured output with emoji formatting

**Unspoken Feelings Translator** - Located in `src/app/services/chat/translator_chat_service.py`
   - Analyzes messages for emotional subtext and hidden meanings
   - Returns original message, likely subtext, and detected emotions

**Dream Curator** - Located in `src/app/services/chat/curator_chat_service.py`
   - Transforms dream descriptions into artistic interpretations
   - Generates title, art description, image prompt for DALL-E, and micro-story

This prompt was crafted to turn dream descriptions into structured, surreal outputs combining storytelling and visual imagination. It's ideal for use with generative image models (like DALL·E or Midjourney) and narrative applications.

Why this format?

Persona-driven: Defines the model as a dream interpreter and surreal artist

Structured output: Title, visual description, image prompt, and micro-story

Ready for multimodal use: The image prompt is directly usable in AI image generation

Examples included: Two detailed samples guide the model toward creative, high-quality results

Even a minimal input like “I was flying in circles” will yield a vivid, symbolic interpretation with poetic flair and image-ready content.


### Prerequisites

- Docker and Docker Compose
- OpenAI API key

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

## API Logging System

The application includes a comprehensive logging system that:

1. Captures all API requests and responses
2. Stores logs in Redis with configurable TTL (default: 7 days)
3. Provides an API endpoint to query logs at `/logs`
4. Offers filtering by request ID or API path