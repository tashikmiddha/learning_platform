# 🧠 AI Personalized Learning Platform

Welcome to the **AI Personalized Learning Platform** – a web-based solution designed to personalize the education experience using modern web technologies and AI. This platform empowers users to interact with courses, chat with an AI tutor, generate curriculum, summarize video lectures, and take quizzes – all in one place.

---

## 🚀 Features

- 🎓 **Dashboard** – Overview of learning progress.
- 📚 **Courses** – Browse and access structured course content.
- 🤖 **AI Chatbot** – Chat with an AI tutor to clarify concepts and get instant help.
- 🧩 **Curriculum Generator** – Generate personalized learning paths using AI.
- 🎥 **Video Summarization** – Upload videos and get concise summaries.
- 📝 **Quiz Section** – Take interactive quizzes and check understanding.
- 🔐 **Authentication** – Register/Login securely with user-based views.
- 🌐 **Responsive Design** – Fully responsive with Bootstrap 5 for seamless usage on all devices.

---

## 🛠️ Built With

- **Python** & **Django** – Backend & templating
- **HTML5 / CSS3 / Bootstrap 5** – Frontend UI
- **JavaScript** – Interactive enhancements
- **AI APIs or Models** – For chatbot, summarization, and curriculum generation *(implementation-dependent)*

---

## 📁 Project Structure

    ```bash
    project/
    ├── templates/
    │   └── base.html           # Main layout with navbar, footer, and blocks
    ├── static/
    │   └── css/                # Custom styles (if any)
    ├── app_name/
    │   ├── views.py            # Views for dashboard, chatbot, etc.
    │   ├── urls.py             # URL routing
    │   ├── models.py           # Data models
    │   └── templates/          # App-specific templates
    ├── manage.py
    ├── db.sqlite3
    └── README.md

✅ How to Run Locally
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/ai-learning-platform.git
   cd ai-learning-platform

3. Create and activate virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

5. Install dependencies
   ```bash
   pip install -r requirements.txt

7. Apply migrations
   ```bash
   python manage.py migrate

9. Run the development server
    ```bash
   python manage.py runserver

11. Access the app
    ```bash
    Open your browser and visit: http://127.0.0.1:8000

🔐 User Authentication

The navbar dynamically updates based on user authentication status.

Logged-in users can access all features (Dashboard, Courses, Chatbot, etc.)

Visitors can only see Login and Register options.

📌 Customization

Navbar: Easily customizable in base.html.

Styling: Extend Bootstrap styling with custom CSS.

Add More Features: Expand views, models, and templates based on your educational use case.

📄 License

This project is open-source. Feel free to modify and build upon it for educational or personal use.

🙋‍♂️ Author

Made with ❤️ by Tashik

