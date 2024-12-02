# Microsoft_outlook_llm

# Flask Authentication and Calendar Integration

## Overview

This project is a Flask-based web application that supports user authentication via Microsoft and Google, allowing secure login and access to Microsoft calendar events. It integrates with Microsoft Graph API for managing calendar events and uses SQLAlchemy to interact with a MySQL database for storing user data. The application uses Flask-JWT-Extended for token-based authentication, ensuring secure access to its endpoints.

## Features

- **Microsoft and Google Login**: Users can log in using either Microsoft or Google credentials.
- **Token-Based Authentication**: Uses JWT for secure API access.
- **Calendar Event Management**: Integrates with Microsoft Graph API to manage calendar events, including retrieving, creating, updating, and deleting events.
- **Password Security**: Passwords are hashed using Flask-Bcrypt for security.
- **CORS Support**: Flask-CORS is enabled to handle cross-origin requests.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   - Create a `.env` file with your configuration values (API keys, database credentials, etc.).

4. **Set Up the Database**:
   - Ensure you have a MySQL database running and update the database credentials in the Flask app configuration.
   - Run the migrations:
   ```bash
   flask db upgrade
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```

## Usage

- **Microsoft Login Endpoint**: `/microsoft-login` (POST)
- **Google Login Endpoint**: `/google-login` (POST)
- **Fetch Microsoft Calendar Events**: `/fetch_microsoft_calendar_events` (POST)

## Security Considerations

- Keep API keys and sensitive credentials secure by storing them in environment variables or configuration files not included in version control.
- Ensure password hashing is always used for user credentials.

## Dependencies

- **Flask**: Web framework for the application.
- **Flask-JWT-Extended**: For token-based authentication.
- **Flask-Bcrypt**: For hashing passwords.
- **Flask-CORS**: To allow cross-origin requests.
- **SQLAlchemy**: For database interaction.
- **Microsoft Graph API**: For managing calendar events.

## Notes

This application is suitable for projects needing federated login using Microsoft or Google and integration with Microsoft calendar services. It ensures secure user management and access to calendar functionalities.

Feel free to contribute or suggest improvements!

