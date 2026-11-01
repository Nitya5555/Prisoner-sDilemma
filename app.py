import streamlit as st
import pymysql
import random

st.set_page_config(
    page_title="Cooperate or Defect",
    page_icon="♟",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');

.stApp {
    background: #101012;
    color: #e8e4df;
    font-family: 'Space Grotesk', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1100px;
    padding-top: 3rem;
    padding-bottom: 4rem;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #f1ece6 !important;
    letter-spacing: -1px;
}

h1 {
    font-size: 3.2rem !important;
    font-weight: 700 !important;
}

h2 {
    font-size: 1.8rem !important;
    margin-top: 2rem !important;
}

p, label, .stMarkdown {
    color: #c4bdb8;
}

[data-testid="stCaptionContainer"] {
    color: #8d8580;
    font-family: 'DM Mono', monospace;
    letter-spacing: 1px;
}

[data-testid="stMetric"] {
    background: #1b191c;
    border: 1px solid #383035;
    border-radius: 12px;
    padding: 22px;
}

[data-testid="stMetricLabel"] {
    color: #a49a96 !important;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
}

[data-testid="stMetricValue"] {
    color: #f0e9e3 !important;
    font-size: 2rem;
    font-weight: 700;
}

.stButton > button {
    background: #711f2b;
    color: #fff0ec;
    border: 1px solid #913441;
    border-radius: 8px;
    padding: 0.65rem 1.5rem;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: #963342;
    border-color: #c05260;
    color: white;
    transform: translateY(-2px);
}

.stSelectbox > div > div,
.stRadio > div {
    background: #1b191c;
    border-color: #393238;
    border-radius: 8px;
}

div[data-testid="stAlert"] {
    background: #21191d;
    border: 1px solid #60313b;
    border-radius: 10px;
}

hr {
    border-color: #393035;
    margin-top: 2rem;
    margin-bottom: 2rem;
}

[data-testid="stDataFrame"] {
    border: 1px solid #393035;
    border-radius: 10px;
    overflow: hidden;
}

.stRadio label {
    color: #e8e0dc !important;
}

footer {
    visibility: hidden;
}
html {
    scroll-behavior: smooth;
}

/* Smooth section appearance */
section {
    scroll-margin-top: 80px;
}

/* Fade-in animation */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.stMarkdown,
.stMetric,
.stButton,
.stSelectbox,
.stRadio,
.stDataFrame {
    animation: fadeIn 0.7s ease both;
}

</style>
""", unsafe_allow_html=True)

def connect(database=True):
    settings = {
        "host": "localhost",
        "user": "root",
        "password": "1234",
        "cursorclass": pymysql.cursors.DictCursor
    }

    if database:
        settings["database"] = "cooperate_game"

    return pymysql.connect(**settings)


def setup_database():
    con = connect(False)

    try:
        cur = con.cursor()
        cur.execute("CREATE DATABASE IF NOT EXISTS cooperate_game")
        cur.execute("USE cooperate_game")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS game_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                strategy VARCHAR(50),
                player_choice VARCHAR(20),
                computer_choice VARCHAR(20),
                player_score INT,
                computer_score INT,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        con.commit()
        cur.close()

    finally:
        con.close()


def get_computer_choice(strategy, history):
    n = len(history)

    if strategy == "Always Cooperate":
        return "Cooperate"

    elif strategy == "Always Defect":
        return "Defect"

    elif strategy == "Tit for Tat":
        return "Cooperate" if n == 0 else history[-1]

    elif strategy == "Random":
        return random.choice(["Cooperate", "Defect"])

    elif strategy == "Grudger":
        return "Defect" if "Defect" in history else "Cooperate"

    elif strategy == "Detective":
        opening = ["Cooperate", "Defect", "Cooperate", "Cooperate"]

        if n < 4:
            return opening[n]

        elif "Defect" in history:
            return history[-1]

        return "Defect"
    elif strategy == "Mystery Opponent":
        get_computer_choice(random.choice(["Always Cooperate", "Always Defect", "Tit for Tat", "Random", "Grudger", "Detective"]), history)
        return get_computer_choice(random.choice(["Always Cooperate", "Always Defect", "Tit for Tat", "Random", "Grudger", "Detective"]), history)


def get_scores(player, computer):
    if player == "Cooperate" and computer == "Cooperate":
        return 3, 3

    if player == "Defect" and computer == "Cooperate":
        return 5, 0

    if player == "Cooperate" and computer == "Defect":
        return 0, 5

    return 1, 1


def save_round(strategy, player, computer, ps, cs):
    con = connect()

    try:
        cur = con.cursor()

        cur.execute("""
            INSERT INTO game_history
            (strategy, player_choice, computer_choice,
             player_score, computer_score)
            VALUES (%s, %s, %s, %s, %s)
        """, (strategy, player, computer, ps, cs))

        con.commit()
        cur.close()

    finally:
        con.close()


def load_history():
    con = connect()

    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM game_history ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        return rows

    finally:
        con.close()


try:
    setup_database()

except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()


if "history" not in st.session_state:
    st.session_state.history = []

if "player_total" not in st.session_state:
    st.session_state.player_total = 0

if "computer_total" not in st.session_state:
    st.session_state.computer_total = 0

if "result" not in st.session_state:
    st.session_state.result = None

if "active_strategy" not in st.session_state:
    st.session_state.active_strategy = None


st.title("♟ Cooperate or Defect")
st.caption("A game theory simulation based on the Prisoner's Dilemma")


st.markdown("""
**The rules**

- Both cooperate: 3 points each.
- You defect while the computer cooperates: you get 5 points.
- You cooperate while the computer defects: the computer gets 5 points.
- Both defect: 1 point each.
""")


strategies = {
    "Tit for Tat": "Copies your previous move after cooperating in round one.",
    "Always Cooperate": "Always chooses cooperation.",
    "Always Defect": "Always chooses defection.",
    "Random": "Chooses randomly between cooperation and defection.",
    "Grudger": "Cooperates until you defect, then always defects.",
    "Detective": "Tests you with an opening sequence, then adapts.",
    "Mystery Opponent": "A secret strategy that adapts"
}


st.subheader("Choose your opponent")

strategy = st.selectbox(
    "Computer strategy",
    list(strategies.keys())
)


if st.session_state.active_strategy is None:
    st.session_state.active_strategy = strategy

elif st.session_state.active_strategy != strategy:
    st.session_state.history = []
    st.session_state.player_total = 0
    st.session_state.computer_total = 0
    st.session_state.result = None
    st.session_state.active_strategy = strategy


st.info(strategies[strategy])


st.subheader("Make your move")

player_choice = st.radio(
    "What will you choose?",
    ["Cooperate", "Defect"],
    horizontal=True
)


if st.button("Play Round", type="primary"):

    computer_choice = get_computer_choice(
        strategy,
        st.session_state.history
    )

    ps, cs = get_scores(player_choice, computer_choice)

    try:
        save_round(
            strategy,
            player_choice,
            computer_choice,
            ps,
            cs
        )

        st.session_state.history.append(player_choice)
        st.session_state.player_total += ps
        st.session_state.computer_total += cs

        st.session_state.result = {
            "strategy": strategy,
            "player": player_choice,
            "computer": computer_choice,
            "ps": ps,
            "cs": cs
        }

    except Exception as e:
        st.error(f"Could not save round: {e}")


if st.session_state.result:

    result = st.session_state.result

    st.divider()
    st.subheader("Round Result")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Your points this round", result["ps"])
        st.write("Your move:", result["player"])

    with col2:
        st.metric("Computer points this round", result["cs"])
        st.write("Computer move:", result["computer"])

    st.caption("Opponent strategy: " + result["strategy"])


st.divider()
st.subheader("Scoreboard")

col1, col2, col3 = st.columns(3)

col1.metric("Your total", st.session_state.player_total)
col2.metric("Computer total", st.session_state.computer_total)
col3.metric("Rounds played", len(st.session_state.history))


if st.session_state.player_total > st.session_state.computer_total:
    st.success("You're ahead!")

elif st.session_state.player_total < st.session_state.computer_total:
    st.warning("The computer is ahead!")

else:
    st.info("The scores are tied.")


st.divider()
st.subheader("Database: Match History")


if st.button("View Saved History"):

    try:
        rows = load_history()

        if rows:
            st.dataframe(rows, use_container_width=True)

        else:
            st.info("No saved rounds yet.")

    except Exception as e:
        st.error(f"Could not retrieve history: {e}")


if st.button("Reset Current Match"):

    st.session_state.history = []
    st.session_state.player_total = 0
    st.session_state.computer_total = 0
    st.session_state.result = None

    st.rerun()