# SchemeAI – AI Chatbot for Government Scheme Recommendation

SchemeAI is a web-based conversational intelligence platform designed to recommend relevant Central and State Government schemes to citizens based on their demographics, income, occupation, and other eligibility criteria.

This is the initial skeleton layout of the project, establishing a clean, modular structure following Python Flask best practices.

---

## 📂 Project Directory Structure

```text
ai chatbot for government schemes/
├── data/                      # Contains static scheme data and user profile schemas
│   └── .gitkeep               # Placeholder file
├── models/                    # AI/ML models, NLP scripts, and recommendation algorithms
│   └── .gitkeep               # Placeholder file
├── static/                    # Public static assets loaded directly by the browser
│   ├── css/
│   │   └── style.css          # Main stylesheet with premium theme styling
│   ├── images/
│   │   └── .gitkeep           # Image resources (logos, illustration assets)
│   └── js/
│       └── script.js          # Interactive frontend micro-interactions
├── templates/                 # Jinja2 HTML templates rendered by Flask
│   └── index.html             # Homepage / Main interface layout
├── utils/                     # Shared helper functions (validators, data cleaners, API clients)
│   └── .gitkeep               # Placeholder file
├── app.py                     # Main Flask application entry point
├── README.md                  # Project documentation and guide (this file)
└── requirements.txt           # Python library dependencies
```

---

## 🧩 Directory & File Explanations

### Folders

1. **`templates/`**
   - **Purpose**: Holds HTML files rendered by Flask using the Jinja2 templating engine. The backend routes dynamically inject data into these HTML pages before sending them to the client.
2. **`static/`**
   - **`static/css/`**: Stores cascading style sheets (CSS) defining page layout, colors, typography, and responsive media rules.
   - **`static/js/`**: Contains client-side JavaScript for handling dynamic UI components, API calls to the chatbot backend, and micro-animations.
   - **`static/images/`**: A central location for graphic files (e.g., logo vectors, default avatar icons, decorative backgrounds).
3. **`data/`**
   - **Purpose**: Destined to store raw or preprocessed datasets containing government schemes, eligibility parameters, state codes, or mapping tables (often in JSON, CSV, or SQLite format).
4. **`models/`**
   - **Purpose**: Reserved for containing machine learning or natural language processing codebase components. This includes text classifiers, TF-IDF vectorizers, embedding models, or interface scripts managing LLM API connectors (e.g., OpenAI or Google Gemini clients).
5. **`utils/`**
   - **Purpose**: A repository for utility/helper modules that keep code DRY (Don't Repeat Yourself). Contains data validators, date formatters, geo-location checks, and other helper functions.

---

### Files

1. **`app.py`**
   - **Purpose**: The core driver script. Instantiates the Flask app, configures the runtime environment, lists web routing endpoints, and runs the local development web server.
2. **`requirements.txt`**
   - **Purpose**: Records the explicit versions of Python libraries required for the project (such as `Flask` and `python-dotenv`). Used to replicate environment installations reliably.
3. **`README.md`**
   - **Purpose**: The main portal of documentation. Outlines what the project is, details the folder blueprint, and guides developers on environment installation and startup.
4. **`templates/index.html`**
   - **Purpose**: The central dashboard interface. Provides semantic layout, mounts global metadata tags, and acts as the interactive viewport.
5. **`static/css/style.css`**
   - **Purpose**: Applies a custom dark-mode theme, utilizing modern styling cues like custom font stacks (Outfit & Inter), glow effects, card layouts, and CSS variable styling.
6. **`static/js/script.js`**
   - **Purpose**: Binds click triggers, governs interactive modal behavior, and handles state animations for elements like the custom "Start Chat" confirmation modal.

---

## 💻 Installation & Setup Guide (Windows)

Follow these steps in your PowerShell or Command Prompt to set up a virtual environment, install dependencies, and launch the development web server.

### 1. Open Terminal and Navigate to Project
Ensure your command-line workspace is pointing at the project directory:
```powershell
cd "c:\Users\91970\OneDrive\ai chatbot for government schemes"
```

### 2. Create a Virtual Environment (Recommended)
Isolate your python dependencies for this project:
```powershell
python -m venv venv
```

### 3. Activate the Virtual Environment
```powershell
# In PowerShell:
.\venv\Scripts\Activate.ps1

# In standard Command Prompt (cmd.exe):
.\venv\Scripts\activate.bat
```
*(You will see `(venv)` prepended to your command line prompt indicating it is active).*

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Run the Application
Execute the Flask server:
```powershell
python app.py
```

After running, the application will boot and output the local host URL. Open your web browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**
