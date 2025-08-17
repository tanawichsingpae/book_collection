from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# ---------- สร้างตารางเมื่อรันครั้งแรก ----------
def init_db():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()

    # ตาราง categories
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    # ตาราง books
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER NOT NULL,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')

    # เพิ่มหมวดหมู่เริ่มต้น (ถ้ายังไม่มี)
    c.execute('SELECT COUNT(*) FROM categories')
    if c.fetchone()[0] == 0:
        c.executemany('INSERT INTO categories (name) VALUES (?)',
                      [('เบ็ตเตล็ดหรือความรู้ทั่วไป (Generalities)',), ('ปรัชญา (Philosophy)',), ('ศาสนา (Religion)',)
                       ,('สังคมศาสตร์ (Social sciences)',),('ภาษาศาสตร์ (Language)',),('วิทยาศาสตร์ (Science)',),
                       ('วิทยาศาสตร์ประยุกต์หรือเทคโนโลยี (Technology)',),('ศิลปกรรมและการบันเทิง (Arts and recreation)',),('วรรณคดี (Literature)',)
                       ,('ประวัติศาสตร์และภูมิศาสตร์ (History and geography)',)])
    conn.commit()
    conn.close()

# ---------- แสดงหน้ารายการหนังสือ ----------
@app.route('/')
def index():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute('''
        SELECT books.id, books.title, books.author, books.year, categories.name
        FROM books
        LEFT JOIN categories ON books.category_id = categories.id
    ''')
    books = c.fetchall()
    conn.close()
    return render_template('index.html', books=books)

# ---------- เพิ่มหนังสือ ----------
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute('SELECT * FROM categories')
    categories = c.fetchall()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = request.form['year']
        category_id = request.form['category_id']

        c.execute('INSERT INTO books (title, author, year, category_id) VALUES (?, ?, ?, ?)',
                  (title, author, year, category_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('add_book.html', categories=categories)

# ---------- แก้ไขหนังสือ ----------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()

    # ดึงข้อมูลหมวดหมู่
    c.execute('SELECT * FROM categories')
    categories = c.fetchall()

    # ดึงข้อมูลหนังสือ
    c.execute('SELECT * FROM books WHERE id=?', (id,))
    book = c.fetchone()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = request.form['year']
        category_id = request.form['category_id']

        c.execute('''
            UPDATE books
            SET title=?, author=?, year=?, category_id=?
            WHERE id=?
        ''', (title, author, year, category_id, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit_book.html', book=book, categories=categories)

# ---------- ลบหนังสือ ----------
@app.route('/delete/<int:id>')
def delete_book(id):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute('DELETE FROM books WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
