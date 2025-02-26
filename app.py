from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import random
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Flask-Login sozlamalari
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Foydalanuvchi ma'lumotlari
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Ma'lumotlarni saqlash uchun fayllar
USERS_FILE = 'data/users.txt'
WORDS_FILE = 'data/words.txt'

# Fayllarni tekshirish va yaratish
if not os.path.exists('data'):
    os.makedirs('data')
if not os.path.exists(USERS_FILE):
    open(USERS_FILE, 'w').close()
if not os.path.exists(WORDS_FILE):
    open(WORDS_FILE, 'w').close()

# Foydalanuvchi ro'yxatdan o'tkazish
def register_user(username, password):
    # Foydalanuvchi nomi allaqachon mavjudligini tekshirish
    with open(USERS_FILE, 'r') as f:
        for line in f:
            existing_username = line.strip().split(':')[0]
            if existing_username == username:
                return False  # Agar foydalanuvchi nomi allaqachon mavjud bo'lsa

    # Yangi foydalanuvchi qo'shish
    with open(USERS_FILE, 'a') as f:
        f.write(f"{username}:{password}\n")
    return True  # Foydalanuvchi muvaffaqiyatli qo'shildi

# Foydalanuvchini tekshirish
def check_user(username, password):
    with open(USERS_FILE, 'r') as f:
        for line in f:
            u, p = line.strip().split(':')
            if u == username and p == password:
                if username == "admin" and password == "admin1234":  # Admin tekshiruvi
                    return "admin"  # Admin sifatida kirish
                return True  # Oddiy foydalanuvchi sifatida kirish
    return False  # Kirish muvaffaqiyatsiz

# So'z qo'shish
def add_word(user_id, japanese_word, uzbek_word):
    with open(WORDS_FILE, 'a') as f:
        f.write(f"{user_id}:{japanese_word}:{uzbek_word}\n")

# Foydalanuvchining so'zlarini olish
def get_user_words(user_id):
    words = []
    with open(WORDS_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split(':')
            if len(parts) == 3:  # user_id:japanese_word:uzbek_word
                uid, jp, uz = parts
                if uid == user_id:
                    words.append((jp, uz))
    return words

# Barcha foydalanuvchilarni olish
def get_all_users():
    users = []
    with open(USERS_FILE, 'r') as f:
        for line in f:
            username, password = line.strip().split(':')
            users.append({"username": username, "password": password})
    return users

# Barcha so'zlarni olish
def get_all_words():
    words = []
    with open(WORDS_FILE, 'r') as f:
        for line in f:
            user_id, japanese_word, uzbek_word = line.strip().split(':')
            words.append({"user_id": user_id, "japanese_word": japanese_word, "uzbek_word": uzbek_word})
    return words

# Tasodifiy so'zni olish
def get_random_word(user_id):
    words = get_user_words(user_id)
    if words:
        return random.choice(words)
    return None

# Yaponcha so'zning o'zbekcha tarjimasini olish
def get_uzbek_translation(user_id, japanese_word):
    with open(WORDS_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split(':')
            if len(parts) == 3:  # user_id:japanese_word:uzbek_word
                uid, jp, uz = parts
                if uid == user_id and jp == japanese_word:
                    return uz
    return None

# So'zni tahrirlash
def edit_word(user_id, old_japanese_word, new_japanese_word, new_uzbek_word):
    with open(WORDS_FILE, 'r') as f:
        lines = f.readlines()

    with open(WORDS_FILE, 'w') as f:
        for line in lines:
            uid, jp, uz = line.strip().split(':')
            if uid == user_id and jp == old_japanese_word:
                f.write(f"{uid}:{new_japanese_word}:{new_uzbek_word}\n")
            else:
                f.write(line)

# So'zni o'chirish
def delete_word(user_id, japanese_word):
    with open(WORDS_FILE, 'r') as f:
        lines = f.readlines()

    with open(WORDS_FILE, 'w') as f:
        for line in lines:
            uid, jp, uz = line.strip().split(':')
            if uid != user_id or jp != japanese_word:
                f.write(line)

# Foydalanuvchi parolini o'zgartirish
def edit_user_password(username, new_password):
    with open(USERS_FILE, 'r') as f:
        lines = f.readlines()

    with open(USERS_FILE, 'w') as f:
        for line in lines:
            u, p = line.strip().split(':')
            if u == username:
                f.write(f"{u}:{new_password}\n")
            else:
                f.write(line)

# Foydalanuvchini o'chirish
def delete_user(username):
    with open(USERS_FILE, 'r') as f:
        lines = f.readlines()

    with open(USERS_FILE, 'w') as f:
        for line in lines:
            u, p = line.strip().split(':')
            if u != username:
                f.write(line)

# Web sahifalar
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = check_user(username, password)
        if user_type == "admin":
            user = User(username)
            login_user(user)
            return redirect(url_for('admin'))
        elif user_type:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login yoki parol noto‘g‘ri!')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if register_user(username, password):
            flash('Ro‘yxatdan muvaffaqiyatli o‘tdingiz!')
            return redirect(url_for('login'))
        else:
            flash('Bu login allaqachon mavjud! Boshqa login tanlang.')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/add_word', methods=['POST'])
@login_required
def add_word_route():
    japanese_word = request.form['japanese_word']
    uzbek_word = request.form['uzbek_word']
    add_word(current_user.id, japanese_word, uzbek_word)
    flash('So‘z muvaffaqiyatli qo‘shildi!')
    return redirect(url_for('index'))

@app.route('/random_word')
@login_required
def random_word():
    word = get_random_word(current_user.id)
    if word:
        return jsonify({"japanese_word": word[0]})
    else:
        return jsonify({"error": "Hozircha so'zlar mavjud emas."})

@app.route('/get_uzbek_translation')
@login_required
def get_uzbek_translation_route():
    japanese_word = request.args.get('japanese_word')
    translation = get_uzbek_translation(current_user.id, japanese_word)
    if translation:
        return jsonify({"translation": translation})
    else:
        return jsonify({"error": "Tarjima topilmadi."})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/get_user_words')
@login_required
def get_user_words_route():
    words = get_user_words(current_user.id)
    return jsonify(words)

@app.route('/admin')
@login_required
def admin():
    if current_user.id == "admin":  # Faqat admin kirganda
        return render_template('admin.html')
    else:
        return redirect(url_for('index'))  # Boshqa foydalanuvchilar uchun

@app.route('/get_all_users')
@login_required
def get_all_users_route():
    users = get_all_users()
    return jsonify(users)

@app.route('/get_all_words')
@login_required
def get_all_words_route():
    words = get_all_words()
    return jsonify(words)

@app.route('/get_words_by_user/<username>')
@login_required
def get_words_by_user(username):
    words = get_all_words()
    filtered_words = [word for word in words if word["user_id"] == username]
    return jsonify(filtered_words)

@app.route('/edit_user_password', methods=['POST'])
@login_required
def edit_user_password_route():
    username = request.form['username']
    new_password = request.form['new_password']
    edit_user_password(username, new_password)
    return jsonify({"success": True})

@app.route('/delete_user', methods=['POST'])
@login_required
def delete_user_route():
    username = request.form['username']
    delete_user(username)
    return jsonify({"success": True})

@app.route('/edit_word', methods=['POST'])
@login_required
def edit_word_route():
    old_japanese_word = request.form['old_japanese_word']
    new_japanese_word = request.form['new_japanese_word']
    new_uzbek_word = request.form['new_uzbek_word']
    edit_word(current_user.id, old_japanese_word, new_japanese_word, new_uzbek_word)
    return jsonify({"success": True})

@app.route('/delete_word', methods=['POST'])
@login_required
def delete_word_route():
    japanese_word = request.form['japanese_word']
    delete_word(current_user.id, japanese_word)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)