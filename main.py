import time
import random
import math
import os
from threading import Thread
import telebot
from telebot import types
from flask import Flask

# Flask web server bot ko active rakhne ke liye
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    # Render/Koyeb automatic PORT asign karte hain
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Aapka Telegram Bot Token
BOT_TOKEN = "8919860591:AAFHKSvSODDmvQL78atOOgulzzLxDnAy3wM"
bot = telebot.TeleBot(BOT_TOKEN)

time_limit = 200  # 200 seconds

user_sessions = {}
leaderboard = []

def get_divisibility_hint(n):
    possible_divisors = [3, 4, 5, 7, 9, 11, 13, 17, 19]
    divisible_by = [str(d) for d in possible_divisors if n % d == 0]
    if divisible_by:
        return f"It is perfectly divisible by: <b>{', '.join(divisible_by)}</b>."
    else:
        return "It is a tough one! Try checking if it's close to a prime number."

def get_advanced_math_hints(n):
    hints = []
    
    # 1. Logarithmic Hint
    log10_val = round(math.log10(n), 3)
    hints.append(f"📐 <b>Log Hint:</b> log₁₀ of this number is approximately <b>{log10_val}</b>.")
    
    # 2. Binomial Hint
    binomial_coeff = (n * (n - 1)) // 2
    hints.append(f"🧮 <b>Binomial Hint:</b> If this number is 'n', the number of ways to choose 2 items from it (nC₂) is <b>{binomial_coeff}</b>.")
    
    # 3. Progression Hint (A.P.)
    ap_sum = (n * (n + 1)) // 2
    hints.append(f"📈 <b>Progression Hint (A.P.):</b> The sum of all natural numbers from 1 up to this number is <b>{ap_sum}</b>.")
    
    # 4. Progression Hint (G.P. or Sequence)
    if n % 2 == 0:
        gp_term = n // 2
        hints.append(f"🧬 <b>Progression Hint (G.P.):</b> This number is the 2nd term of a Geometric Progression whose 1st term is <b>{gp_term}</b> (Common Ratio = 2).")
    else:
        hints.append(f"🧬 <b>Progression Hint (Sequence):</b> 2 times of this number minus 1 makes a perfect even sequence boundary: <b>{(2*n) - 1}</b>.")

    return "\n\n".join(hints)

def update_leaderboard(user_name, time_taken):
    global leaderboard
    leaderboard.append({'name': user_name, 'time_taken': round(time_taken, 2)})
    leaderboard = sorted(leaderboard, key=lambda x: x['time_taken'])[:5]


@bot.message_handler(commands=['players'])
def show_active_players(message):
    chat_id = message.chat.id
    active_muggles = []
    for uid, session in user_sessions.items():
        if session.get('game_active'):
            elapsed_time = time.time() - session['start_time']
            if elapsed_time <= time_limit:
                active_muggles.append({
                    'name': session.get('user_name', 'Unknown'),
                    'rem_time': int(time_limit - elapsed_time)
                })
            else:
                session['game_active'] = False

    if not active_muggles:
        bot.send_message(chat_id, "💤 <b>No one is playing right now.</b>", parse_mode='HTML')
        return

    players_text = "🧙‍♂️ <b>CURRENT ACTIVE MUGGLES IN THE LOOP</b>\n=====================================\n"
    for i, player in enumerate(active_muggles, 1):
        players_text += f"{i}. 👤 <b>{player['name']}</b> — ⏱️ {player['rem_time']}s left\n"
    players_text += "====================================="
    bot.send_message(chat_id, players_text, parse_mode='HTML')


@bot.message_handler(commands=['leaderboard'])
def show_leaderboard(message):
    chat_id = message.chat.id
    if not leaderboard:
        bot.send_message(chat_id, "🏆 <b>Leaderboard is empty!</b>", parse_mode='HTML')
        return
    leaderboard_text = "🏆 <b>TOP 5 FASTEST MUGGLES</b> 🏆\n===============================\n"
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for index, record in enumerate(leaderboard):
        leaderboard_text += f"{medals[index]} <b>{record['name']}</b> — <code>{record['time_taken']}s</code>\n"
    bot.send_message(chat_id, leaderboard_text, parse_mode='HTML')


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    chat_id = message.chat.id
    welcome_text = (
        "<b>+================================+</b>\n"
        "<b>| Welcome to my game, muggle!    |</b>\n"
        "<b>| Enter an integer number        |</b>\n"
        "<b>| and guess what number I've     |</b>\n"
        "<b>| picked for you.                |</b>\n"
        "<b>| So, what is the secret number? |</b>\n"
        "<b>+================================+</b>\n\n"
        "🔥 Now the number can be of <b>ANY digits</b>! Advanced math logic applies.\n"
        "📊 /leaderboard | 🔍 /players"
    )
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    start_btn = types.KeyboardButton("🎮 Start Game")
    markup.add(start_btn)
    bot.send_message(chat_id, welcome_text, parse_mode='HTML', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "🎮 Start Game")
def start_game(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name if message.from_user.first_name else "Muggle"
    
    selected_secret = random.randint(10, 2000)
    
    total_digits = len(str(selected_secret))
    divisibility_info = get_divisibility_hint(selected_secret)
    digit_sum = sum(int(digit) for digit in str(selected_secret))
    
    advanced_hints = get_advanced_math_hints(selected_secret)
    
    user_sessions[chat_id] = {
        'start_time': time.time(),
        'game_active': True,
        'user_name': user_name,
        'secret_number': selected_secret
    }
    
    hints_text = (
        f"⏰ <b>You have {time_limit} seconds to solve this!</b> ⏰\n\n"
        "<b>MATHEMATICAL ANALYSIS OF THE SECRET NUMBER ※</b>\n"
        "====================================\n\n"
        f"💡 <b>Hint 1:</b> It is a <b>{total_digits}-digit</b> number.\n\n"
        f"💡 <b>Hint 2:</b> {divisibility_info}\n\n"
        f"💡 <b>Hint 3:</b> The sum of all digits of this secret number is exactly <b>{digit_sum}</b>.\n\n"
        "----- ADVANCED ANALYSIS BLOCK -----\n\n"
        f"{advanced_hints}\n\n"
        "====================================\n"
        "👇 <b>Calculate fast and enter your guess:</b>"
    )
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(chat_id, hints_text, parse_mode='HTML', reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_guess(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions or not user_sessions[chat_id]['game_active']:
        bot.reply_to(message, "❌ Please click on /start to begin the game!")
        return

    session = user_sessions[chat_id]
    elapsed_time = time.time() - session['start_time']
    
    if elapsed_time > time_limit:
        session['game_active'] = False
        bot.send_message(chat_id, "⏳ <b>Time's up, muggle! Loop locked forever!</b>\nTry again? Click /start", parse_mode='HTML')
        return

    try:
        user_guess = int(message.text)
    except ValueError:
        bot.reply_to(message, "🔢 Please enter a valid integer number.")
        return

    user_name = session['user_name']
    current_secret = session['secret_number']

    if user_guess == current_secret:
        session['game_active'] = False
        update_leaderboard(user_name, elapsed_time)
        win_text = (
            f"🎉 <b>Well done, {user_name}! You cracked it!</b>\n"
            f"🔮 The secret number was indeed <b>{current_secret}</b>.\n"
            f"⏱️ Time taken: <b>{round(elapsed_time, 2)} seconds</b>!\n\n"
            "🏆 Check ranking using /leaderboard"
        )
        bot.send_message(chat_id, win_text, parse_mode='HTML')
    else:
        remaining_time = int(time_limit - elapsed_time)
        direction = "Too Low 👇" if user_guess < current_secret else "Too High 👆"
        
        log10_guide = round(math.log10(current_secret), 3)
        ap_sum_guide = (current_secret * (current_secret + 1)) // 2
        
        loop_text = (
            "👹 <b>Ha ha! You're stuck in my loop.</b>\n"
            f"⚠️ Your guess is <b>{direction}</b>.\n\n"
            "🧠 <b>PRO-MATH SMART DIRECTION:</b>\n"
            f"⚡ Don't waste time! Focus on the <b>Log Hint</b>: <code>10^{log10_guide}</code> se range ka pata lagao, "
            f"ya fir <b>AP Sum</b> (<code>{ap_sum_guide}</code>) ka reverse formula lagakar seconds mein exact value decode karo! 🔥\n\n"
            f"⏰ <b>Remaining Time:</b> {remaining_time} seconds"
        )
        bot.reply_to(message, loop_text, parse_mode='HTML')

if __name__ == "__main__":
    # Flask ko alag thread mein chalayenge taaki polling block na ho
    t = Thread(target=run_flask)
    t.start()
    
    print("Your Advanced Math Bot is running 24/7...")
    bot.infinity_polling()