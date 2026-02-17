



# React Native App (Expo) - PaperCheck OMR

This is a cross-platform mobile application built using **React Native** with **Expo**. The same codebase works on Android and iOS without platform-specific changes.

---

## 🚀 Features
* **Single codebase** for Android & iOS
* **Fast development** with Expo
* **Hot Reload** / Fast Refresh
* **Runs on real devices** using Expo Go
* **Easy setup** and configuration

## 🛠 Tech Stack
* **Frontend:** React Native, Expo, Tailwind CSS
* **Backend:** FastAPI, Python
* **Database:** PostgreSQL

---

## 📋 Prerequisites
Make sure you have the following installed:

### 1. Node.js (LTS Recommended)
* [Download from nodejs.org](https://nodejs.org/)
* **Check installation:**
    ```bash
    node -v
    npm -v
    ```

### 2. Expo Go App (On Mobile Device)
Install **Expo Go** from your mobile app store:
* **Android:** Play Store
* **iOS:** App Store

### 3. Android Setup (Optional)
* Android Studio & Android SDK
* USB Debugging enabled
* **Check environment:**
    ```bash
    adb devices
    ```

---

## ⚙️ Project Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/lmsoftwaresolutions/papercheck_omr.git]
cd papercheck_omr

```

### 2. Install Dependencies

```bash
npm install

```

---

## ▶️ Running the Application

### Start Expo Development Server

```bash
npx expo start

```

> [!TIP]
> If you face cache issues, use `npx expo start -c`

### Run on Android

1. Open **Expo Go** on your Android phone.
2. Scan the **QR code** in the terminal.
3. *OR* (if emulator is running) press `a`.

### Run on iOS

1. Open **Expo Go** on your iPhone.
2. Scan the **QR code**.
3. **Note:** iOS Simulator requires macOS and Xcode. On Windows, use a real iPhone with Expo Go.

---

## 🖥 Backend Setup (FastAPI)

### 1. Navigate to Backend Folder

```bash
cd backend

```

### 2. Create Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate

```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate

```

### 3. Create Environment File

Create a file named `.env`. You can copy from the example:

**macOS / Linux:**

```bash
cp .env.example .env

```

**Windows:**

```bash
copy .env.example .env

```

### 4. Install Backend Dependencies

```bash
# If requirements.txt exists:
pip install -r requirements.txt



```

### 5. Run FastAPI Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

```

---

## 🛑 Stop Services

* **Stop Backend/Frontend:** Press `Ctrl + C` in the terminal.

---

## 📂 Project Structure

```text
papercheck_omr/
├── assets/             # Images and static files
├── screens/            # UI Components
├── navigation/         # App Routing
├── App.js              # Entry Point
├── package.json        # Node Dependencies
├── backend/
│   ├── app/            # Logic & Models
│   ├── main.py         # Entry Point
│   ├── requirements.txt
│   └── .env            # Environment Variables
└── README.md           # Documentation

```

## 📄 generate_strong_secret_here properly


Run this command in terminal:

```

python -c "import secrets; print(secrets.token_hex(32))"

```
