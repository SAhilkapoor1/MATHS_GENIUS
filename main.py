import time
import random
import math
import os
import sympy as sp
from PIL import Image
import pytesseract
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

# Render ke Environment Variables se token padhega
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Agar token nahi mila toh error dikhayega
if not BOT_TOKEN:
    raise ValueError("ERROR: BOT_TOKEN Environment Variable nahi mila!")

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


# --- STEP-BY-STEP MATH SOLVER LOGIC (DETERMINISTIC) ---
def process_math_step_by_step(query: str) -> str:
    x, y, z = sp.symbols('x y z')
    query = query.strip()
    steps = []

    # 1. Differentiation Step-by-Step
    if "diff" in query or "d/dx" in query:
        clean_expr = query.replace("diff", "").replace("d/dx", "").strip()
        expr = sp.sympify(clean_expr)
        steps.append(f"<b>Step 1: Given Expression</b>\n<code>f(x) = {expr}</code>")
        
        derivative = sp.diff(expr, x)
        steps.append(f"<b>Step 2: Apply Differentiation Rules wrt (x)</b>\n<code>d/dx [{expr}]</code>")
        steps.append(f"<b>Step 3: Final Computed Result</b>\n<code>{derivative}</code>")

    # 2. Integration Step-by-Step
    elif "integrate" in query or "∫" in query:
        clean_expr = query.replace("integrate", "").replace("∫", "").strip()
        expr = sp.sympify(clean_expr)
        steps.append(f"<b>Step 1: Given Integral Function</b>\n<code>f(x) = {expr}</code>")
        
        integral = sp.integrate(expr, x)
        steps.append(f"<b>Step 2: Apply Integration Formulas</b>\n<code>∫ ({expr}) dx</code>")
        steps.append(f"<b>Step 3: Final Solution</b>\n<code>{integral} + C</code>")

    # 3. Equation Solving Step-by-Step
    elif "=" in query:
        lhs_str, rhs_str = query.split("=")
        lhs = sp.sympify(lhs_str)
        rhs = sp.sympify(rhs_str)
        eq = sp.Eq(lhs, rhs)
        
        steps.append(f"<b>Step 1: Formulate the Equation</b>\n<code>{eq}</code>")
        
        steps.append(f"<b>Step 2: Rearrange Terms to (LHS - RHS = 0)</b>\n<code>{lhs - rhs} = 0</code>")
        
        solutions = sp.solve(eq, x)
        steps.append(f"<b>Step 3: Find Roots/Values for Variable 'x'</b>\n<code>x = {solutions}</code>")

    else:
        expr = sp.sympify(query)
        steps.append(f"<b>Step 1: Original Expression</b>\n<code>{expr}</code>")
        steps.append(f"<b>Step 2: Simplify Term Structures</b>\n<code>{sp.simplify(expr)}</code>")

    return "\n\n".join(steps)


# --- PHOTO HANDLER FEATURE ---
@bot.message_handler(content_types=['photo'])
def handle_photo_math(message):
    chat_id = message.chat.id
    status_msg = bot.send_message(chat_id, "🔍 <b>Scanning image for math equations...</b>", parse_mode='HTML')

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        image_path = f"photo_{chat_id}.jpg"
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image).strip()

        if os.path.exists(image_path):
            os.remove(image_path)

        if not extracted_text:
            bot.edit_message_text("❌ <b>Image text padhne mein dikkat aayi. Please clear photo bhejien.</b>", chat_id, status_msg.message_id, parse_mode='HTML')
            return

        solution_steps = process_math_step_by_step(extracted_text)
        
        output_text = (
            f"📷 <b>Extracted Query:</b> <code>{extracted_text}</code>\n\n"
            f"📑 <b>STEP-BY-STEP SOLUTION:</b>\n"
            f"=====================================\n\n"
            f"{solution_steps}\n\n"
            f"====================================="
        )
        bot.edit_message_text(output_text, chat_id, status_msg.message_id, parse_mode='HTML')

    except Exception as e:
        bot.edit_message_text(f"❌ <b>Processing Error:</b>\n<code>{str(e)}</code>", chat_id, status_msg.message_id, parse_mode='HTML')


# --- ADVANCED MATH SOLVER COMMAND ---
@bot.message_handler(commands=['solve'])
def solve_math_command(message):
    chat_id = message.chat.id
    query = message.text.replace('/solve', '').strip()

    if not query:
        usage_text = (
            "📐 <b>ADVANCED MATH SOLVER (Step-by-Step Engine)</b>\n"
            "=====================================\n"
            "Aap niche diye tarike se question puch sakte hain:\n\n"
            "1️⃣ <b>Text Format:</b>\n"
            "• Equation: <code>/solve x**2 - 5*x + 6 = 0</code>\n"
            "• Derivative: <code>/solve diff x**3 + 4*x</code>\n"
            "• Integral: <code>/solve integrate cos(x)</code>\n\n"
            "2️⃣ <b>Photo Format:</b>\n"
            "• Directly bot ko math question ki **Photo** bhej dein!\n"
            "====================================="
        )
        bot.send_message(chat_id, usage_text, parse_mode='HTML')
        return

    try:
        solution_steps = process_math_step_by_step(query)
        bot.send_message(chat_id, f"📑 <b>STEP-BY-STEP SOLUTION:</b>\n\n{solution_steps}", parse_mode='HTML')
    except Exception as e:
        bot.send_message(chat_id, f"❌ <b>Math Engine Error:</b>\n<code>{str(e)}</code>", parse_mode='HTML')


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


# --- UPDATED WELCOME COMMAND WITH 2ND OPTION ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    chat_id = message.chat.id
    welcome_text = (
        "<b>+================================+</b>\n"
        "<b>|    WELCOME TO MATH & GAME BOT   |</b>\n"
        "<b>+================================+</b>\n\n"
        "Aap is bot se 2 cheezein kar sakte hain:\n\n"
        "🎮 <b>1. Number Guessing Game:</b>\n"
        "Secret integer number guess kijiye math hints ki madad se!\n\n"
        "🧮 <b>2. Math Question Solver (Step-by-Step):</b>\n"
        "Aap advanced math question ka step-by-step solution pa sakte hain:\n"
        "• <b>Text dwara:</b> Write <code>/solve [question]</code>\n"
        "• <b>Photo dwara:</b> Direct question ki photo bhej dein!\n\n"
        "====================================\n"
        "📊 /leaderboard | 🔍 /players | 🧮 /solve"
    )
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    start_btn = types.KeyboardButton("🎮 Start Game")
    solve_btn = types.KeyboardButton("/solve")
    markup.add(start_btn, solve_btn)
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
        bot.reply_to(message, "❌ Please click on /start to begin or /solve to ask a math question!")
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
        bot.reply_to(message, "🔢 Please enter a valid integer number or use /solve for equations.")
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


def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

keep_alive()

print("Your Advanced Math & Game Bot is running 24/7...")

bot.infinity_polling(timeout=10, long_polling_timeout=5)
