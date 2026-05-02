## Features

-  **Authentication**: JWT-based auth with refresh tokens
-  **Messenger**: Private and group chats
-  **Task Management**: Create, update, and track tasks
-  **Olympiads**: Track competition participation
-  **Internationalization**: Multi-language support (i18n)
-  **Responsive UI**: Modern, mobile-friendly interface

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy (Async), SQLite/PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Security**: JWT, bcrypt password hashing
- **Containerization**: Docker, Docker Compose

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd fastapi_app

# Set environment variables
export SECRET_KEY=$(openssl rand -hex 32)
export DEBUG=True

# Run with Docker Compose
docker-compose up --build
```

The application will be available at `http://localhost:8000`

### Manual Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SECRET_KEY=$(openssl rand -hex 32)
export DEBUG=True

# Run the application
uvicorn main:app --reload
```

## API Documentation

Once running, access the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite+aiosqlite:///./devstudio.db
DEBUG=True
ALLOWED_ORIGINS=["http://localhost:8000","http://127.0.0.1:8000"]
PASSWORD_MIN_LENGTH=8
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (required for production) | Auto-generated |
| `DATABASE_URL` | Database connection string | SQLite local |
| `DEBUG` | Enable debug mode | `True` |
| `ALLOWED_ORIGINS` | CORS allowed origins | localhost only |
| `PASSWORD_MIN_LENGTH` | Minimum password length | `8` |

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user

### Users
- `GET /api/users/search?query=` - Search users
- `GET /api/users/{user_id}` - Get user by ID

### Messenger
- `GET /api/messenger/chats` - Get all chats
- `POST /api/messenger/chats` - Create chat
- `GET /api/messenger/chats/{chat_id}/messages` - Get chat messages
- `POST /api/messenger/messages` - Send message
- `GET /api/messenger/messages/direct/{user_id}` - Get direct messages
- `PATCH /api/messenger/messages/{message_id}/read` - Mark as read

### Tasks
- `GET /api/tasks/?skip=0&limit=20` - Get tasks (paginated)
- `POST /api/tasks/` - Create task
- `PATCH /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task

### Health & Info
- `GET /health` - Health check endpoint
- `GET /api` - API information

## Password Requirements

Passwords must meet the following criteria:
- Minimum 8 characters (configurable via `PASSWORD_MIN_LENGTH`)
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

## Development

### Running Tests

```bash
pytest
```

### Code Style

This project follows PEP 8 guidelines. Use `black` and `flake8` for formatting and linting.

## Project Structure

```
fastapi_app/
├── app/
│   ├── api/           # API routes
│   ├── core/          # Core configuration
│   ├── db/            # Database setup
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── static/        # Static files
│   └── templates/     # HTML templates
├── tests/             # Test files
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Security Notes

- Always change `SECRET_KEY` in production
- Use HTTPS in production
- Enable rate limiting for production deployments
- Regularly update dependencies


## Support

For issues and questions, please open an issue on the GitHub repository.
