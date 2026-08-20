MoneyTrack is a modern, lightweight, cross-platform mobile application for tracking daily expenses and managing budgets. Built with Python, KivyMD, and SQLite3, it features Material Design UI components, fluid slide animations, and an asynchronous multithreaded architecture for a smooth, lag-free experience.
​📸 App Architecture & Screens

[ Main Dashboard ]
       │
       ├──► [ Set Budget Screen ]      (Update monthly expenditure limit)
       ├──► [ Add Expense Screen ]     (Form with dynamic category selector)
       └──► [ Category Items Screen ]  (Filtered transaction history)
                     │
                     └──► [ Transaction Details Screen ] (Inspect & Delete)

✨ Key Features
​⚡ Lag-Free Performance (Multithreading):
All database operations run in background worker threads, preventing UI lockups and frame drops.
​
📊 Live Budget vs. Spent Metrics:
Real-time calculation of overall balance and monthly budget limits.

​📂 Smart Category Management:
Visually distinct cards for categories (Water, Food, Shopping, Electricity, Bills, Travel, and custom entries).

​🔽 Auto-Suggest Category Dropdown:
Quickly choose existing categories or type a new one directly.
​
🕒 Automatic Date & Time Tracking:
Automatically logs exact timestamps (DD Mon, YYYY | hh:mm AM/PM) for every expense.
​
🗑️ Transaction Inspection & Deletion:
View detailed notes for any transaction with instant local record deletion.

​📱 Material UI with Fluid Animations:
Polished with KivyMD widgets, custom ripple cards, and directional slide screen transitions.
​
💾 Local Offline Storage: 
Lightweight SQLite3 engine ensures zero internet dependency and fast local data persistence.


​🛠️ Tech Stack
Component - Technology
Language Python - 3.8+
UI Framework - Kivy & KivyMD (Material Design)
Database - SQLite3
Concurrency - Python threading + Kivy @mainthread dispatchers



🚀 Getting Started

​1. Prerequisites
​Make sure Python 3.8 or higher is installed on your machine.

​2. Clone the Repository
git clone https://github.com/your-username/money-track-kivymd.git
cd money-track-kivymd

3. Set Up Virtual Environment (Recommended)
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate


 4. Install Dependencies
    pip install kivy kivymd

 5. Run the Application
    python money_tracker.py

 🗄️ Database Schema
​The application automatically creates and manages two SQLite tables:

 ​settings Table

Column    Type    Description
id    INTEGER PRIMARY KEY    Settings ID (Fixed: 1)
budget    REAL    Total allocated monthly budget

expenses Table
Column.       Type.        Description
id.       INTEGER PRIMARY KEY AUTOINCREMENT.       Unique Transaction ID
category.       TEXT.       Category name (e.g., Food, Water)
amount.       REAL.       Cost incurred
description.       TEXT.       Custom notes or item details
date.       TEXT.       Formatted timestamp string

📂 Project Structure
money-track-kivymd/
│
├── main.py              # Application core logic, KV templates & DB controller
├── money_track.db       # Auto-generated SQLite database
├── requirements.txt     # Python package dependencies
├── LICENSE              # License configuration
└── README.md            # Comprehensive project documentation

🤝 Contributing
​Fork the project.
​Create your feature branch: git checkout -b feature/AmazingFeature
​Commit your changes: git commit -m 'Add some AmazingFeature'
​Push to the branch: git push origin feature/AmazingFeature
​Open a Pull Request.
​📄 License
​Distributed under the MIT License. See LICENSE for more information.
