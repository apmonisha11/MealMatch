import streamlit as st
from datetime import datetime, timedelta
import database as db
import pandas as pd
from groq_ai import ask_food_bridge_ai

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="MealMatch",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700;800&display=swap');

/* =========================================================
   COLOR PALETTE
   ========================================================= */

:root {
    --basil: #1E3D2B;
    --basil-light: #2B5940;

    --marigold: #E8A23A;
    --marigold-dark: #C67E1E;

    --chili: #C1432B;
    --leaf: #4C8C5B;

    --paper: #FFFBF2;

    /* NEW MAIN BACKGROUND — WARM DARK TAN */
    --tan-bg: #D8C3A5;

    /* MAIN TEXT — DARK GREEN */
    --main-text: #1E3D2B;

    --ink: #4A2C20;
    --ink-soft: #6B5845;

    --sidebar-text: #E9C9A0;
    --sidebar-text-soft: #D9B084;
}


/* =========================================================
   TEXT SELECTION / HIGHLIGHT
   ========================================================= */

/* When you drag/select text, DON'T show blue */
::selection {
    background: #1E3D2B !important;
    color: #FFFBF2 !important;
}

::-moz-selection {
    background: #1E3D2B !important;
    color: #FFFBF2 !important;
}


/* =========================================================
   GLOBAL
   ========================================================= */

html,
body,
[class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--main-text);
    font-weight: 600;
    font-size: 17px;
}


/* =========================================================
   MAIN APP BACKGROUND — DARK TAN
   ========================================================= */

.stApp {
    background: #D8C3A5 !important;
}


/* Main content area */
[data-testid="stAppViewContainer"] {
    background: #D8C3A5 !important;
}

[data-testid="stAppViewContainer"] .main {
    background: #D8C3A5 !important;
    color: #1E3D2B !important;
}


/* =========================================================
   MAIN AREA TEXT
   ========================================================= */

[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main span,
[data-testid="stAppViewContainer"] .main label {
    color: #1E3D2B !important;
}


/* Don't force every div's color because Streamlit
   uses divs internally for widgets */
[data-testid="stAppViewContainer"] .main .stMarkdown {
    color: #1E3D2B !important;
}


/* =========================================================
   HEADINGS
   ========================================================= */

h1,
h2,
h3,
h4,
.header-title,
.hero-title {
    font-family: 'Playfair Display', serif;
    font-weight: 800;
    color: #1E3D2B;
}


/* Main headings */
[data-testid="stAppViewContainer"] .main h1,
[data-testid="stAppViewContainer"] .main h2,
[data-testid="stAppViewContainer"] .main h3,
[data-testid="stAppViewContainer"] .main h4 {
    color: #1E3D2B !important;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        var(--basil) 0%,
        var(--basil-light) 100%
    );
}


/* Sidebar text */
[data-testid="stSidebar"] * {
    color: #F5F0E1 !important;
    font-size: 16px !important;
}


/* Sidebar input */
[data-testid="stSidebar"] input {
    color: #4A2C20 !important;
    background-color: var(--paper) !important;
    border-radius: 8px !important;
}


/* Sidebar radio */
[data-testid="stSidebar"] .stRadio > label {
    display: none;
}

[data-testid="stSidebar"] .stRadio [role="radiogroup"] label {
    background: rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 8px 12px;
    margin-bottom: 6px;
    transition: all 0.15s ease;
    border: 1px solid transparent;
}

[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:hover {
    background: rgba(232,162,58,0.18);
    border: 1px solid var(--marigold);
}


/* =========================================================
   HERO BANNER
   ========================================================= */

.hero-banner {
    background: linear-gradient(
        120deg,
        var(--basil) 0%,
        var(--basil-light) 65%,
        #3d6b4a 100%
    );

    border-radius: 18px;
    padding: 26px 30px;
    margin-bottom: 22px;

    box-shadow:
        0 6px 20px rgba(30,61,43,0.18);

    position: relative;
    overflow: hidden;
}


.hero-banner::after {
    content: "";
    position: absolute;

    right: -40px;
    top: -40px;

    width: 140px;
    height: 140px;

    background: radial-gradient(
        circle,
        rgba(232,162,58,0.35) 0%,
        rgba(232,162,58,0) 70%
    );

    border-radius: 50%;
}


.hero-title {
    font-size: 40px;
    font-weight: 800;
    color: #FFFBF2 !important;
    margin: 0;
}


.hero-sub {
    color: #D9E4D3 !important;
    font-size: 17px;
    margin-top: 6px;
}


/* =========================================================
   HERO ICON
   ========================================================= */

@keyframes float-bob {

    0% {
        transform: translateY(0px) rotate(0deg);
    }

    50% {
        transform: translateY(-8px) rotate(-6deg);
    }

    100% {
        transform: translateY(0px) rotate(0deg);
    }

}


.hero-icon {
    display: inline-block;
    font-size: 34px;
    margin-bottom: 6px;
    animation: float-bob 2.6s ease-in-out infinite;
}


/* =========================================================
   FOOD CARD
   ========================================================= */

.food-card {
    background: var(--paper);

    border-radius: 14px;

    padding: 18px 22px;
    margin-bottom: 16px;

    box-shadow:
        0 3px 12px rgba(42,38,32,0.08);

    border-left: 6px solid var(--leaf);

    position: relative;
}


.food-card.nonveg {
    border-left-color: var(--chili);
}


.food-title {
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    font-weight: 700;

    color: #1E3D2B !important;

    margin-bottom: 4px;
    padding-right: 90px;
}


.food-sub {
    color: #6B5845 !important;
    font-size: 15px;
    margin-bottom: 6px;
}


.veg-tag {
    color: var(--leaf) !important;
    font-weight: 700;
    font-size: 15px;
}


.nonveg-tag {
    color: var(--chili) !important;
    font-weight: 700;
    font-size: 15px;
}


/* =========================================================
   STATUS STAMP
   ========================================================= */

.stamp {
    position: absolute;

    top: 18px;
    right: 18px;

    border: 2px dashed;

    border-radius: 8px;

    padding: 4px 10px;

    font-family: 'DM Sans', sans-serif;

    font-weight: 700;

    font-size: 11px;

    letter-spacing: 1.5px;

    text-transform: uppercase;

    transform: rotate(-8deg);
}


.stamp-available {
    color: var(--leaf) !important;
    border-color: var(--leaf);
}


.stamp-claimed {
    color: var(--chili) !important;
    border-color: var(--chili);
}


.stamp-expired {
    color: #9c9587 !important;
    border-color: #9c9587;
}


/* =========================================================
   FRESHNESS BAR
   ========================================================= */

.freshness-label {
    font-size: 14px;

    font-weight: 600;

    color: #6B5845 !important;

    margin-top: 12px;
    margin-bottom: 4px;
}


.freshness-track {
    height: 7px;

    border-radius: 6px;

    background: #E4E0CF;

    overflow: hidden;
}


.freshness-fill {
    height: 100%;

    border-radius: 6px;

    transition: width 0.3s ease;
}


/* =========================================================
   HEADER SUBTEXT
   ========================================================= */

.header-sub {
    color: #6B5845 !important;

    font-size: 17px;

    margin-bottom: 18px;
}


/* =========================================================
   METRICS
   ========================================================= */

/* Metric labels */
[data-testid="stMetricLabel"] {
    color: #1E3D2B !important;
}


/* Metric numbers */
[data-testid="stMetricValue"] {
    color: #1E3D2B !important;
}


/* Metric delta */
[data-testid="stMetricDelta"] {
    color: #1E3D2B !important;
}


/* =========================================================
   BUTTONS
   ========================================================= */

div.stButton > button {

    border-radius: 10px;

    font-weight: 600;

    padding: 7px 20px;

    background: var(--marigold);

    color: #FFFBF2 !important;

    border: none;

    transition:
        transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1),
        box-shadow 0.25s ease,
        background 0.25s ease;

    box-shadow:
        0 2px 6px rgba(0,0,0,0.10);

    position: relative;

    overflow: hidden;
}


div.stButton > button::before {

    content: "";

    position: absolute;

    top: 0;
    left: -75%;

    width: 50%;
    height: 100%;

    background: linear-gradient(
        120deg,
        transparent,
        rgba(255,255,255,0.45),
        transparent
    );

    transform: skewX(-20deg);

    transition: left 0.5s ease;
}


div.stButton > button:hover::before {
    left: 130%;
}


div.stButton > button:hover {

    background: var(--marigold-dark);

    transform:
        translateY(-3px)
        scale(1.02);

    box-shadow:
        0 10px 18px rgba(198,126,30,0.30);

    color: #FFFBF2 !important;
}


div.stButton > button:active {
    transform:
        translateY(-1px)
        scale(0.98);
}


/* =========================================================
   FORM SUBMIT BUTTON
   ========================================================= */

div[data-testid="stFormSubmitButton"] > button {
    background: var(--basil);
    color: #FFFBF2 !important;
}


div[data-testid="stFormSubmitButton"] > button:hover {

    background: var(--basil-light);

    box-shadow:
        0 10px 18px rgba(30,61,43,0.32);

    color: #FFFBF2 !important;
}


/* =========================================================
   INPUTS / SELECTBOXES
   ========================================================= */

[data-testid="stAppViewContainer"] input,
[data-testid="stAppViewContainer"] textarea {

    color: #1E3D2B !important;

    background-color: #FFFBF2 !important;
}


[data-testid="stAppViewContainer"] input::placeholder,
[data-testid="stAppViewContainer"] textarea::placeholder {

    color: #8A7560 !important;

    opacity: 1 !important;
}


/* Selectbox text */
[data-testid="stAppViewContainer"] [data-baseweb="select"] * {
    color: #1E3D2B !important;
}


/* =========================================================
   INFO / SUCCESS / WARNING / ERROR
   ========================================================= */

[data-testid="stAlert"] {
    color: #1E3D2B !important;
}


[data-testid="stAlert"] p {
    color: #1E3D2B !important;
}


/* =========================================================
   DIVIDERS
   ========================================================= */

[data-testid="stAppViewContainer"] hr {
    border-color: rgba(30,61,43,0.20) !important;
}


/* =========================================================
   SIDEBAR CUSTOM HEADER
   ========================================================= */

.sidebar-title {
    font-family: 'Playfair Display', serif;

    font-size: 32px;

    font-weight: 800;

    color: #E9C9A0 !important;
}


.sidebar-description {
    color: #D9B084 !important;

    font-size: 15px;

    margin-top: 4px;
}
/* Make AI answer text readable */
[data-testid="stAlert"] p,
[data-testid="stAlert"] li,
[data-testid="stAlert"] strong,
[data-testid="stAlert"] span {
    color: #1E3D2B !important;
    font-weight: 600 !important;
}

/* ---------- MEALMATCH VISUAL MOTION ---------- */

@keyframes blob-drift {
    0%, 100% {
        transform: translate(0, 0) scale(1);
    }
    50% {
        transform: translate(36px, -28px) scale(1.12);
    }
}

@keyframes card-float {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-10px);
    }
}

@keyframes sparkle {
    0%, 100% {
        opacity: 0.35;
        transform: scale(0.85) rotate(0deg);
    }
    50% {
        opacity: 1;
        transform: scale(1.15) rotate(12deg);
    }
}

/* Soft animated background */
.stApp {
    background:
        radial-gradient(circle at 12% 18%, rgba(232, 162, 58, 0.25), transparent 22%),
        radial-gradient(circle at 88% 24%, rgba(76, 140, 91, 0.22), transparent 24%),
        radial-gradient(circle at 76% 85%, rgba(193, 67, 43, 0.12), transparent 18%),
        #D8C3A5 !important;
}

/* Bigger premium hero */
.hero-banner {
    border: 2px solid rgba(255, 251, 242, 0.18);
    box-shadow:
        0 18px 36px rgba(30, 61, 43, 0.25),
        inset 0 1px 0 rgba(255, 255, 255, 0.16);
}

/* Floating card movement */
.food-card {
    transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.food-card:hover {
    transform: translateY(-7px) scale(1.01);
    box-shadow: 0 15px 30px rgba(74, 44, 32, 0.18);
}

/* Dashboard metric cards */
[data-testid="stMetric"] {
    background: rgba(255, 251, 242, 0.82);
    border: 1px solid rgba(30, 61, 43, 0.12);
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 8px 20px rgba(74, 44, 32, 0.10);
    transition: transform 0.2s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
}

/* Input cards */
[data-testid="stTextInput"],
[data-testid="stSelectbox"],
[data-testid="stNumberInput"] {
    background: rgba(255, 251, 242, 0.16);
    border-radius: 14px;
    padding: 4px 8px;
}

/* Animated small sparkle class for the next step */
.graphic-sparkle {
    display: inline-block;
    animation: sparkle 2.2s ease-in-out infinite;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# HERO BANNER
# ---------------------------------------------------------

def hero_banner(icon, title, subtitle):
    st.markdown(
        f"""<div class="hero-banner">
<div class="hero-icon">{icon}</div>
<div class="hero-title">{title}</div>
<div class="hero-sub">{subtitle}</div>
</div>""",
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# INIT DATABASE
# ---------------------------------------------------------

db.init_db()
db.init_users_table()
db.init_ngos_table()
db.init_map_locations_table()
db.update_expired_listings()


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def format_time_remaining(cooked_time_str, expiry_time_str):

    """Returns (text, urgency, percent_remaining)."""

    cooked = datetime.fromisoformat(cooked_time_str)

    expiry = datetime.fromisoformat(expiry_time_str)

    now = datetime.now()

    diff = expiry - now

    total_window = (
        expiry - cooked
    ).total_seconds() or 1


    if diff.total_seconds() <= 0:

        return "Expired", "expired", 0


    hours = int(
        diff.total_seconds() // 3600
    )

    minutes = int(
        (diff.total_seconds() % 3600) // 60
    )


    if hours > 0:

        text = (
            f"Expires in {hours}h {minutes}m"
        )

    else:

        text = (
            f"Expires in {minutes}m"
        )


    percent = max(
        0,
        min(
            100,
            int(
                (
                    diff.total_seconds()
                    / total_window
                ) * 100
            )
        )
    )


    urgency = (
        "soon"
        if diff.total_seconds() < 3600
        else "ok"
    )


    return text, urgency, percent


# ---------------------------------------------------------
# STATUS BADGE
# ---------------------------------------------------------

def stamp_badge(status):

    css_class = {

        "Available": "stamp-available",

        "Claimed": "stamp-claimed",

        "Picked Up": "stamp-picked-up",

        "Expired": "stamp-expired"

    }.get(
        status,
        "stamp-available"
    )


    return (
        f'<div class="stamp {css_class}">'
        f'{status}'
        f'</div>'
    )


# ---------------------------------------------------------
# FOOD CARD
# ---------------------------------------------------------

def render_food_card(row, show_claim=True, show_delete=False):

    (
        listing_id,
        food_name,
        quantity,
        food_type,
        location,
        donor_name,
        donor_contact,
        cooked_time,
        expiry_time,
        status,
        claimed_by,
        created_at
    ) = row

    time_text, urgency, percent = format_time_remaining(
        cooked_time,
        expiry_time
    )

    if status != "Available":
        fill_color = "#9c9587"
    elif urgency == "soon":
        fill_color = "var(--chili)"
    else:
        fill_color = "var(--leaf)"

    veg_class = "veg-tag" if food_type == "Veg" else "nonveg-tag"

    card_class = (
        "food-card"
        if food_type == "Veg"
        else "food-card nonveg"
    )

    with st.container():

        st.markdown(
            f"""<div class="{card_class}">
{stamp_badge(status)}
<div class="food-title">{food_name}</div>
<div class="food-sub">
📍 {location} &nbsp;|&nbsp; 🍽️ {quantity} &nbsp;|&nbsp;
<span class="{veg_class}">{food_type}</span>
</div>
<div class="food-sub">Donated by: {donor_name}</div>
<div class="freshness-label">⏰ {time_text}</div>
<div class="freshness-track">
<div class="freshness-fill" style="width:{percent}%; background:{fill_color};"></div>
</div>
</div>""",
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([1, 1, 3])

        if show_claim and status == "Available":
            with col1:
                claimer = st.session_state.get(
                    "current_user",
                    "NGO/Volunteer"
                )

                if st.button(
                    "Claim Food",
                    key=f"claim_{listing_id}"
                ):
                    db.claim_listing(
                        listing_id,
                        claimer
                    )

                    st.success(
                        f"You claimed '{food_name}'!"
                    )

                    st.rerun()
        

        if status == "Claimed":
            with col1:
                if st.button(
                    "Confirm Pickup",
                    key=f"pickup_{listing_id}"
                ):
                    db.confirm_pickup(listing_id)
                    st.success(
                        f"Pickup confirmed for '{food_name}'!"
                    )
                    st.toast(
                        "🚚 Pickup confirmed!",
                        icon="✅"
                    )
                    st.rerun()

        if show_delete:
            with col2:
                if st.button(
                    "Delete",
                    key=f"delete_{listing_id}"
                ):
                    db.delete_listing(listing_id)

                    st.warning(
                        f"Deleted '{food_name}'"
                    )

                    st.rerun()
# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# LOGIN / CREATE ACCOUNT SCREEN
# ---------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown("""
    <style>
    @keyframes food-float {
        0%, 100% { transform: translateY(0) rotate(-8deg); }
        50% { transform: translateY(-24px) rotate(8deg); }
    }

    @keyframes glow {
        0%, 100% { opacity: 0.35; transform: scale(1); }
        50% { opacity: 0.75; transform: scale(1.12); }
    }

    .login-food-hero {
        background: linear-gradient(135deg, #1E3D2B, #2B5940);
        border-radius: 24px;
        padding: 42px 25px;
        text-align: center;
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
    }

    .login-food-hero::before {
        content: "";
        position: absolute;
        width: 300px;
        height: 300px;
        background: #E8A23A;
        border-radius: 50%;
        top: -150px;
        right: -100px;
        filter: blur(25px);
        animation: glow 3s ease-in-out infinite;
    }

    .food-animation {
        font-size: 92px;
        display: inline-block;
        animation: food-float 2.5s ease-in-out infinite;
        position: relative;
        z-index: 2;
    }

    .login-title {
        color: #FFFBF2 !important;
        font-family: 'Playfair Display', serif;
        font-size: 42px;
        font-weight: 800;
        margin-top: 10px;
        position: relative;
        z-index: 2;
    }

    .login-subtitle {
        color: #D9E4D3 !important;
        font-size: 17px;
        position: relative;
        z-index: 2;
    }
    </style>

    <div class="login-food-hero">
        <div class="food-animation">🍲</div>
        <div class="login-title">Welcome to MealMatch</div>
        <div class="login-subtitle">
            Share surplus food. Match meals with people who need them.
        </div>
    </div>
    """, unsafe_allow_html=True)

    left, centre, right = st.columns([1, 2, 1])

    with centre:
        sign_in_tab, create_account_tab = st.tabs(
            ["🔐 Sign In", "✨ Create Account"]
        )

        with sign_in_tab:
            login_username = st.text_input(
                "Username",
                key="login_username"
            )

            login_password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )

            if st.button("Sign In to MealMatch", use_container_width=True):
                if db.authenticate_user(login_username, login_password):
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = login_username.strip()
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

        with create_account_tab:
            new_username = st.text_input(
                "Choose a username",
                key="new_username"
            )

            new_password = st.text_input(
                "Choose a password",
                type="password",
                key="new_password"
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                key="confirm_password"
            )

            if st.button("Create My MealMatch Account", use_container_width=True):
                if new_password != confirm_password:
                    st.error("The passwords do not match.")

                else:
                    created, message = db.create_user(
                        new_username,
                        new_password
                    )

                    if created:
                        st.session_state["logged_in"] = True
                        st.session_state["current_user"] = new_username.strip()
                        st.success(message)
                        st.rerun()

                    else:
                        st.error(message)

    st.stop()

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-title">
            🍲 MealMatch
        </div>

        <div class="sidebar-description">
            Connecting surplus food to people
            who need it — in real time.
        </div>
        """,
        unsafe_allow_html=True
    )


    st.divider()


    st.markdown(
        "**Your name** (used for donating / claiming)"
    )


    user_name = st.text_input(
        "Your name",
        value=st.session_state.get(
            "current_user",
            ""
        ),
        label_visibility="collapsed"
    )


    if user_name:

        st.session_state[
            "current_user"
        ] = user_name


    st.divider()


    page = st.radio(
    "Navigate",
    [
        "🏠 Dashboard",
        "🍛 Donate Food",
        "🔍 Browse Listings",
        "📋 My Listings",
        "🤖 AI Assistant",
        "🤝 NGO Profiles",
        "🗺️ Meal Map"
    ]
)


# =========================================================
# PAGE: DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    hero_banner(
        "📊",
        "Dashboard",
        "A quick snapshot of what's happening right now."
    )


    listings = db.get_all_listings()


    total = len(listings)


    available = sum(
        1
        for l in listings
        if l[9] == "Available"
    )


    claimed = sum(
        1
        for l in listings
        if l[9] == "Claimed"
    )


    expired = sum(
        1
        for l in listings
        if l[9] == "Expired"
    )


    c1, c2, c3, c4 = st.columns(4)


    c1.metric(
        "Total Listings",
        total
    )


    c2.metric(
        "Available",
        available
    )


    c3.metric(
        "Claimed",
        claimed
    )


    c4.metric(
        "Expired",
        expired
    )


    st.divider()


    st.markdown(
        "### Recent Listings"
    )


    if listings:

        for row in listings[:5]:

            render_food_card(
                row,
                show_claim=False
            )

    else:

        st.info(
            "No listings yet. Be the first to donate!"
        )


# =========================================================
# PAGE: DONATE FOOD
# =========================================================

elif page == "🍛 Donate Food":

    hero_banner(
        "🍛",
        "Donate Surplus Food",
        "Fill in the details below — takes less than a minute."
    )


    with st.form(
        "donate_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)


        with col1:

            food_name = st.text_input(
                "Food Name (e.g. Rice & Dal, Pizza)"
            )


            quantity = st.text_input(
                "Quantity (e.g. Serves 10, 5 boxes)"
            )


            food_type = st.selectbox(
                "Food Type",
                ["Veg", "Non-Veg"]
            )


        with col2:

            location = st.text_input(
                "Location / Area (e.g. Block A, Sector 12)"
            )


            donor_contact = st.text_input(
                "Contact Number"
            )


            hours_valid = st.slider(
                "Safe to consume for how many hours?",
                1,
                12,
                3
            )


        donor_name = st.session_state.get(
            "current_user",
            ""
        )


        if not donor_name:

            st.warning(
                "Enter your name in the sidebar first."
            )


        submitted = st.form_submit_button(
            "Post Listing",
            use_container_width=True
        )


        if submitted:

            if not (
                food_name
                and quantity
                and location
                and donor_name
            ):

                st.error(
                    "Please fill in all required fields "
                    "(and set your name in the sidebar)."
                )

            else:

                cooked_time = (
                    datetime.now().isoformat()
                )


                expiry_time = (
                    datetime.now()
                    + timedelta(
                        hours=hours_valid
                    )
                ).isoformat()


                db.add_listing(
                    food_name,
                    quantity,
                    food_type,
                    location,
                    donor_name,
                    donor_contact,
                    cooked_time,
                    expiry_time
                )


                st.success(
                    f"'{food_name}' has been listed! "
                    "Nearby NGOs/volunteers can now claim it."
                )


                st.balloons()


# =========================================================
# PAGE: BROWSE LISTINGS
# =========================================================

elif page == "🔍 Browse Listings":

    hero_banner(
        "🔍",
        "Browse Listings",
        "Find surplus food near you and claim it before it expires."
    )


    db.update_expired_listings()



    listings = db.get_all_listings()


    # Filters

    fcol1, fcol2, fcol3 = st.columns(3)


    with fcol1:

        search_term = st.text_input(
            "🔎 Search food (e.g. Pizza)"
        )


    with fcol2:

        status_filter = st.selectbox(
            "Status",
            [
                "All",
                "Available",
                "Claimed",
                "Expired"
            ]
        )


    with fcol3:

        location_filter = st.text_input(
            "📍 Filter by location"
        )


    filtered = listings


    if search_term:

        filtered = [
            l
            for l in filtered
            if search_term.lower()
            in l[1].lower()
        ]


    if status_filter != "All":

        filtered = [
            l
            for l in filtered
            if l[9] == status_filter
        ]


    if location_filter:

        filtered = [
            l
            for l in filtered
            if location_filter.lower()
            in l[4].lower()
        ]


    st.markdown(
        f"**{len(filtered)} listing(s) found**"
    )


    st.divider()


    if filtered:

        for row in filtered:

            render_food_card(
                row,
                show_claim=True
            )

    else:

        st.info(
            "No listings match your filters."
        )


# =========================================================
# PAGE: MY LISTINGS
# =========================================================

elif page == "📋 My Listings":

    hero_banner(
        "📋",
        "My Listings",
        "Manage the food you've donated."
    )


    donor_name = st.session_state.get(
        "current_user",
        ""
    )


    if not donor_name:

        st.warning(
            "Enter your name in the sidebar "
            "to see your listings."
        )

    else:

        db.update_expired_listings()


        my_listings = (
            db.get_listings_by_donor(
                donor_name
            )
        )


        if my_listings:

            for row in my_listings:

             # Database columns:
             # 1 = food_name
             # 9 = status
             # 10 = claimed_by

             food_name = row[1]
             status = row[9]
             claimed_by = row[10]

            if status == "Picked Up":

                st.success(
                    f"🚚 Pickup Confirmed!\n\n"
                    f"Your donation '{food_name}' "
                    f"was picked up by {claimed_by}."
            )

            render_food_card(
                row,
                show_claim=False,
                show_delete=True
           )

        else:

            st.info(
                "You haven't posted any listings yet."
            )
# ---------------------------------------------------------
# PAGE: AI ASSISTANT
# ---------------------------------------------------------
elif page == "🤖 AI Assistant":
    hero_banner(
        "🤖",
        "MealMatch AI Assistant",
        "Ask for safe food donation guidance."
    )

    question = st.text_input(
        "Ask a question",
        placeholder="Example: How can I safely donate rice?"
    )

    if st.button("Ask MealMatch AI"):
        if question:
            with st.spinner("Thinking..."):
                try:
                    answer = ask_food_bridge_ai(question)
                    st.success(answer)

                except Exception as error:
                    st.error(
                        "AI could not respond. Check your internet and API key."
                    )
                    st.caption(str(error))
        else:
            st.warning("Please type a question first.")
# ---------------------------------------------------------
# PAGE: NGO PROFILES
# ---------------------------------------------------------
elif page == "🤝 NGO Profiles":
    hero_banner(
        "🤝",
        "NGO Profiles",
        "Register organisations and connect nearby food donations."
    )

    tab1, tab2 = st.tabs(
        ["➕ Register an NGO", "🏢 Browse NGOs"]
    )

    with tab1:
        st.subheader("Create an NGO Profile")

        with st.form("ngo_form", clear_on_submit=True):
            ngo_name = st.text_input(
                "NGO / Organisation Name *"
            )

            contact_person = st.text_input(
                "Contact Person *"
            )

            phone = st.text_input(
                "Phone Number *"
            )

            location = st.text_input(
                "Location / Area *",
                placeholder="Example: Anna Nagar, Chennai"
            )

            description = st.text_area(
                "About this NGO",
                placeholder="Tell MealMatch what food or support your NGO needs."
            )

            submitted = st.form_submit_button(
                "Create NGO Profile",
                use_container_width=True
            )

        if submitted:
            if not all([
                ngo_name.strip(),
                contact_person.strip(),
                phone.strip(),
                location.strip()
            ]):
                st.error("Please fill in every field marked *.")

            else:
                db.add_ngo(
                    ngo_name.strip(),
                    contact_person.strip(),
                    phone.strip(),
                    location.strip(),
                    description.strip()
                )

                st.success(
                    f"{ngo_name} has been added to MealMatch!"
                )

    with tab2:
        st.subheader("Registered NGOs")

        ngos = db.get_all_ngos()

        if ngos:
            for ngo in ngos:
                st.markdown(f"""
                <div class="food-card">
                    <div class="food-title">🏢 {ngo[1]}</div>
                    <div class="food-sub">
                        👤 Contact: {ngo[2]}
                    </div>
                    <div class="food-sub">
                        📞 {ngo[3]} &nbsp;|&nbsp; 📍 {ngo[4]}
                    </div>
                    <div class="freshness-label">
                        {ngo[5] if ngo[5] else "No description added yet."}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.info(
                "No NGO profiles yet. Create the first one above."
            )
# ---------------------------------------------------------
# PAGE: MEAL MAP
# ---------------------------------------------------------
elif page == "🗺️ Meal Map":
    hero_banner(
        "🗺️",
        "Meal Map",
        "Find nearby food pickup points and NGO locations."
    )

    add_tab, map_tab = st.tabs(
        ["📍 Add a Location", "🗺️ View Meal Map"]
    )

    with add_tab:
        st.subheader("Add a Food or NGO Location")

        st.caption(
            "Tip: Use Google Maps to find the latitude and longitude "
            "of your pickup location."
        )

        with st.form("map_location_form", clear_on_submit=True):
            place_name = st.text_input(
                "Place name *",
                placeholder="Example: Anna Nagar Community Kitchen"
            )

            address = st.text_input(
                "Address / Area *",
                placeholder="Example: Anna Nagar, Chennai"
            )

            location_type = st.selectbox(
                "Location type",
                ["🍲 Food Pickup", "🤝 NGO", "🏪 Restaurant Donor"]
            )

            col1, col2 = st.columns(2)

            with col1:
                latitude = st.number_input(
                    "Latitude *",
                    value=13.0827,
                    format="%.6f"
                )

            with col2:
                longitude = st.number_input(
                    "Longitude *",
                    value=80.2707,
                    format="%.6f"
                )

            save_location = st.form_submit_button(
                "Add Pin to Meal Map",
                use_container_width=True
            )

        if save_location:
            if not place_name.strip() or not address.strip():
                st.error("Please enter the place name and address.")

            else:
                db.add_map_location(
                    place_name.strip(),
                    address.strip(),
                    latitude,
                    longitude,
                    location_type
                )

                st.success("Location added to the Meal Map!")

    with map_tab:
        st.subheader("Nearby Food & NGO Locations")

        locations = db.get_map_locations()

        if locations:
            map_data = pd.DataFrame(
                [
                    {
                        "name": item[1],
                        "address": item[2],
                        "latitude": item[3],
                        "longitude": item[4],
                        "type": item[5]
                    }
                    for item in locations
                ]
            )

            st.map(
                map_data,
                latitude="latitude",
                longitude="longitude",
                zoom=12,
                use_container_width=True
            )

            st.markdown("### Location Details")

            for item in locations:
                st.info(
                    f"{item[5]}  |  **{item[1]}**\n\n"
                    f"📍 {item[2]}"
                )

        else:
            st.info(
                "No map pins yet. Add your first food pickup or NGO location."
            )