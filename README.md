## LinkedIn Profile Analyzer for Wi-Fi and Network Infrastructure Relevance

This application analyzes LinkedIn profile text and determines whether a person is relevant for selling Wi-Fi or Network Infrastructure solutions. It uses Groq LLM (LLaMA 3.1) to extract insights, assess relevance, and recommend next steps.

The tool is created for sales teams, presales teams, and business development professionals who need a simple interface to evaluate LinkedIn profiles without technical expertise.

The interface is built using Streamlit, and all analysis is automated using AI.

---
Live Link : https://lssyre.streamlit.app/

## 1. Purpose of the Application

This application helps users understand whether a LinkedIn profile belongs to a person who can influence or decide network infrastructure or Wi-Fi purchase decisions. It evaluates designation relevance, responsibilities, decision authority, and provides a clear recommendation.

The system supports two modes:

1. Single Profile Analysis
2. Batch Profile Analysis using a file upload

---

## 2. Key Features

### 2.1 Single Profile Analysis

* Paste any LinkedIn profile text.
* Click one button to analyze.
* Displays relevance score (High, Medium, Low, No).
* Provides a detailed explanation.
* Recommends the correct target persona if the person is not relevant.
* Allows downloading results in CSV or TSV formats.

### 2.2 Batch Analysis

* Upload a simple text file containing multiple profiles.
* The system automatically processes all profiles.
* Outputs a structured table for all analyzed profiles.
* Downloadable CSV/TSV summary.

### 2.3 AI-Powered Analysis

Uses Groq LLM to:

* Extract information
* Evaluate designation relevance
* Provide structured JSON output
* Ensure consistent scoring based on defined business rules

---

## 3. Technology Used

| Component | Usage                          |
| --------- | ------------------------------ |
| Streamlit | User interface                 |
| Groq LLM  | AI-based analysis              |
| Python    | Core logic                     |
| Pandas    | Table formatting and downloads |

---

## 4. Requirements

Before running the application, ensure you have:

1. Python 3.9 or higher
2. Groq API key
3. Installed dependencies
4. A stable internet connection

---

## 5. Installation Steps

Follow the steps below. No technical background needed.

### Step 1: Download or Clone the Project

If you are using Git:

```
git clone https://github.com/kiruba11k/Syntel-Relevance.git
cd Syntel-Relevance
```

Or download the ZIP folder and extract it.

---

### Step 2: Create a Virtual Environment

This keeps all project files separate and clean.

Run:

```
python -m venv venv
```

Activate it:

Windows:

```
venv\Scripts\activate
```

Mac/Linux:

```
source venv/bin/activate
```

---

### Step 3: Install Dependencies

Run the following command:

```
pip install -r requirements.txt
```

This installs Streamlit, Groq SDK, Pandas, and other dependencies.

---

### Step 4: Add Your API Key

Create a folder named `.streamlit` in the project directory.

Inside it, create a file called:

```
secrets.toml
```

Add your Groq API key inside the file:

```
GROQ_API_KEY = "your_groq_api_key_here"
```

Save the file.

This allows the application to securely use the Groq model without exposing your key.

---

### Step 5: Run the Application

Start the app with:

```
streamlit run app.py
```

Your browser will automatically open the application dashboard.

---

## 6. How to Use the Application

### 6.1 Single Profile Mode

1. Go to the "Single Profile Analysis" tab.
2. Paste the full LinkedIn profile text in the text box.
3. Click "Analyze Profile".
4. Wait while the AI processes the information.
5. View the detailed structured table.
6. Download results as CSV or TSV if needed.

---

### 6.2 Batch Profile Mode

1. Create a text file containing multiple LinkedIn profiles.
2. Separate each profile using this line:

   ```
   ===PROFILE===
   ```
3. Upload the file in the "Batch Profile Analysis" tab.
4. Click "Analyze All Profiles".
5. View the combined results table.
6. Download CSV/TSV output.

---

## 7. Understanding the Output

The AI outputs structured fields:

### 1. Designation Relevance

Possible values:

* High
* Medium
* Low
* No

### 2. How Relevant

Explanation of why the profile is scored as High/Medium/Low/No.

### 3. Target Persona

If relevance is Low or No, the AI suggests the correct target (example: CIO, Head of IT Infrastructure).

### 4. Next Step

Guidance for the sales team such as:

* Ask for an introduction
* Reach out to IT head directly
* Ignore this contact

---

## 8. Troubleshooting

### Problem: “Groq client failed to initialize”

Solution:
Check if your API key is correctly placed in `.streamlit/secrets.toml`.

### Problem: Application does not start

Ensure:

* Virtual environment is activated
* All dependencies are installed
* Python version is correct

### Problem: JSON error or incomplete output

Groq may occasionally return text outside JSON format.
The application uses a fallback method to prevent crashes.

---

## 9. Folder Structure

```
project/
│
├── app.py
├── requirements.txt
├── README.md
└── .streamlit/
    └── secrets.toml
```

---

## 10. Safety Notes

* API keys must never be shared publicly.
* The application does not save any data permanently.
* Uploaded files are used only during the session.

---

## 11. Intended Users

This tool is designed for:

* Sales teams
* Business development teams
* Pre-sales consultants
* Account managers
* Anyone evaluating LinkedIn profiles for Wi-Fi/Network infra outreach


---
