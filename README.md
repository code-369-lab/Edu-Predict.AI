# EduPredict.AI 🎓 ✨

EduPredict.AI is a cutting-edge, Full-Stack Real-Time Web Application designed to predict student performance using Machine Learning. It provides actionable recommendations, live data streaming, explainable AI impact tracking, and an integrated Intelligent Study Assistant.

---

## 🚀 Features

*   **Real-Time Data Streaming**: Simulates live student activity (attendance, study hours) fed directly via WebSockets.
*   **Live Teacher Dashboard**: Monitors all active students and instantly flashes alerts when risk thresholds are met.
*   **Explainable AI (XAI)**: Shows *exactly why* a prediction was made, breaking down the positive and negative point impacts of habits like sleep and study hours.
*   **Interactive Profile Radar Chart**: Uses `Chart.js` to draw a dynamic comparison of the student’s habits against an "Ideal Standard Baseline".
*   **AI Study Assistant Portal**: A dedicated tool where students can type any academic subject and instantly generate an intelligent topic summary, interactive 3D Flashcards, and a day-by-day Study Schedule.
*   **Progressive Web App (PWA) Offline Mode**: Installs securely to your device. If the internet goes down, the embedded Service Worker takes over, allowing you to ask the **Offline AI Chatbot** questions about prediction logic entirely client-side!
*   **Secure Authentication**: Role-based access control protecting student history and teacher live streams using `Flask-Login` and `bcrypt`.
*   **Exportable PDF Reports**: Easily save or print prediction results natively within the browser using dedicated print stylesheets.

---

## 🛠️ Technology Stack

*   **Backend**: Python, Flask, Flask-SQLAlchemy (SQLite)
*   **Real-Time**: Flask-SocketIO, Eventlet
*   **Machine Learning (Mock)**: Scikit-Learn (Simulated Random Forest Classifier via procedurally generated algorithmic logic)
*   **Frontend**: HTML5, Vanilla CSS (Glassmorphism UI), Vanilla JavaScript
*   **Visualizations**: Chart.js
*   **PWA**: Service Workers (Stale-While-Revalidate Caching structure)
*   **Deployment Integration**: Validated for Render, Docker, AWS, and Heroku.

---

## 💻 Local Installation & Setup

Want to run this locally on your own machine?

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/YOUR_USERNAME/edupredict-ai.git
    cd edupredict-ai
    ```

2.  **Create a Virtual Environment (Recommended)**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Server**
    *(Make sure you run using the Python file natively to ensure Eventlet WebSockets boot up correctly).*
    ```bash
    python app.py
    ```

5.  **Access the Application**
    Open your browser to: `http://127.0.0.1:5000`

---

## 🌐 Deployment to Render (Free Tier)

This application is optimized for deployment on Render.com's web hosting platform!

1. Upload this repository to your GitHub account.
2. Sign up at [Render.com](https://render.com).
3. Click **New +** and select **Web Service**.
4. Connect the GitHub repository.
5. In the settings, ensure you have:
    *   **Runtime**: Python 3
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app`
6.  Scroll down to the bottom and select the **Free** tier.
7.  Under **Advanced**, add a new Environment Variable:
    *   **Key**: `SECRET_KEY`
    *   **Value**: `your_super_secret_random_text_here`
8. Click **Create Web Service**.

---

## 👥 Roles & Access

By default, the application supports two user roles when registering:

*   **Student**: Access to the Prediction Profiler, Profile Tracking, XAI charts, and the AI Study Assistant Mode.
*   **Teacher**: Exclusive access to the `/dashboard` Live Streaming view handling thousands of mock data points simultaneously.

---

*Built for education. Designed to scale.*
