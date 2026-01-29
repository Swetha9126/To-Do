from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = "todo.db"


def get_db():
    return sqlite3.connect(DB_NAME)


def init_db():
    db = get_db()
    com = db.cursor()
    com.execute("""
        CREATE TABLE IF NOT EXISTS lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    com.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            list_id INTEGER,
            task TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (list_id) REFERENCES lists(id)
        )
    """)
    db.commit()
    db.close()


@app.route('/')
@app.route('/index')
def index():
    db = get_db()
    com = db.cursor()
    com.execute("SELECT * FROM lists")
    lists = com.fetchall()
    list_data = []
    total_tasks = 0
    completed_tasks = 0
    for lst in lists:
        com.execute(
            "SELECT * FROM tasks WHERE list_id = ?", (lst[0],)
        )
        tasks = com.fetchall()

        total_tasks = total_tasks + len(tasks)
        completed_tasks = completed_tasks + len([t for t in tasks if t[3] == "Completed"])

        list_data.append({
            "id": lst[0],
            "name": lst[1],
            "tasks": tasks,
            "task_count": len(tasks)
        })

    db.close()

    return render_template(
        "index.html",
        lists=list_data,
        lists_count=len(lists),
        total_tasks=total_tasks,
        completed_tasks=completed_tasks
    )


@app.route('/viewlist/<list_id>')
def viewlist(list_id):
    db = get_db()
    com = db.cursor()

    com.execute("SELECT * FROM lists WHERE id = ?", (list_id,))
    lists = com.fetchall()
    list_data = []
    total_tasks = 0
    completed_tasks = 0

    com.execute(
        "SELECT * FROM tasks WHERE list_id = ?", (list_id,)
    )
    tasks = com.fetchall()

    total_tasks = total_tasks + len(tasks)
    completed_tasks = completed_tasks + len([t for t in tasks if t[3] == "Completed"])

    list_data.append({
        "id": list_id,
        "name": lists[0][1],
        "tasks": tasks,
        "task_count": len(tasks)
    })

    db.close()

    return render_template(
        "viewlist.html",
        lists=list_data,
        lists_count=len(lists),
        total_tasks=total_tasks,
        completed_tasks=completed_tasks
    )


@app.route('/add_list', methods=['POST'])
def add_list():
    name = request.form['list_name']
    db = get_db()
    com = db.cursor()
    com.execute("SELECT * FROM lists WHERE name = ?", (name,))
    exists = com.fetchone()
    if not exists:
        com.execute("INSERT INTO lists (name) VALUES (?)", (name,))
        db.commit()
    db.close()
    return redirect(url_for('index'))


@app.route('/delete_list/<int:list_id>')
def delete_list(list_id):
    db = get_db()
    com = db.cursor()
    com.execute("DELETE FROM tasks WHERE list_id = ?", (list_id,))
    com.execute("DELETE FROM lists WHERE id = ?", (list_id,))
    db.commit()
    db.close()

    return redirect(url_for('index'))


@app.route('/add_task/<list_id>', methods=['POST'])
def add_task(list_id):
    task = request.form['task']
    db = get_db()
    com = db.cursor()
    com.execute(
        "INSERT INTO tasks (list_id, task, status) VALUES (?, ?, ?)",
        (list_id, task, "Pending")
    )
    db.commit()
    db.close()
    return redirect(url_for('viewlist', list_id=list_id))


@app.route('/complete/<task_id>/<list_id>')
def complete(task_id, list_id):
    db = get_db()
    com = db.cursor()
    com.execute(
        "UPDATE tasks SET status='Completed' WHERE id=?",
        (task_id,)
    )
    db.commit()
    db.close()
    return redirect(url_for('viewlist', list_id=list_id))

@app.route('/completed/<task_id>/<list_id>')
def completed(task_id, list_id):
    db = get_db()
    com = db.cursor()
    com.execute(
        "UPDATE tasks SET status='Pending' WHERE id=?",
        (task_id,)
    )
    db.commit()
    db.close()
    return redirect(url_for('viewlist', list_id=list_id))


@app.route('/delete/<task_id>/<list_id>')
def delete(task_id, list_id):
    db = get_db()
    com = db.cursor()
    com.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    db.commit()
    db.close()
    return redirect(url_for('viewlist', list_id=list_id))


@app.route('/update/<int:list_id>', methods=['PUT'])
def update(list_id):
    name = request.form['name']
    db = get_db()
    com = db.cursor()
    com.execute("UPDATE lists SET name = ? WHERE id = ?",(name, list_id))
    db.commit()
    db.close()
    return redirect(url_for('index'))


@app.route('/search_list', methods=['POST'])
def search_list():
    name = request.form['search_list']
    db = get_db()
    com = db.cursor()
    com.execute("SELECT * FROM lists WHERE name LIKE ?", (name+'%',))
    lists = com.fetchall()
    list_data = []
    total_tasks = 0
    completed_tasks = 0
    for lst in lists:
        com.execute(
            "SELECT * FROM tasks WHERE list_id = ?", (lst[0],)
        )
        tasks = com.fetchall()

        total_tasks = total_tasks + len(tasks)
        completed_tasks = completed_tasks + len([t for t in tasks if t[3] == "Completed"])

        list_data.append({
            "id": lst[0],
            "name": lst[1],
            "tasks": tasks,
            "task_count": len(tasks)
        })

    db.close()

    return render_template(
        "index.html",
        lists=list_data,
        lists_count=len(lists),
        total_tasks=total_tasks,
        completed_tasks=completed_tasks
    )


    


@app.route('/api/index')
def api_index():
    db = get_db()
    com = db.cursor()

    com.execute("SELECT * FROM lists")
    lists = com.fetchall()

    list_data = []

    for lst in lists:
        com.execute("SELECT * FROM tasks WHERE list_id = ?", (lst[0],))
        tasks = com.fetchall()

        list_data.append({
            "id": lst[0],
            "name": lst[1],
            "tasks": [
                {
                    "id": t[0],
                    "task": t[2],
                    "status": t[3]
                } for t in tasks
            ]
        })

    db.close()
    return jsonify(list_data)


@app.route('/api/viewlist/<list_id>')
def api_viewlist(list_id):
    db = get_db()
    com = db.cursor()

    com.execute("SELECT * FROM lists WHERE id = ?", (list_id,))
    lists = com.fetchall()

    list_data = []
    total_tasks = 0
    completed_tasks = 0

    com.execute(
        "SELECT * FROM tasks WHERE list_id = ?", (list_id,)
    )
    tasks = com.fetchall()

    total_tasks = total_tasks + len(tasks)
    completed_tasks = completed_tasks + len([t for t in tasks if t[3] == "Completed"])

    list_data.append({
        "id": list_id,
        "name": lists[0][1],
        "tasks": tasks,
        "task_count": len(tasks)
    })

    db.close()
    return jsonify(list_data)


@app.route('/api/add_list', methods=['POST'])
def api_add_list():
    data = request.get_json()
    name = data["name"]

    db = get_db()
    com = db.cursor()
    com.execute("SELECT * FROM lists WHERE name = ?", (name,))
    exists = com.fetchone()

    if not exists:
        com.execute("INSERT INTO lists (name) VALUES (?)", (name,))
        db.commit()

    db.close()
    return jsonify({"message": "List added", "list_name": name})


@app.route('/api/delete_list/<int:list_id>', methods=['DELETE'])
def api_delete_list(list_id):
    db = get_db()
    com = db.cursor()
    com.execute("DELETE FROM tasks WHERE list_id = ?", (list_id,))
    com.execute("DELETE FROM lists WHERE id = ?", (list_id,))
    db.commit()
    db.close()

    return jsonify({"message": "List deleted", "list_id": list_id})


@app.route('/api/add_task/<list_id>', methods=['POST'])
def api_add_task(list_id):
    data = request.get_json()
    task = data["task"]

    db = get_db()
    com = db.cursor()
    com.execute(
        "INSERT INTO tasks (list_id, task, status) VALUES (?, ?, ?)",
        (list_id, task, "Pending")
    )
    db.commit()
    db.close()

    return jsonify({
        "message": "Task added",
        "list_id": list_id,
        "task": task
    })


@app.route('/api/delete/<task_id>/<list_id>', methods=['DELETE'])
def api_delete(task_id, list_id):
    db = get_db()
    com = db.cursor()
    com.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    db.commit()
    db.close()
    return jsonify({"message": "Task deleted", "task_name": task_id, "list_id": list_id})


@app.route('/api/update/<int:list_id>', methods=['PUT'])
def api_update(list_id):
    data = request.get_json()
    name = data["name"]

    db = get_db()
    com = db.cursor()
    com.execute(
        "UPDATE lists SET name = ? WHERE id = ?",
        (name, list_id)
    )
    db.commit()
    db.close()

    return jsonify({
        "success": True,
        "message": "List name updated"
    })


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
