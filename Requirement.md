# OMR-Based Exam Evaluation System  (EvalSnap)


## 1. Project Overview

### Purpose

The purpose of this project is to digitize and automate the evaluation
of OMR-based exams using a mobile application.
It helps academies, coaching institutes, and teachers quickly scan
answer sheets, calculate scores, and manage exam results online.
This system reduces manual checking, saves time, and minimizes human
error.

------------------------------------------------------------------------

## 2. Problem Statement

Currently, many academies:

-   Check OMR sheets manually
-   Spend hours calculating results
-   Maintain results in Excel or paper format
-   Lack centralized digital records

This project solves these problems by providing:

-   Automated OMR scanning
-   Instant score calculation
-   Centralized result storage
-   Easy access to exam analytics

------------------------------------------------------------------------

## 3. How the System Works (High-Level Flow)

1.  Teacher logs into the mobile application
2.  Teacher designs OMR sheet
3.  Teacher adds students
4.  Teacher scans the OMR sheet using mobile camera
5.  System automatically detects marked answers
6.  Score is calculated instantly
7.  Result is saved and uploaded to the server
8.  Teacher can view results and analytics anytime

------------------------------------------------------------------------

## 4. System Architecture (Simple Explanation)

The system follows a mobile + server architecture:

-   **Mobile App:** Used for scanning OMR sheets and viewing results
-   **Backend Server:** Handles authentication, data storage, and
    analytics
-   **Database:** Stores exams, students, and results

OMR processing is done on the mobile device, while result management is
handled online.

------------------------------------------------------------------------

## 5. Features of the Project

### 5.1 User Authentication

-   Secure login for teachers/admins
-   Role-based access

### 5.2 Exam Management

-   Create exams
-   Define answer keys
-   Manage multiple exams per academy

### 5.3 OMR Sheet Scanning

-   Scan OMR sheets using mobile camera
-   Automatic detection of marked answers
-   Works even in low internet conditions

### 5.4 Automatic Result Calculation

-   Instant score generation
-   Eliminates manual checking
-   Reduces evaluation errors

### 5.5 Result Management

-   Store student results digitally
-   View results exam-wise or student-wise
-   Secure cloud storage

### 5.6 Analytics & Reports

-   Average score per exam
-   Highest and lowest marks
-   Performance overview for teachers

------------------------------------------------------------------------

## 6. Application Pages / Screens

### Mobile Application Screens

1.  **Login Screen**
    -   Teacher/Admin login
2.  **Dashboard**
    -   Quick access to main features
3.  **Exam List Page**
    -   View all available exams
4.  **Add Student Page**
    -   Add students manually and in bulk to generate student IDs
5.  **OMR Scan Page**
    -   Camera screen for scanning answer sheets
6.  **Processing Screen**
    -   Shows evaluation progress
7.  **Result Page**
    -   Displays student score and answer summary
8.  **Analytics Page**
    -   Exam performance statistics
9.  **Settings Page**
    -   Profile and logout options

------------------------------------------------------------------------

## 7. Technology Stack Used

### 7.1 Frontend (Mobile Application)

-   **React Native**
    -   Cross-platform mobile framework
    -   Supports Android and iOS

### 7.2 Image Processing

-   **OpenCV**
    -   Used for OMR detection
    -   Runs directly on the mobile device

### 7.3 Backend (Server)

-   **FastAPI (Python)**
    -   High-performance REST API framework
    -   Handles authentication, exams, and results

### 7.4 Database

-   **PostgreSQL**
    -   Stores exam data, students, and results
    -   Reliable and scalable relational database

### 7.5 Security

-   **JWT Authentication**
    -   Secure user sessions
    -   Token-based authentication

------------------------------------------------------------------------

## 8. Future Enhancements

-   Offline-first syncing
-   Advanced AI-based OMR detection
-   Advanced text-based answer detection

------------------------------------------------------------------------

## 9. Conclusion

The OMR Evaluation & Exam Management System is a modern, scalable, and
practical solution for educational institutions.

It demonstrates strong skills in:

-   Mobile application development
-   Backend system design
-   Image processing
-   Database management

This project reflects real-world industry use cases and is suitable for
enterprise-level applications.
