# How to Start

This guide provides instructions on how to set up and run this project in both a development and a production-like environment.

## Prerequisites

Before you begin, ensure you have the following installed:

*   Python 3
*   pip
*   Git
*   For the production-like environment on macOS: [Homebrew](https://brew.sh/)

## Initial Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Create your environment file:**

    Copy the example environment file and fill in the values:

    ```bash
    cp .env.example .env
    ```

    You will need to provide a `SECRET_KEY` and set the `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` for your environment.

## Development Server

The development server is suitable for local development and testing.

### Start the Development Server

1.  **Activate the virtual environment (if not already activated):**

    ```bash
    source venv/bin/activate
    ```

2.  **Run the server:**

    ```bash
    source .env && python manage.py runserver
    ```

    The server will be available at `http://localhost:8000`.

### Stop the Development Server

Press `Ctrl+C` in the terminal where the server is running.

## Production-like Server

This setup uses Gunicorn, Nginx, and Supervisor to create a more robust environment that can handle multiple users. The following instructions are tailored for macOS with Homebrew.

### Initial Setup for Production-like Environment

1.  **Install Nginx and Supervisor:**

    ```bash
    brew install nginx
    pip install supervisor
    ```

2.  **Configure Gunicorn, Nginx, and Supervisor:**

    This project includes template configuration files for Gunicorn (`gunicorn_start.bash`), Nginx (`nginx.conf`), and Supervisor (`supervisord.conf`). You will need to review and adapt these files to your specific environment, paying close attention to file paths and user/group settings.

### Start the Production-like Server

1.  **Start Nginx:**

    Load the Nginx configuration. You may need to include the `nginx.conf` from this project in your main Nginx configuration file (e.g., `/opt/homebrew/etc/nginx/nginx.conf`).

    ```bash
    nginx -c <path-to-your-main-nginx.conf>
    ```

2.  **Start Supervisor:**

    ```bash
    supervisord -c /path/to/your/project/supervisord.conf
    ```

    The application will be available at the URL you configured in your Nginx setup (e.g., `http://localhost:8081`).

### Stop the Production-like Server

1.  **Stop the Gunicorn process:**

    ```bash
    supervisorctl -c /path/to/your/project/supervisord.conf stop timeline_project
    ```

2.  **Stop Supervisor:**

    ```bash
    supervisorctl -c /path/to/your/project/supervisord.conf shutdown
    ```

3.  **Stop Nginx:**

    ```bash
    nginx -s stop
    ```

## Checking Status and Restarting Servers

### Development Server

*   **Status:** Observe the terminal output for logs and errors.
*   **Restart:** Stop the server with `Ctrl+C` and start it again.

### Production-like Server

*   **Check Gunicorn Status:**

    Use `supervisorctl` to check the status of the Gunicorn process:

    ```bash
    supervisorctl -c /path/to/your/project/supervisord.conf status
    ```

*   **Restart Gunicorn:**

    To restart the Gunicorn process after making changes to the application code:

    ```bash
    supervisorctl -c /path/to/your/project/supervisord.conf restart timeline_project
    ```

*   **Check Nginx Configuration:**

    Before reloading Nginx, it's a good practice to test the configuration for syntax errors:

    ```bash
    nginx -t
    ```

*   **Reload Nginx:**

    To apply changes to the Nginx configuration without stopping the server:

    ```bash
    nginx -s reload
    ```
