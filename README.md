# React Native App (Expo)

This is a cross-platform mobile application built using React Native with Expo.  
The same codebase works on Android and iOS without platform-specific changes.

---

##  Features

• Single codebase for Android & iOS  
• Fast development with Expo  
• Hot Reload / Fast Refresh  
• Runs on real devices using Expo Go  
• Easy setup and configuration  

---

##  Tech Stack

• React Native  
• Expo  
• FastAPI  
• Python  
• Tailwind CSS  
• PostgreSQL  

---

##  Prerequisites

Make sure you have the following installed:

### 1️⃣ Node.js (LTS Recommended)

Download from:  
https://nodejs.org/

Check installation:

```bash
node -v
npm -v
```

---

### 2️⃣ Expo Go App (On Mobile Device)

Install Expo Go:

• Android → Play Store  
• iOS → App Store  

---

### 3️⃣ Android Setup (Optional but Recommended)

• Android Studio  
• Android SDK  
• USB Debugging enabled  

Check environment:

```bash
adb devices
```

---

##  Project Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/lmsoftwaresolutions/papercheck_omr.git
cd papercheck_omr
```

### 2️⃣ Install Dependencies

```bash
npm install
```

---

## ▶️ Run the Application

Start Expo Development Server:

```bash
npx expo start
```

If you face cache issues:

```bash
npx expo start -c
```

---

##  Run on Android

1. Open Expo Go on Android phone  
2. Scan the QR code  

OR (if emulator running) press:

```bash
r
```

---

##  Run on iOS

1. Open Expo Go on iPhone  
2. Scan QR code  

⚠️ iOS Simulator requires macOS and Xcode.  
On Windows, use real iPhone with Expo Go.

---

##  Stop the Application

Press:

```bash
Ctrl + C
```

---

## 📂 Project Structure

```
your-project/
│
├── assets/
├── screens/
├── navigation/
├── App.js
├── package.json
└── README.md
```

---


## 📄 License

This project is for educational and learning purposes.
