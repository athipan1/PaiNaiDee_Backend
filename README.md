# PaiNaiDee_Backend

This is the backend for the PaiNaiDee application, a Flask-based API for finding and managing attractions.

## Running the Application

There are two ways to run the application: locally for development or using Docker.

### Local Development

1. **Prerequisites:**
   - Python 3.9 or higher
   - PostgreSQL installed and running

2. **Installation:**
   - Clone the repository:
     ```bash
     git clone https://github.com/athipan1/PaiNaiDee_Backend.git
     cd PaiNaiDee_Backend
     ```
   - Create and activate a virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
     ```
   - Install the dependencies:
     ```bash
     pip install -r requirements.txt
     ```

3. **Configuration:**
   - Create a `.env` file in the root of the project and add the following, replacing the values with your local PostgreSQL details:
     ```env
     DB_HOST=localhost
     DB_NAME=painaidee_db
     DB_USER=postgres
     DB_PASSWORD=your_password
     DB_PORT=5432
     FLASK_ENV=development
     ```

4. **Running the Application:**
   - Run the application:
     ```bash
     flask run
     ```
   - The API will be available at `http://localhost:5000`.

### Docker

1. **Prerequisites:**
   - Docker and Docker Compose installed and running

2. **Running the Application:**
   - From the root of the project, run:
     ```bash
     docker-compose up --build
     ```
   - The API will be available at `http://localhost:5000`.