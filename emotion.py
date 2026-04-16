import streamlit as st
from datetime import datetime
import cv2
from deepface import DeepFace
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector

 # ---------------- DATABASE ----------------
db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="roots",
        database="student_app"
    )
cursor = db.cursor()

# -------- CONFIG --------
st.set_page_config(page_title="Emotion Aware Student Assisstant", layout="wide")

# -------- GEMINI SETUP --------
genai.configure(api_key="AIzaSyCnUvIv_cqXFwmgDBDXuYA_L4i3KrZrT2Q")
model = genai.GenerativeModel("gemini-3-flash-preview")

def get_suggestions(mood):
    try:
        prompt = f"Give 3 short helpful suggestions for a student feeling {mood}"
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Could not fetch suggestion."

# -------- CSS --------
st.markdown("""
<style>

/* -------- BACKGROUND -------- */
.stApp {
    background: linear-gradient(135deg, #fef6fb, #eff6ff);
    font-family: 'Segoe UI';
    color: #1e293b;
}

/* -------- SIDEBAR -------- */
section[data-testid="stSidebar"] {
    background: #fff7ed;
    padding: 20px 10px;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton>button {
    background: transparent;
    color: #1e293b;
    border-radius: 12px;
    padding: 10px;
    font-weight: 500;
}

/* Hover */
section[data-testid="stSidebar"] .stButton>button:hover {
    background: #fde68a;
}

/* Active */
.active-btn {
    background: linear-gradient(135deg, #fbcfe8, #bfdbfe);
    border-radius: 12px;
    padding: 10px;
    font-weight: 600;
}

/* -------- INPUTS -------- */
.stTextInput input {
    background: #fef9ff;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    color: #1e293b;
}


/* ===== STREAMLIT DROPDOWN FULL FIX ===== */

/* Selected box */
div[data-baseweb="select"] * {
    color: #000000 !important;
}

/* Dropdown menu container (IMPORTANT) */
div[role="listbox"] {
    background: #ffffff !important;
    color: #000000 !important;
    border-radius: 10px !important;
}

/* Each option */
div[role="option"] {
    color: #000000 !important;
    background: #ffffff !important;
    font-weight: 500 !important;
}

/* Hover */
div[role="option"]:hover {
    background: #dbeafe !important;
    color: #000000 !important;
}

/* Selected option */
div[aria-selected="true"] {
    background: #bfdbfe !important;
    color: #000000 !important;
}

/* -------- BUTTONS -------- */
.stButton>button {
    background: linear-gradient(135deg, #bfdbfe, #fbcfe8);
    color: #1e293b;
    border-radius: 12px;
    height: 45px;
    font-weight: 600;
}

/* Hover button */
.stButton>button:hover {
    background: linear-gradient(135deg, #93c5fd, #f9a8d4);
}

/* -------- CARDS -------- */
.card {
    background: #ffffff;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}

/* -------- TEXT -------- */
h1, h2, h3 {
    color: #0f172a !important;
}

p, label, span {
    color: #334155 !important;
}

/* -------- METRICS -------- */
[data-testid="stMetric"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 15px;
    border: 1px solid #e2e8f0;
}

/* -------- ALERTS -------- */
.stSuccess {
    background: #dcfce7 !important;
    color: #166534 !important;
}

.stError {
    background: #fee2e2 !important;
    color: #991b1b !important;
}

.stInfo {
    background: #e0f2fe !important;
    color: #075985 !important;
}
/* ===== SELECTBOX FULL FIX ===== */

/* Main box */
div[data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 2px solid #cbd5f5 !important;
    border-radius: 12px !important;
    color: #111827 !important;   /* DARK TEXT */
    font-weight: 600;
}

/* Selected text */
div[data-baseweb="select"] span {
    color: #111827 !important;   /* DARK */
}

/* Dropdown popup container */
div[role="listbox"] {
    background: #ffffff !important;
    border-radius: 12px !important;
    padding: 5px;
}

/* Each option */
div[role="option"] {
    color: #111827 !important;   /* DARK TEXT FIX */
    font-weight: 500;
}

/* Hover */
div[role="option"]:hover {
    background: #e0f2fe !important;  /* light blue pastel */
    color: #000000 !important;
}

/* Selected option */
div[aria-selected="true"] {
    background: #bae6fd !important;
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)
# -------- SESSION --------
if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "completed" not in st.session_state:
    st.session_state.completed = 0

if "mood" not in st.session_state:
    st.session_state.mood = None

if "mood_history" not in st.session_state:
    st.session_state.mood_history = []

# -------- SIDEBAR --------
st.sidebar.title("Student Assisstant 👩🏻‍🎓")

menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Study Planner",
    "Focus Timer",
    "Journal",
    "Analytics"
])

# -------- GREETING --------
hour = datetime.now().hour
greeting = "Good morning ☀️" if hour < 12 else "Good afternoon 🌤" if hour < 18 else "Good evening 🌙"

# -------- DASHBOARD --------
if menu == "Dashboard":

    st.title(greeting)
    st.subheader("How are you feeling today?")

    col1, col2 = st.columns(2)

    # -------- CAMERA --------
    with col1:
        if st.button("📷 Open Camera"):
            cap = cv2.VideoCapture(0)

            ret, frame = cap.read()
            cap.release()

            if ret:
                try:
                    result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                    mood = result[0]['dominant_emotion']

                    st.session_state.mood = mood
                    st.session_state.mood_history.append(mood)
                    cursor.execute(
                        "INSERT INTO emotions (emotion) VALUES (%s)",
                    (mood,)
                    )
                    db.commit()
                    st.success(f"Detected: {mood}")

                except:
                    st.error("Face not detected properly")

    # -------- MANUAL --------
    with col2:
        mood = st.selectbox("Select mood",
            ["happy", "sad", "stressed", "tired", "confused", "neutral"]
        )

        if st.button("Save Mood"):
            st.session_state.mood = mood
            st.session_state.mood_history.append(mood)
            cursor.execute(
                "INSERT INTO emotions (emotion) VALUES (%s)",
            (mood,)
            )
            db.commit()
            st.success(f"Saved: {mood}")

    # -------- GEMINI SUGGESTIONS --------
    if st.session_state.mood:
        st.info(get_suggestions(st.session_state.mood))

    # -------- METRICS --------
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status='Completed'")
    completed = cursor.fetchone()[0]
    

    col1, col2 = st.columns(2)
    col1.metric("Tasks Done", f"{completed}/{total}")
    # -------- STREAK CALCULATION --------
    from datetime import date, timedelta

    cursor.execute("""
    SELECT DATE(created_at)
    FROM tasks
    WHERE status='Completed'
    ORDER BY created_at DESC
""")

    dates = cursor.fetchall()

    completed_dates = [row[0] for row in dates]

    # remove duplicates
    completed_dates = list(set(completed_dates))
    completed_dates.sort(reverse=True)

    streak = 0
    today = date.today()
    current_day = today

    for d in completed_dates:
        if d == current_day:
            streak += 1
            current_day = current_day - timedelta(days=1)
        else:
            break
    
    col2.metric("Streak🔥",f"{streak} days")
    

# -------- STUDY PLANNER --------
elif menu == "Study Planner":
    import mysql.connector
    from datetime import datetime

    st.title("📚 Study Planner")
    st.markdown("Manage tasks with smart reminders 🔔")

    # ---------------- CUSTOM UI ----------------
    st.markdown("""
    <style>
    .task-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
        box-shadow: 0px 3px 8px rgba(0,0,0,0.1);
    }
    .pending {
        border-left: 6px solid #4CAF50;
    }
    .due-soon {
        border-left: 6px solid #FFA500;
    }
    .overdue {
        border-left: 6px solid #FF4B4B;
    }
    .completed {
        text-decoration: line-through;
        color: gray;
    }
    </style>
    """, unsafe_allow_html=True)

   

    # ---------------- ADD TASK ----------------
    st.markdown("### ➕ Add Task")

    col1, col2 = st.columns(2)

    with col1:
        task = st.text_input("Task", placeholder="Study Python")

    with col2:
        due = st.datetime_input("Reminder Time")

    if st.button("➕ Add Task"):
        if task:
            cursor.execute(
                "INSERT INTO tasks (task, status, reminder_time) VALUES (%s, %s, %s)",
                (task, "Pending", due)
            )
            db.commit()
            st.success("Task added with reminder 🔔")
            st.rerun()
        else:
            st.warning("Please enter a task")

    # ---------------- VIEW TASKS ----------------
    st.markdown("### 📋 Your Tasks")

    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    now = datetime.now()

    for t in tasks:
        task_id, task_name, reminder_time, status, created_at = t

        # ---------------- STATUS LOGIC ----------------
        card_class = "pending"
        alert_msg = ""

        if status == "Completed":
            card_class = "completed"

        elif reminder_time <= now:
            card_class = "overdue"
            alert_msg = "⚠️ Overdue!"

        elif (reminder_time- now).total_seconds() < 300:
            card_class = "due-soon"
            alert_msg = "🔔 Due Soon!"

        # ---------------- TASK CARD ----------------
        col1, col2, col3 = st.columns([6,1,1])

        with col1:
            st.markdown(f"""
            <div class="task-card {card_class}">
                <b>📌 {task_name}</b><br>
                ⏰ {reminder_time}<br>
                <span>{alert_msg}</span>
            </div>
            """, unsafe_allow_html=True)

        # ---------------- COMPLETE BUTTON ----------------
        with col2:
            if status != "Completed":
                if st.button("✔️", key=f"done{task_id}"):
                    cursor.execute(
                        "UPDATE tasks SET status='Completed' WHERE id=%s",
                        (task_id,)
                    )
                    db.commit()
                    st.rerun()

        # ---------------- DELETE BUTTON ----------------
        with col3:
            if st.button("🗑️", key=f"del{task_id}"):
                cursor.execute(
                    "DELETE FROM tasks WHERE id=%s",
                    (task_id,)
                )
                db.commit()
                st.rerun()

    
       

# -------- ANALYTICS --------
elif menu == "Analytics":

    st.title("📊 Analytics")

    # Mood chart (FROM DATABASE)

    cursor.execute("SELECT mood FROM moods")
    data = cursor.fetchall()

    if data:
        moods = [row[0] for row in data]

        df = pd.DataFrame(moods, columns=["Mood"])
        mood_counts = df["Mood"].value_counts()

        st.subheader("Mood Distribution")

        fig, ax = plt.subplots(figsize=(5,3))
        ax.bar(mood_counts.index, mood_counts.values)
        ax.set_title("Mood Distribution")

        st.pyplot(fig)
    else:
        df = pd.DataFrame(st.session_state.mood_history, columns=["Mood"])
        mood_counts = df["Mood"].value_counts()

        st.subheader("Mood Distribution")

        fig, ax = plt.subplots(figsize=(5,3))
        ax.bar(mood_counts.index, mood_counts.values)
        ax.set_title("Mood Distribution")

        st.pyplot(fig)

    # Task progress
    total = len(st.session_state.tasks)
    completed = st.session_state.completed

    if total > 0:
        st.subheader("Task Completion")
        st.progress(completed / total)

# -------- focus timer --------
elif menu == "Focus Timer":
    import time
    import streamlit as st

    # ---------- UI DESIGN ----------
    st.markdown("""
        <style>
        body {
            background: linear-gradient(120deg, #ff9a9e, #fad0c4, #fbc2eb, #a6c1ee);
        }

        .title {
            text-align: center;
            font-size: 42px;
            font-weight: bold;
            color: black;
        }

        .timer-card {
            text-align: center;
            padding: 45px;
            border-radius: 25px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
            margin-top: 30px;
        }

        .time-text {
            font-size: 75px;
            font-weight: bold;
            color: white;
        }

        .quote {
            text-align: center;
            font-size: 16px;
            color: black;
            margin-top: 10px;
        }

        /* 🔥 BIG BUTTON STYLE */
        div.stButton > button {
            width: 100%;
            height: 70px;
            font-size: 22px;
            font-weight: bold;
            border-radius: 15px;
            transition: 0.3s ease;
        }

        div.stButton > button:hover {
            transform: scale(1.05);
        }
        </style>
    """, unsafe_allow_html=True)

    # ---------- TITLE ----------
    st.markdown('<div class="title">🌈 Focus Mode Activated</div>', unsafe_allow_html=True)

    # ---------- SESSION ----------
    if "running" not in st.session_state:
        st.session_state.running = False
    if "time_left" not in st.session_state:
        st.session_state.time_left = 1500  # 25 min

    # ---------- TIMER ----------
    minutes = st.session_state.time_left // 60
    seconds = st.session_state.time_left % 60

    st.markdown(f"""
        <div class="timer-card">
            <div class="time-text">{minutes:02d}:{seconds:02d}</div>
        </div>
        <div class="quote">✨ Stay focused. Your future is built now.</div>
    """, unsafe_allow_html=True)

    # ---------- SPACE ----------
    st.markdown("<div style='margin-top:100px;'></div>", unsafe_allow_html=True)

    # ---------- BUTTONS (BIG) ----------
    col1, col2, col3 = st.columns(3)

    start = col1.button("🚀 START")
    pause = col2.button("⏸ PAUSE")
    reset = col3.button("🔄 RESET")

    # ---------- ACTIONS ----------
    if start:
        st.session_state.running = True

    if pause:
        st.session_state.running = False

    if reset:
        st.session_state.time_left = 1500
        st.session_state.running = False

    # ---------- TIMER RUN ----------
    if st.session_state.running:
        time.sleep(1)
        st.session_state.time_left -= 1

        if st.session_state.time_left <= 0:
            st.success("🎉 Session Completed! Take a break 💖")
            st.balloons()
            st.session_state.running = False

        st.rerun()
#---------journal-------
elif menu == "Journal":
    st.subheader("📝 Write your Journal")

    content = st.text_area("Write your thoughts...")

    save = st.button("💾 Save Entry")
    if save:
        if content != "":
            cursor.execute(
            "INSERT INTO journal_entries (content) VALUES (%s)",
            (content,)
        )
            db.commit()
            st.success("Journal saved successfully ✅")
        else:
            st.warning("Please write something before saving")
    