# 🚀 Secure Server Application with FastAPI and JWT

This project is a secure server application built using the powerful Python framework **FastAPI** and the **JSON Web Token (JWT)** authentication mechanism. It provides a robust and scalable solution for managing user authentication and authorization.

---

## 🛠️ **Getting Started**

Follow these steps to set up and run the project locally:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-repository>.git
   cd <your-repository>
   ```

2. **Switch to the Desired Branch**:
   ```bash
   git checkout -b lb2 origin/lb2
   ```

3. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables**:
   - Create a `.env` file in the root directory with the required settings (e.g., database URL, token secrets, etc.). Refer to `example.env` for guidance.

6. **Run Database Migrations**:
   ```bash
   alembic upgrade head
   ```

7. **Start the Server**:
   ```bash
   uvicorn main:app --reload
   ```

8. **Access the API**:
   - Open your browser and navigate to `http://127.0.0.1:8000/docs` to explore the Swagger UI.

---

## 2️⃣ **Development Tasks** 🛠️

1. **Create 7 Routes**: Add the following routes to the application:
   - `/register` for user registration.
   - `/login` for user authentication.
   - `/user-info` to retrieve authenticated user information.
   - `/logout` to log out and revoke the access token.
   - `/tokens` to list active tokens for the user.
   - `/revoke-all-tokens` to revoke all tokens of the authenticated user.
   - `/change-password` for password change functionality.

2. **Request Classes**: Create **2 request classes**:
   - **AuthenticationRequest**: To handle user login details.
   - **RegistrationRequest**: To process user registration data.

3. **DTO (Data Transfer Object) Classes**: Define **3 DTO classes**:
   - **AuthTokenDTO**: To structure authentication tokens.
   - **UserDTO**: To format user information.
   - **RegistrationDTO**: To structure registration data.

4. **Add Methods**: Include a method in each request class that returns an instance of the corresponding resource.

5. **Controller Class**: Implement a controller class containing methods for all 7 routes.

---

## 3️⃣ **Controller Methods** 📋

1. **Registration**:
   - **Input**: An instance of the `RegistrationRequest` class.
   - **Output on Success**: Returns the created user resource with a `201` status code.
   - **Output on Failure**: Returns an error message with a problem description.

2. **Authentication**:
   - **Input**: An instance of the `AuthenticationRequest` class.
   - **Output on Success**: Returns an access token with a `200` status code.
   - **Output on Failure**: Returns an error message with a problem description.

3. **User Information Retrieval**:
   - Returns the authenticated user's resource instance.

4. **Logout**:
   - Revokes the used access token and ensures it can no longer be used.

5. **Active Tokens List**:
   - Returns a list of all active tokens associated with the authenticated user.

6. **Revoke All Tokens**:
   - Revokes all active tokens for the authenticated user and returns a `200` status code.

7. **Password Change**:
   - Allows the user to change their password after confirming their current password.

---

## 4️⃣ **Configuration** ⚙️

1. **Token Security**:
   - Implement measures to protect tokens from interception.
   - Note: The specific implementation method is flexible.

2. **Refresh Tokens**:
   - Ensure the use of refresh tokens for obtaining new access tokens.

3. **Active Tokens Limit**:
   - Set a limit on the maximum number of active tokens per user in the environment configuration.

4. **Token Lifetime**:
   - Configure token expiration through environment variables or application settings.

---

## 5️⃣ **Final Steps** ✅

1. **Commit Changes**:
   - Save your progress by committing the changes:
     ```bash
     git add .
     git commit -m "Implemented JWT-based authentication system"
     ```

2. **Push Changes to Remote Branch**:
   - Publish your updates to the `lb2` branch:
     ```bash
     git push origin lb2
     ```

---

