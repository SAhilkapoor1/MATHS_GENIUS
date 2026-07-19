# MATHS_GENIUS
# 🧙‍♂️ The Muggle Loop: Advanced Math Guessing Game Bot

An advanced, interactive Telegram game bot built with Python. Players are trapped in a mathematical loop and must use real-time complex math hints (Logarithms, Arithmetic Progressions, Geometric Progressions, and Combinatorics) to deduce a dynamic secret number before the countdown expires.

---

## 🔥 Key Features

- **🎮 Dynamic Secret Numbers:** Generates dynamic, multi-digit integer puzzles ranging from simple to highly advanced scales.
- **🧠 Real-Time Math Telemetry:** Provides live, advanced mathematical direction based on the user's guess:
  - **Logarithmic Anchors:** Helps players instantly narrow down the number range using $\log_{10}$ boundaries.
  - **Progression Vectors:** Generates complex Arithmetic (A.P.) and Geometric (G.P.) sequences derived from the secret number.
  - **Combinatorial Logic:** Factors in combinations ($nC_2$) and exact digit sums.
- **⏳ Residual Heat Web Server:** Integrated with a background Flask frame to handle automated pings, keeping the bot active 24/7 on free cloud hosting instances (Render, Koyeb).
- **📊 Live Tracking & Competitions:** 
  - `/players` — Monitors active users currently stuck in the loop with live countdown timers.
  - `/leaderboard` — Displays the Top 5 fastest players with millisecond precision.

---

## 🛠️ Tech Stack & Architecture

- **Language:** Python 3.x
- **Framework:** `pyTelegramBotAPI` (Telebot)
- **Web Server:** Flask (for 24/7 Keep-Alive polling)
- **Concurrency:** Multi-threading (`threading.Thread`) for simultaneous server responsiveness and bot polling.

---

## 🚀 Quick Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
   cd YOUR_REPO_NAME
