# Schedule Checker for Concurrency Control

This repository provides a comprehensive tool for verifying the correctness of transaction schedules in database systems under various concurrency control criteria. Implemented in Python and Flask, the tool checks schedules for properties such as serializability (both view and conflict), recoverability, rigorousness, and compliance with two-phase locking (2PL) protocols, including strict and strong strict 2PL. Using D3.js, the tool also generates visual precedence graphs to illustrate dependencies in transaction schedules. This utility aids in maintaining ACID properties in concurrent database systems by ensuring data consistency and integrity across interleaved transactions.

# 🏆 Our team:
```
Francesco Sudoso, matricola: 1808353

Andrea Panceri, matricola: 1884749
```

## 🛰️ How to run in local enviroment:

```
git clone https://github.com/Awenega/Schedule-Checker-for-Concurrency-Control.git
cd Schedule-Checker-for-Concurrency-Control/flask/

In the terminal write:

pip install flask
python app.py
```

## 🛰️ Debug Mode:

if want active flask debug mode add in flask folder .DEBUG_MODE_ON empty file, otherwise delete it.

## 📖 Report

### [Click here to see the report](https://drive.google.com/file/d/1iMp9yERiNgKdTXjQED4f3yBOYOjN4mNH/view?usp=drive_link)

## 📖 Final Product

### [Click here to use the webapp](https://transaction-checker-sie6.onrender.com/)
