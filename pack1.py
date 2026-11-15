import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
import base64

# ডার্ক থিম কনফিগ
os.makedirs(".streamlit", exist_ok=True)
os.makedirs("product_images", exist_ok=True)
config_path = ".streamlit/config.toml"
if not os.path.exists(config_path):
    with open(config_path, "w", encoding="utf-8") as f:
        f.write('[theme]\nbase="dark"\nprimaryColor="#ec4899"\n')
        f.write('backgroundColor="#090d16"\n')
        f.write('secondaryBackgroundColor="#0f172a"\n')
        f.write('textColor="#f8fafc"\n')

st.set_page_config(
    page_title="packxebec | Custom Packaging Studio & ERP",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "packxebec_erp_v3.db"

# ==========================================================
# ১. SQLITE DATABASE ENGINE
# ==========================================================
def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            date TEXT,
            customer_name TEXT,
            phone TEXT,
            box_type TEXT,
            material TEXT,
            dimensions TEXT,
            finish TEXT,
            printing TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_price REAL,
            paid_amount REAL,
            due_amount REAL,
            prod_cost REAL,
            profit REAL,
            notes TEXT,
            status TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            code TEXT,
            img_path TEXT,
            box_type TEXT,
            material TEXT,
            finish TEXT,
            printing TEXT,
            length REAL,
            width REAL,
            height REAL,
            clicks INTEGER DEFAULT 12
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS custom_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            option_name TEXT UNIQUE,
            rate REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS site_stats (
            stat_key TEXT PRIMARY KEY,
            stat_val TEXT
        )
    """)

    default_stats = [
        ("today_visitors", "31"),
        ("page_views", "47"),
        ("live_now", "1"),
        ("order_clicks", "203"),
        ("open_quotations", "2"),
        ("seo_title", "packxebec | Custom Packaging & Box Manufacturer in BD"),
        ("seo_keywords", "300 GSM Swedish Board, Custom Box Dhaka, Packaging Printing"),
        ("seo_desc", "Order custom printed packaging boxes with instant quotation."),
        ("factory_phone", "01XXXXXXXXX")
    ]
    c.executemany(
        "INSERT OR IGNORE INTO site_stats VALUES (?, ?)",
        default_stats
    )

    c.execute("SELECT COUNT(*) FROM custom_options")
    if c.fetchone()[0] == 0:
        default_opts = [
            ("box_type", "Tuck End Box (সুইডিশ বোর্ড স্ট্যান্ডার্ড)", 0.0),
            ("box_type", "Mailer Box (ই-কমার্স প্রিমিয়াম লক)", 0.0),
            ("box_type", "Food / Sweet Packaging Box", 0.0),
            ("box_type", "Rigid Luxury Gift Box", 0.0),
            ("material", "300 GSM Swedish Board (Best Seller)", 0.045),
            ("material", "350 GSM Art Card", 0.052),
            ("material", "280 GSM Duplex Board", 0.032),
            ("material", "E-Flute Corrugated Board", 0.060),
            ("finish", "Glossy Lamination (গ্লসি ফিনিশ)", 0.015),
            ("finish", "Matte Lamination (ম্যাট ফিনিশ)", 0.018),
            ("finish", "Spot UV + Matte Coating", 0.025),
            ("finish", "No Lamination", 0.0),
            ("printing", "4 Color (CMYK Full Print)", 2500.0),
            ("printing", "Single Color Brand Print", 1200.0),
            ("printing", "No Print (Plain Box)", 500.0),
        ]
        c.executemany(
            "INSERT OR IGNORE INTO custom_options "
            "(category, option_name, rate) VALUES (?, ?, ?)",
            default_opts
        )

    c.execute("SELECT COUNT(*) FROM catalog")
    if c.fetchone()[0] == 0:
        u1 = "https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=600"
        u2 = "https://images.unsplash.com/photo-1607083206869-4c7672e72a8a?w=600"
        u3 = "https://images.unsplash.com/photo-1543083477-4f785aeafaa9?w=600"
        u4 = "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=600"
        u5 = "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=600"
        u6 = "https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=600"
        u7 = "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600"
        u8 = "https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=600"

        default_catalog = [
            ("১২ x ৯ x ৪ কাস্টম ডাই-কাট বক্স", "PX-101 • E-Flute Kraft", u1,
             "Mailer Box (ই-কমার্স প্রিমিয়াম লক)", "E-Flute Corrugated Board",
             "No Lamination", "Single Color Brand Print", 12.0, 9.0, 4.0, 58),
            ("300 GSM Swedish Tuck Box", "PX-102 • Custom Brand Print", u2,
             "Tuck End Box (সুইডিশ বোর্ড স্ট্যান্ডার্ড)", "300 GSM Swedish Board (Best Seller)",
             "Glossy Lamination (গ্লসি ফিনিশ)", "4 Color (CMYK Full Print)", 4.5, 4.5, 5.5, 44),
            ("Silver Foil Metallic Mailer", "PX-103 • Silver Art Card", u3,
             "Mailer Box (ই-কমার্স প্রিমিয়াম লক)", "350 GSM Art Card",
             "Glossy Lamination (গ্লসি ফিনিশ)", "4 Color (CMYK Full Print)", 7.0, 5.0, 2.5, 31),
            ("Silver Roll-End Tuck Box", "PX-104 • Premium Metallic", u4,
             "Food / Sweet Packaging Box", "300 GSM Swedish Board (Best Seller)",
             "Glossy Lamination (গ্লসি ফিনিশ)", "Single Color Brand Print", 6.0, 6.0, 3.5, 19),
            ("Eco Die-Cut Delivery Box", "PX-105 • Duplex / Kraft", u5,
             "Food / Sweet Packaging Box", "280 GSM Duplex Board",
             "No Lamination", "Single Color Brand Print", 9.0, 7.0, 3.0, 15),
            ("Pharma & Bottle Tuck Box", "PX-106 • 300 GSM Swedish", u6,
             "Tuck End Box (সুইডিশ বোর্ড স্ট্যান্ডার্ড)", "300 GSM Swedish Board (Best Seller)",
             "Glossy Lamination (গ্লসি ফিনিশ)", "4 Color (CMYK Full Print)", 3.5, 3.5, 7.0, 12),
            ("Metallic Cosmetics Box", "PX-107 • Spot UV Finish", u7,
             "Tuck End Box (সুইডিশ বোর্ড স্ট্যান্ডার্ড)", "350 GSM Art Card",
             "Spot UV + Matte Coating", "4 Color (CMYK Full Print)", 5.0, 4.0, 3.0, 14),
            ("Luxury Black Rigid Drawer", "PX-108 • Velvet Matte Rigid", u8,
             "Rigid Luxury Gift Box", "350 GSM Art Card",
             "Matte Lamination (ম্যাট ফিনিশ)", "Single Color Brand Print", 8.5, 4.5, 2.0, 10)
        ]
        c.executemany("""
            INSERT INTO catalog (
                title, code, img_path, box_type, material,
                finish, printing, length, width, height, clicks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, default_catalog)

    c.execute("SELECT COUNT(*) FROM orders")
    if c.fetchone()[0] == 0:
        demo_orders = [
            ("PX-1101", "2026-11-10 11:20", "Aarong Artisan", "01711000001",
             "Tuck End Box (সুইডিশ বোর্ড স্ট্যান্ডার্ড)", "300 GSM Swedish Board (Best Seller)",
             "12x9x4", "Glossy Lamination (গ্লসি ফিনিশ)", "4 Color (CMYK Full Print)",
             6000, 12.5, 75000.0, 60000.0, 15000.0, 54000.0, 21000.0,
             "Urgent Glossy Batch", "Delivered"),
            ("PX-1102", "2026-11-12 15:40", "Glow Cosmetics BD", "01819000002",
             "Mailer Box (ই-কমার্স প্রিমিয়াম লক)", "350 GSM Art Card",
             "7x5x2.5", "Matte Lamination (ম্যাট ফিনিশ)", "4 Color (CMYK Full Print)",
             2000, 16.2, 32400.0, 19700.0, 12700.0, 23500.0, 8900.0,
             "Logo on top flap", "In Printing"),
            ("PX-1103", "2026-11-14 18:10", "BakeHouse Dhaka", "01912000003",
             "Food / Sweet Packaging Box", "300 GSM Swedish Board (Best Seller)",
             "8x8x3", "Glossy Lamination (গ্লসি ফিনিশ)", "Single Color Brand Print",
             500, 14.0, 7000.0, 0.0, 7000.0, 5100.0, 1900.0,
             "Asked for price quote", "Quotation")
        ]
        c.executemany(
            "INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            demo_orders
        )

    conn.commit()
    conn.close()

init_db()

def get_stat(key, default="0"):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT stat_val FROM site_stats WHERE stat_key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default

def set_stat(key, val):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO site_stats VALUES (?, ?)",
        (key, str(val))
    )
    conn.commit()
    conn.close()

def get_options_dict(category):
    conn = get_conn()
    q = "SELECT option_name, rate FROM custom_options WHERE category=?"
    df = pd.read_sql_query(q, conn, params=(category,))
    conn.close()
    return dict(zip(df["option_name"], df["rate"]))

def get_catalog_df():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM catalog ORDER BY id ASC", conn)
    conn.close()
    return df

def get_orders_df():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM orders ORDER BY date DESC", conn)
    conn.close()
    return df

def render_img_src(img_path):
    p = str(img_path)
    if p.startswith("http"):
        return p
    if os.path.exists(p):
        with open(p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            ext = "png" if p.lower().endswith(".png") else "jpeg"
            return f"data:image/{ext};base64,{b64}"
    return "https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=600"

def svg_to_b64(svg_str):
    b64 = base64.b64encode(svg_str.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"

def to_bn_num(val):
    en = "0123456789"
    bn = "০১২৩৪৫৬৭৮৯"
    return str(val).translate(str.maketrans(en, bn))

# ==========================================================
# ২. PACKXEBEC BRAND LOGO
# ==========================================================
DARK_LOGO_PARTS = [
    '<svg viewBox="0 0 500 430" xmlns="http://www.w3.org/2000/svg">',
    '<defs>',
    '<linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">',
    '<stop offset="0%" stop-color="#f43f5e"/>',
    '<stop offset="50%" stop-color="#a855f7"/>',
    '<stop offset="100%" stop-color="#38bdf8"/></linearGradient>',
    '<linearGradient id="g2" x1="100%" y1="0%" x2="0%" y2="100%">',
    '<stop offset="0%" stop-color="#38bdf8"/>',
    '<stop offset="50%" stop-color="#c084fc"/>',
    '<stop offset="100%" stop-color="#f43f5e"/></linearGradient>',
    '</defs><g fill="#f8fafc">',
    '<path d="M 248 25 C 254 25, 258 30, 263 40 L 285 82 ',
    'C 287 87, 285 93, 279 96 L 264 105 C 258 108, 254 103, 252 97 ',
    'C 249 91, 244 93, 244 100 C 244 114, 260 122, 272 115 L 292 102 ',
    'C 297 99, 302 102, 305 108 L 346 188 C 350 197, 344 206, 334 206 ',
    'L 317 206 C 310 206, 306 201, 302 193 L 272 135 L 225 135 ',
    'L 185 215 C 181 223, 174 227, 165 227 L 150 227 ',
    'C 140 227, 135 218, 140 208 L 234 35 C 238 28, 243 25, 248 25 Z"/>',
    '<path fill-rule="evenodd" d="M 248 158 C 256 158, 263 163, 269 173 ',
    'L 302 228 C 309 238, 318 242, 330 242 C 356 242, 382 258, 386 286 ',
    'C 388 300, 381 318, 372 325 L 202 325 C 197 325, 194 321, 193 315 ',
    'L 190 302 C 188 292, 176 290, 172 298 C 169 304, 172 315, 175 322 ',
    'C 177 325, 174 325, 168 325 L 132 325 C 122 325, 113 310, 113 295 ',
    'C 113 274, 128 256, 152 256 L 170 256 C 176 256, 178 263, 175 270 ',
    'L 165 290 L 184 290 L 230 173 C 235 163, 241 158, 248 158 Z ',
    'M 248 196 L 206 288 L 292 288 Z ',
    'M 326 266 L 317 282 L 333 306 L 345 298 Z"/></g>',
    '<text x="52" y="398" font-family="Arial Black, sans-serif" ',
    'font-weight="900" font-size="68" fill="#ffffff" ',
    'letter-spacing="-2">pack</text>',
    '<g transform="translate(234, 348)">',
    '<polygon points="4,0 18,0 48,50 34,50" fill="url(#g1)"/>',
    '<polygon points="48,0 34,0 4,50 18,50" fill="url(#g2)"/>',
    '<polygon points="26,19 31,25 26,31 21,25" fill="#fff"/></g>',
    '<text x="286" y="398" font-family="Arial Black, sans-serif" ',
    'font-weight="900" font-size="68" fill="#ffffff" ',
    'letter-spacing="-2">ebec</text></svg>'
]
LOGO_SRC = svg_to_b64("".join(DARK_LOGO_PARTS))

if "sel_box_type" not in st.session_state:
    st.session_state.sel_box_type = "Tuck End Box (সুইডিশ বোর্ড স্ট্যান্ডার্ড)"
if "sel_material" not in st.session_state:
    st.session_state.sel_material = "300 GSM Swedish Board (Best Seller)"
if "sel_finish" not in st.session_state:
    st.session_state.sel_finish = "Glossy Lamination (গ্লসি ফিনিশ)"
if "sel_printing" not in st.session_state:
    st.session_state.sel_printing = "4 Color (CMYK Full Print)"
if "sel_dims" not in st.session_state:
    st.session_state.sel_dims = (6.0, 4.0, 2.5)
if "active_sample" not in st.session_state:
    st.session_state.active_sample = "300 GSM Swedish Tuck Box"
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ==========================================================
# ৩. DARK SLATE UI CSS
# ==========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #f8fafc;
}
.stApp {
    background: radial-gradient(circle at top right, #1e1b4b 0%, #090d16 45%, #060911 100%);
    color: #f8fafc;
}
header[data-testid="stHeader"] {
    background: rgba(9, 13, 22, 0.75) !important;
    backdrop-filter: blur(10px);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #090d16 100%) !important;
    border-right: 1px solid #1e293b !important;
}
section[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}
h1, h2, h3, h4, h5, label, .stMarkdown p, div[data-testid="stWidgetLabel"] p {
    color: #f8fafc !important;
    font-weight: 600 !important;
}
.brand-title {
    font-size: 2.2rem;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -1px;
    margin: 0;
}
.brand-x {
    background: linear-gradient(135deg, #f472b6 0%, #a78bfa 50%, #60a5fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 900;
}
.dark-glass-card {
    background: linear-gradient(145deg, #0f172a 0%, #131c31 100%);
    color: #ffffff;
    padding: 24px 26px;
    border-radius: 16px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45);
    border: 1px solid #26334d;
    position: relative;
    overflow: hidden;
    margin-bottom: 20px;
}
.dark-glass-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #ec4899, #8b5cf6, #3b82f6);
}
.ov-card {
    background: linear-gradient(145deg, #0f172a 0%, #15203b 100%);
    border: 1px dashed #3b82f6;
    border-radius: 14px;
    padding: 22px;
    min-height: 235px;
    position: relative;
    margin-bottom: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.35);
    transition: all 0.2s ease;
}
.ov-card:hover {
    border-color: #ec4899;
    transform: translateY(-3px);
}
.ov-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.92rem;
    font-weight: 700;
    color: #cbd5e1;
    margin-bottom: 14px;
}
.ov-link { color: #60a5fa; font-size: 0.82rem; font-weight: 600; }
.ov-sub { font-size: 0.8rem; color: #94a3b8; margin-bottom: 4px; }
.ov-big {
    font-size: 2.35rem;
    font-weight: 900;
    background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.15;
    margin: 4px 0 8px 0;
}
.ov-foot { font-size: 0.78rem; color: #94a3b8; margin-top: 8px; line-height: 1.4; }
.live-badge {
    background: rgba(34, 197, 94, 0.14);
    color: #4ade80 !important;
    padding: 5px 13px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    border: 1px solid rgba(74, 222, 128, 0.25);
    display: inline-block;
}
.gradient-num {
    font-size: 2.35rem;
    font-weight: 800;
    background: linear-gradient(90deg, #f472b6, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 4px 0;
}
.spec-pill {
    display: inline-block;
    background: rgba(255, 255, 255, 0.05);
    padding: 6px 12px;
    border-radius: 9px;
    font-size: 0.82rem;
    color: #f1f5f9 !important;
    margin: 4px 5px 4px 0;
    border: 1px solid rgba(255, 255, 255, 0.14);
}
.cat-card {
    background: linear-gradient(145deg, #0f172a 0%, #162038 100%);
    border: 1px solid #26334d;
    border-radius: 15px;
    overflow: hidden;
    transition: all 0.25s ease;
    margin-bottom: 8px;
}
.cat-card:hover {
    transform: translateY(-4px);
    border-color: #a855f7;
}
.cat-img-box {
    background: #0b1120;
    height: 155px;
    width: 100%;
    overflow: hidden;
    border-bottom: 1px solid #1e293b;
}
.cat-img-box img { width: 100%; height: 100%; object-fit: cover; }
.cat-info { padding: 12px 14px; }
.cat-title { font-size: 0.9rem; font-weight: 700; color: #f8fafc !important; margin: 0; }
.cat-sub { font-size: 0.75rem; color: #c084fc !important; font-weight: 600; margin-top: 4px; }

div[data-baseweb="select"] > div,
div[data-baseweb="input"],
div[data-baseweb="base-input"],
div[data-testid="stNumberInputContainer"],
div[data-baseweb="textarea"] {
    background-color: #131c31 !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}
div[data-baseweb="select"] span,
div[data-baseweb="select"] div { color: #ffffff !important; }
div[data-baseweb="popover"],
ul[role="listbox"],
li[role="option"] {
    background-color: #0f172a !important;
    color: #ffffff !important;
}
input[type="text"],
input[type="number"],
input[type="password"],
textarea {
    background-color: #131c31 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 600 !important;
}
div[data-testid="stForm"] {
    background: linear-gradient(145deg, #0f172a 0%, #131c31 100%);
    border: 1px solid #26334d;
    border-radius: 18px;
    padding: 22px;
}
div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(90deg, #2563eb 0%, #7c3aed 50%, #ec4899 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.2rem !important;
    font-weight: 700 !important;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

box_dict = get_options_dict("box_type")
mat_dict = get_options_dict("material")
finish_dict = get_options_dict("finish")
print_dict = get_options_dict("printing")

box_options = list(box_dict.keys())
mat_options = list(mat_dict.keys())
finish_options = list(finish_dict.keys())
print_options = list(print_dict.keys())

# ==========================================================
# SIDEBAR: ডিফল্ট কাস্টমার ভিউ + সিকিউর অ্যাডমিন লগইন
# ==========================================================
with st.sidebar:
    st.markdown(
        f'<div class="dark-glass-card" style="padding:16px 12px; text-align:center; margin-bottom:16px;">'
        f'<img src="{LOGO_SRC}" style="width:155px; height:auto; border-radius:8px;">'
        f'<div style="margin-top:8px;"><span class="live-badge">● Online Ordering Active</span></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div style="background:rgba(255,255,255,0.03); padding:12px; border-radius:12px; border:1px solid rgba(255,255,255,0.08); font-size:0.82rem; margin-bottom:16px;">'
        '<div style="color:#60a5fa; font-weight:700; margin-bottom:4px;">📦 প্যাকজেবেক ফ্যাক্টরি স্ট্যান্ডার্ড</div>'
        '<div style="color:#cbd5e1;">✨ 300 GSM Swedish Board</div>'
        '<div style="color:#cbd5e1;">🎨 4-Color CMYK Offset Print</div>'
        '<div style="color:#cbd5e1;">💎 Glossy / Matte Lamination</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # কাস্টমারদের থেকে লুকানো স্টাফ লগইন সেকশন
    admin_page = None
    with st.expander("🔐 Admin Login (Staff Only)", expanded=st.session_state.admin_logged_in):
        if not st.session_state.admin_logged_in:
            pwd_input = st.text_input("অ্যাডমিন পাসওয়ার্ড দিন:", type="password", placeholder="Password...")
            if st.button("🔑 লগইন করুন"):
                if pwd_input == "admin123":
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("❌ ভুল পাসওয়ার্ড!")
        else:
            st.success("✅ Admin Mode Active")
            if st.button("🚪 লগআউট (Back to Customer View)"):
                st.session_state.admin_logged_in = False
                st.rerun()

    if st.session_state.admin_logged_in:
        st.markdown("<hr style='margin:10px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        portal_mode = st.radio(
            "ভিউ মোড:",
            ["🛒 Customer Studio (ফ্রন্টএন্ড)", "🔐 Admin Backend (ব্যাকএন্ড)"],
            index=1
        )
        if portal_mode == "🔐 Admin Backend (ব্যাকএন্ড)":
            st.markdown(
                "<div style='color:#60a5fa; font-size:0.78rem; font-weight:700; margin:10px 0 4px 0;'>[ ব্যবসা ও ওয়েবসাইট মেনু ]</div>",
                unsafe_allow_html=True
            )
            admin_page = st.radio(
                "ব্যাকএন্ড নেভিগেশন:",
                [
                    "💠 ওভারভিউ",
                    "📑 অর্ডার (Orders)",
                    "👥 কাস্টমার (Customers)",
                    "💳 হিসাব (Accounts & Due)",
                    "📦 প্রোডাক্ট ও ছবি (Products CMS)",
                    "🏷️ ক্যাটাগরি ও রেট (Categories)",
                    "📊 ট্রাফিক (Traffic)",
                    "✨ প্রোডাক্টের আগ্রহ (Interest)",
                    "🔍 সার্চ (Search)",
                    "🌐 এসইও (SEO)",
                    "⚙️ সেটিংস (Settings)"
                ],
                label_visibility="collapsed"
            )
    else:
        portal_mode = "🛒 Customer Studio (ফ্রন্টএন্ড)"

# ==========================================================
# PART A: CUSTOMER STUDIO (ডিফল্ট কাস্টমার ভিউ)
# ==========================================================
if portal_mode == "🛒 Customer Studio (ফ্রন্টএন্ড)":
    st.markdown(
        '<div class="dark-glass-card" style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap;">'
        '<div>'
        '<div style="font-size:0.76rem; color:#94a3b8; letter-spacing:1px;">CUSTOM PACKAGING STUDIO</div>'
        '<div class="brand-title">pack<span class="brand-x">x</span>ebec</div>'
        '<div style="color:#cbd5e1; font-size:0.9rem;">Real Product Showcase, Instant Cost Calculator & Online Order</div>'
        '</div>'
        '<div><span class="live-badge">● 300 GSM Swedish Board Specialist</span></div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("### 🖼️ ১. রিয়েল প্রোডাক্ট স্যাম্পল গ্যালারি (Click to Customize)")
    catalog_df = get_catalog_df()
    catalog_records = catalog_df.to_dict("records")

    for i in range(0, len(catalog_records), 4):
        row_items = catalog_records[i:i+4]
        cols = st.columns(4, gap="medium")
        for idx, item in enumerate(row_items):
            with cols[idx]:
                img_src = render_img_src(item["img_path"])
                st.markdown(
                    f'<div class="cat-card">'
                    f'<div class="cat-img-box"><img src="{img_src}"></div>'
                    f'<div class="cat-info">'
                    f'<p class="cat-title">{item["title"]}</p>'
                    f'<p class="cat-sub">{item["code"]}</p>'
                    f'<div style="margin-top:6px;"><span class="spec-pill" style="font-size:0.72rem; padding:3px 8px;">📏 {item["length"]}"×{item["width"]}"×{item["height"]}"</span></div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
                if st.button("✨ Select & Customize", key=f"cbtn_{item['id']}"):
                    conn = get_conn()
                    conn.execute("UPDATE catalog SET clicks = clicks + 1 WHERE id=?", (item["id"],))
                    conn.commit()
                    conn.close()
                    set_stat("order_clicks", int(get_stat("order_clicks", "203")) + 1)

                    st.session_state.sel_box_type = item["box_type"] if item["box_type"] in box_options else box_options[0]
                    st.session_state.sel_material = item["material"] if item["material"] in mat_options else mat_options[0]
                    st.session_state.sel_finish = item["finish"] if item["finish"] in finish_options else finish_options[0]
                    st.session_state.sel_printing = item["printing"] if item["printing"] in print_options else print_options[0]
                    st.session_state.sel_dims = (float(item["length"]), float(item["width"]), float(item["height"]))
                    st.session_state.active_sample = item["title"]
                    st.rerun()

    st.markdown("<hr style='margin:24px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1.22, 1], gap="large")

    with left_col:
        st.markdown(f"### 🛠️ ২. বক্স কাস্টমাইজার (`{st.session_state.active_sample}`)")
        tab1, tab2 = st.tabs(["📐 বক্সের স্টাইল ও মাপ", "🎨 প্রিন্টিং ও ফিনিশিং"])

        with tab1:
            b_idx = box_options.index(st.session_state.sel_box_type) if st.session_state.sel_box_type in box_options else 0
            m_idx = mat_options.index(st.session_state.sel_material) if st.session_state.sel_material in mat_options else 0
            box_type = st.selectbox("বক্সের ধরন (Box Style)", box_options, index=b_idx)
            material = st.selectbox("ম্যাটেরিয়াল (Board Grade)", mat_options, index=m_idx)
            c1, c2, c3 = st.columns(3)
            length = c1.number_input("দৈর্ঘ্য (Length)", min_value=1.0, max_value=40.0, value=float(st.session_state.sel_dims[0]), step=0.5)
            width = c2.number_input("প্রস্থ (Width)", min_value=1.0, max_value=40.0, value=float(st.session_state.sel_dims[1]), step=0.5)
            height = c3.number_input("উচ্চতা (Height)", min_value=1.0, max_value=40.0, value=float(st.session_state.sel_dims[2]), step=0.5)

        with tab2:
            f_idx = finish_options.index(st.session_state.sel_finish) if st.session_state.sel_finish in finish_options else 0
            p_idx = print_options.index(st.session_state.sel_printing) if st.session_state.sel_printing in print_options else 0
            f_col1, f_col2 = st.columns(2)
            finish = f_col1.selectbox("লেমিনেশন ফিনিশিং", finish_options, index=f_idx)
            printing = f_col2.selectbox("প্রিন্টিং মোড", print_options, index=p_idx)
            quantity = st.slider("📦 অর্ডারের পরিমাণ (Quantity - Pcs)", min_value=100, max_value=20000, value=500, step=100)

        surface_area = 2 * ((length * width) + (length * height) + (width * height)) * 1.25
        board_cost = surface_area * mat_dict.get(material, 0.045)
        lam_cost = surface_area * finish_dict.get(finish, 0.015)
        setup_cost = print_dict.get(printing, 2500.0)
        making_cost = 1.50 + box_dict.get(box_type, 0.0)
        fixed_cost_per_box = setup_cost / quantity

        unit_prod_cost = board_cost + lam_cost + making_cost + fixed_cost_per_box
        margin = 1.35 if quantity < 1000 else (1.25 if quantity < 3000 else 1.18)

        unit_selling_price = round(unit_prod_cost * margin, 2)
        total_selling_price = round(unit_selling_price * quantity, 2)
        total_prod_cost = round(unit_prod_cost * quantity, 2)
        estimated_profit = round(total_selling_price - total_prod_cost, 2)

        st.markdown("#### 📝 ৩. অর্ডার বা কোটেশন সাবমিট করুন")
        with st.form("cust_order_form"):
            fc1, fc2 = st.columns(2)
            cust_name = fc1.text_input("আপনার নাম / ব্র্যান্ডের নাম *")
            cust_phone = fc2.text_input("মোবাইল নম্বর *")
            req_type = st.radio("রিকোয়েস্টের ধরন:", ["অর্ডার কনফার্ম (Order)", "খোলা কোটেশন (Price Quotation Only)"], horizontal=True)
            advance_pay = st.number_input("অ্যাডভান্স পেমেন্ট (যদি থাকে - BDT)", min_value=0.0, value=0.0, step=500.0)
            cust_notes = st.text_area("কাস্টম রিকোয়ারমেন্ট বা ডিজাইন নোট (ঐচ্ছিক)", height=70)
            submit_btn = st.form_submit_button("🚀 সাবমিট করুন")

            if submit_btn:
                if not cust_name.strip() or not cust_phone.strip():
                    st.error("⚠️ অনুগ্রহ করে আপনার নাম এবং মোবাইল নম্বর দিন।")
                else:
                    order_id = f"PX-{datetime.now().strftime('%m%d%H%M%S')}"
                    status_val = "Quotation" if "কোটেশন" in req_type else "Pending"
                    due_val = max(0.0, total_selling_price - advance_pay)
                    conn = get_conn()
                    conn.execute(
                        "INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (
                            order_id, datetime.now().strftime("%Y-%m-%d %H:%M"),
                            cust_name, cust_phone, box_type, material,
                            f"{length}x{width}x{height}", finish, printing,
                            quantity, unit_selling_price, total_selling_price,
                            advance_pay, due_val, total_prod_cost,
                            estimated_profit, cust_notes, status_val
                        )
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"🎉 সফলভাবে গৃহীত হয়েছে! আপনার ট্র্যাকিং আইডি: **{order_id}**")

    with right_col:
        st.markdown(
            f'<div class="dark-glass-card">'
            f'<div style="display:flex; justify-content:space-between; align-items:center;">'
            f'<span style="font-size:0.85rem; color:#94a3b8;">INSTANT ESTIMATE</span>'
            f'<span class="live-badge">● Live Pricing</span>'
            f'</div>'
            f'<div style="margin-top:16px;">'
            f'<div style="font-size:0.95rem; color:#cbd5e1;">মোট প্রাক্কলিত মূল্য ({quantity} পিস)</div>'
            f'<div class="gradient-num">৳ {total_selling_price:,.2f}</div>'
            f'<div style="font-size:1rem; color:#e2e8f0;">প্রতি পিস বক্সের দাম: <strong>৳ {unit_selling_price}</strong></div>'
            f'</div>'
            f'<hr style="border-color:rgba(255,255,255,0.1); margin:20px 0;">'
            f'<div style="font-size:0.86rem; color:#94a3b8; margin-bottom:8px;">সিলেক্টেড স্পেসিফিকেশন:</div>'
            f'<div>'
            f'<span class="spec-pill">📦 {box_type}</span>'
            f'<span class="spec-pill">📄 {material}</span>'
            f'<span class="spec-pill">📏 {length}" × {width}" × {height}"</span>'
            f'<span class="spec-pill">✨ {finish}</span>'
            f'<span class="spec-pill">🎨 {printing}</span>'
            f'<span class="spec-pill">📐 Die-Cut: {surface_area:.1f} sq.in</span>'
            f'</div></div>',
            unsafe_allow_html=True
        )

# ==========================================================
# PART B: ADMIN BACKEND (শুধুমাত্র পাসওয়ার্ড দিয়ে লগইন করলে দেখা যাবে)
# ==========================================================
elif portal_mode == "🔐 Admin Backend (ব্যাকএন্ড)" and st.session_state.admin_logged_in:
    orders_df = get_orders_df()
    catalog_df = get_catalog_df()

    real_orders = orders_df[orders_df["status"] != "Quotation"] if not orders_df.empty else orders_df
    quote_orders = orders_df[orders_df["status"] == "Quotation"] if not orders_df.empty else orders_df

    total_due = real_orders["due_amount"].sum() if not real_orders.empty else 0.0
    total_collected = real_orders["paid_amount"].sum() if not real_orders.empty else 0.0
    total_sales = real_orders["total_price"].sum() if not real_orders.empty else 0.0
    order_count = len(real_orders)
    quote_count = len(quote_orders)

    today_vis = get_stat("today_visitors", "31")
    page_vw = get_stat("page_views", "47")
    live_usr = get_stat("live_now", "0")
    ord_clicks = get_stat("order_clicks", "203")

    best_prod_name = "১২ x ৯ x ৪ কাস্টম ডাই-কাট বক্স"
    best_prod_qty = 6000
    best_prod_rev = 75000.0
    if not real_orders.empty:
        top_row = real_orders.sort_values(by="total_price", ascending=False).iloc[0]
        best_prod_name = f"{top_row['dimensions']} {top_row['box_type'].split('(')[0].strip()}"
        best_prod_qty = int(top_row["quantity"])
        best_prod_rev = float(top_row["total_price"])

    if admin_page == "💠 ওভারভিউ":
        st.markdown(
            '<div style="margin-bottom:18px;">'
            '<div style="font-size:2.2rem; font-weight:900; color:#60a5fa; letter-spacing:-0.5px;">ওভারভিউ</div>'
            '<div style="font-size:0.88rem; color:#94a3b8;">মাসের হিসাব মাসের ১ তারিখ থেকে আজ পর্যন্ত • packxebec স্মার্ট ড্যাশবোর্ড</div>'
            '<hr style="border-color:#2563eb; margin-top:10px;">'
            '</div>',
            unsafe_allow_html=True
        )

        r1_c1, r1_c2, r1_c3 = st.columns(3, gap="medium")
        with r1_c1:
            st.markdown(
                f'<div class="ov-card">'
                f'<div class="ov-header"><span>[ মোট বাকি ]</span><span class="ov-link">হিসাব →</span></div>'
                f'<div class="ov-sub">কাস্টমারদের কাছে পাওনা</div>'
                f'<div class="ov-big">৳{to_bn_num(f"{total_due:,.0f}")}</div>'
                f'<div class="ov-foot">সব কাস্টমার মিলিয়ে এখন পর্যন্ত যত টাকা বাকি।</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with r1_c2:
            st.markdown(
                f'<div class="ov-card">'
                f'<div class="ov-header"><span>[ এই মাসে আদায় ]</span><span class="ov-link">হিসাব →</span></div>'
                f'<div class="ov-sub">হাতে পাওয়া টাকা</div>'
                f'<div class="ov-big">৳{to_bn_num(f"{total_collected:,.0f}")}</div>'
                f'<div class="ov-foot">এই মাসে কাস্টমারদের কাছ থেকে যত টাকা পাওয়া গেছে।</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with r1_c3:
            st.markdown(
                f'<div class="ov-card">'
                f'<div class="ov-header"><span>[ এই মাসের অর্ডার ও বিক্রি ]</span><span class="ov-link">অর্ডার →</span></div>'
                f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                f'<div><div class="ov-sub">অর্ডার</div><div class="ov-big" style="font-size:1.9rem;">{to_bn_num(order_count)}</div></div>'
                f'<div><div class="ov-sub">বিক্রি</div><div class="ov-big" style="font-size:1.9rem;">৳{to_bn_num(f"{total_sales:,.0f}")}</div></div>'
                f'</div>'
                f'<div class="ov-sub" style="margin-top:4px;">খোলা কোটেশন: <strong style="color:#f472b6; font-size:1.1rem;">{to_bn_num(quote_count)}</strong></div>'
                f'<div class="ov-foot">দাম জানানো হয়েছে, কাস্টমার এখনো হ্যাঁ বলেননি।</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        r2_c1, r2_c2, r2_c3 = st.columns(3, gap="medium")
        with r2_c1:
            st.markdown(
                f'<div class="ov-card">'
                f'<div class="ov-header"><span>[ আজকের ভিজিটর ]</span><span class="ov-link">ট্রাফিক →</span></div>'
                f'<div style="display:flex; gap:45px; align-items:center;">'
                f'<div><div class="ov-sub">আজ ভিজিটর</div><div class="ov-big">{to_bn_num(today_vis)}</div></div>'
                f'<div><div class="ov-sub">এখন সাইটে</div><div class="ov-big">{to_bn_num(live_usr)}</div></div>'
                f'</div>'
                f'<div class="ov-foot">পেজ ভিউ: {to_bn_num(page_vw)} &nbsp;|&nbsp; গত ৫ মিনিটে অ্যাক্টিভ</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with r2_c2:
            st.markdown(
                f'<div class="ov-card">'
                f'<div class="ov-header"><span>[ অর্ডার ক্লিক বনাম অর্ডার ]</span><span class="ov-link">আগ্রহ →</span></div>'
                f'<div style="display:flex; gap:45px; align-items:center;">'
                f'<div><div class="ov-sub">মেসেঞ্জার/কল/ক্লিক</div><div class="ov-big">{to_bn_num(ord_clicks)}</div></div>'
                f'<div><div class="ov-sub">খাতায় তোলা অর্ডার</div><div class="ov-big">{to_bn_num(order_count)}</div></div>'
                f'</div>'
                f'<div class="ov-foot">সাইটের কাস্টমাইজ বা কল বাটনে যতবার ট্যাপ হয়েছে, আর পাশে যত অর্ডার খাতায় তোলা হয়েছে।</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with r2_c3:
            st.markdown(
                f'<div class="ov-card">'
                f'<div class="ov-header"><span>[ এই মাসের সেরা প্রোডাক্ট ]</span><span class="ov-link">আগ্রহ →</span></div>'
                f'<div style="font-size:1.05rem; font-weight:800; color:#f8fafc; margin-bottom:10px;">{best_prod_name}</div>'
                f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                f'<div><div class="ov-sub">বিক্রি (পিস)</div><div class="ov-big" style="font-size:1.85rem;">{to_bn_num(f"{best_prod_qty:,}")}</div></div>'
                f'<div><div class="ov-sub">বিক্রির টাকা</div><div class="ov-big" style="font-size:1.85rem;">৳{to_bn_num(f"{best_prod_rev:,.0f}")}</div></div>'
                f'</div></div>',
                unsafe_allow_html=True
            )

    elif admin_page == "📑 অর্ডার (Orders)":
        st.markdown("### 📑 অর্ডার এবং খোলা কোটেশন ম্যানেজমেন্ট")
        if orders_df.empty:
            st.info("এখনো কোনো অর্ডার নেই।")
        else:
            st.dataframe(orders_df, use_container_width=True)
            csv_data = orders_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 এক্সেল / CSV ডাউনলোড করুন", data=csv_data, file_name="packxebec_orders.csv", mime="text/csv")

            st.markdown("---")
            st.markdown("#### ⚙️ অর্ডার স্ট্যাটাস পরিবর্তন করুন")
            c1, c2, c3 = st.columns(3)
            sel_ord = c1.selectbox("Order ID সিলেক্ট করুন", orders_df["order_id"].tolist())
            new_st = c2.selectbox("নতুন স্ট্যাটাস", [
                "Pending", "Quotation", "In Printing",
                "Glossy/Matte Lamination", "Die-Cutting", "Ready", "Delivered"
            ])
            c3.write("")
            c3.write("")
            if c3.button("🔄 স্ট্যাটাস আপডেট করুন"):
                conn = get_conn()
                conn.execute("UPDATE orders SET status=? WHERE order_id=?", (new_st, sel_ord))
                conn.commit()
                conn.close()
                st.success("✅ স্ট্যাটাস আপডেট হয়েছে!")
                st.rerun()

    elif admin_page == "👥 কাস্টমার (Customers)":
        st.markdown("### 👥 কাস্টমার তালিকা ও লেনদেন সামারি")
        if orders_df.empty:
            st.info("কোনো কাস্টমার ডাটা নেই।")
        else:
            cust_summary = orders_df.groupby(["customer_name", "phone"]).agg(
                মোট_অর্ডার=("order_id", "count"),
                মোট_বিল=("total_price", "sum"),
                মোট_জমা=("paid_amount", "sum"),
                মোট_বাকি=("due_amount", "sum")
            ).reset_index()
            st.dataframe(cust_summary, use_container_width=True)

    elif admin_page == "💳 হিসাব (Accounts & Due)":
        st.markdown("### 💳 হিসাব খাতা (মোট বাকি ও আদায় ম্যানেজার)")
        k1, k2, k3 = st.columns(3)
        k1.metric("মোট বিক্রি (Total Billed)", f"৳ {total_sales:,.0f}")
        k2.metric("এই মাসে আদায় (Collected)", f"৳ {total_collected:,.0f}")
        k3.metric("মোট বাকি (Total Due)", f"৳ {total_due:,.0f}")

        st.markdown("---")
        st.markdown("#### 💰 কাস্টমারের বকেয়া টাকা জমা নিন (Update Payment)")
        if not orders_df.empty:
            p_c1, p_c2, p_c3 = st.columns(3)
            pay_ord = p_c1.selectbox("Order ID সিলেক্ট করুন", orders_df["order_id"].tolist())
            cur_row = orders_df[orders_df["order_id"] == pay_ord].iloc[0]
            p_c2.info(f"কাস্টমার: **{cur_row['customer_name']}** | মোট বিল: ৳{cur_row['total_price']} | বর্তমান বাকি: **৳{cur_row['due_amount']}**")
            new_pay = p_c3.number_input("নতুন জমা টাকা (BDT)", min_value=0.0, value=float(cur_row["paid_amount"]), step=500.0)
            if st.button("✅ পেমেন্ট আপডেট করুন"):
                new_due = max(0.0, float(cur_row["total_price"]) - new_pay)
                conn = get_conn()
                conn.execute(
                    "UPDATE orders SET paid_amount=?, due_amount=? WHERE order_id=?",
                    (new_pay, new_due, pay_ord)
                )
                conn.commit()
                conn.close()
                st.success("🎉 পেমেন্ট ও বাকি হিসাব আপডেট হয়েছে!")
                st.rerun()

    elif admin_page == "📦 প্রোডাক্ট ও ছবি (Products CMS)":
        st.markdown("### 📦 প্রোডাক্ট গ্যালারি ও ছবি আপলোডার (Add/Edit Box Photos)")
        col_add, col_edit = st.columns([1.1, 1], gap="large")

        with col_add:
            st.markdown("#### ➕ নতুন বক্স ও ছবি যোগ করুন")
            with st.form("cms_add_box"):
                new_title = st.text_input("বক্সের নাম *", placeholder="যেমন: 300 GSM Swedish Perfume Box")
                new_code = st.text_input("কোড ও সাবটাইটেল *", placeholder="PX-109 • Swedish Board")
                up_file = st.file_uploader("ছবি আপলোড করুন (.jpg, .png, .webp)", type=["jpg", "jpeg", "png", "webp"])
                or_url = st.text_input("অথবা ছবির অনলাইন লিংক দিন:", placeholder="https://...")

                gc1, gc2 = st.columns(2)
                g_box = gc1.selectbox("বক্সের ধরন", box_options)
                g_mat = gc2.selectbox("ম্যাটেরিয়াল", mat_options)
                gc3, gc4 = st.columns(2)
                g_fin = gc3.selectbox("ফিনিশিং", finish_options)
                g_prt = gc4.selectbox("প্রিন্টিং", print_options)

                d1, d2, d3 = st.columns(3)
                g_l = d1.number_input("দৈর্ঘ্য (L)", value=6.0, step=0.5)
                g_w = d2.number_input("প্রস্থ (W)", value=4.0, step=0.5)
                g_h = d3.number_input("উচ্চতা (H)", value=3.0, step=0.5)

                if st.form_submit_button("✨ প্রোডাক্ট গ্যালারিতে সেভ করুন"):
                    if not new_title.strip():
                        st.error("বক্সের নাম দিন।")
                    else:
                        saved_path = "https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=600"
                        if up_file is not None:
                            ext = os.path.splitext(up_file.name)[1]
                            fname = f"box_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
                            saved_path = os.path.join("product_images", fname)
                            with open(saved_path, "wb") as f:
                                f.write(up_file.getbuffer())
                        elif or_url.strip():
                            saved_path = or_url.strip()

                        conn = get_conn()
                        conn.execute("""
                            INSERT INTO catalog (
                                title, code, img_path, box_type, material,
                                finish, printing, length, width, height, clicks
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                        """, (new_title, new_code or "PX-Custom", saved_path, g_box, g_mat, g_fin, g_prt, g_l, g_w, g_h))
                        conn.commit()
                        conn.close()
                        st.success("✅ নতুন বক্স গ্যালারিতে যুক্ত হয়েছে!")
                        st.rerun()

        with col_edit:
            st.markdown("#### 🖼️ বর্তমান প্রোডাক্টের ছবি পরিবর্তন বা ডিলিট")
            if not catalog_df.empty:
                bmap = {f"{r['id']} - {r['title']}": r["id"] for _, r in catalog_df.iterrows()}
                sel_lbl = st.selectbox("প্রোডাক্ট সিলেক্ট করুন:", list(bmap.keys()))
                sel_id = bmap[sel_lbl]
                srow = catalog_df[catalog_df["id"] == sel_id].iloc[0]

                st.markdown(
                    f'<div class="cat-card" style="max-width:260px;">'
                    f'<div class="cat-img-box"><img src="{render_img_src(srow["img_path"])}"></div>'
                    f'<div class="cat-info"><p class="cat-title">{srow["title"]}</p><p class="cat-sub">{srow["code"]}</p></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                rep_photo = st.file_uploader("নতুন ছবি আপলোড করুন:", type=["jpg", "jpeg", "png", "webp"], key="rep_up")
                if st.button("📸 ছবিটি আপডেট করুন"):
                    if rep_photo is not None:
                        ext = os.path.splitext(rep_photo.name)[1]
                        fname = f"box_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
                        fpath = os.path.join("product_images", fname)
                        with open(fpath, "wb") as f:
                            f.write(rep_photo.getbuffer())
                        conn = get_conn()
                        conn.execute("UPDATE catalog SET img_path=? WHERE id=?", (fpath, sel_id))
                        conn.commit()
                        conn.close()
                        st.success("✅ ছবি পরিবর্তন হয়েছে!")
                        st.rerun()

                if st.button("🗑️ এই প্রোডাক্টটি ডিলিট করুন"):
                    conn = get_conn()
                    conn.execute("DELETE FROM catalog WHERE id=?", (sel_id,))
                    conn.commit()
                    conn.close()
                    st.success("প্রোডাক্ট ডিলিট হয়েছে!")
                    st.rerun()

    elif admin_page == "🏷️ ক্যাটাগরি ও রেট (Categories)":
        st.markdown("### 🏷️ ক্যাটাগরি, ম্যাটেরিয়াল ও কাস্টমার রিকোয়ারমেন্ট বিল্ডার")
        rc1, rc2 = st.columns([1, 1.2], gap="large")
        with rc1:
            with st.form("cat_form"):
                cat_ch = st.selectbox("ক্যাটাগরি সিলেক্ট করুন", [
                    "material (বোর্ড ও জিএসএম)",
                    "box_type (বক্সের ধরন)",
                    "finish (লেমিনেশন ও ফিনিশিং)",
                    "printing (প্রিন্টিং ও প্লেট)"
                ])
                ckey = cat_ch.split(" ")[0]
                oname = st.text_input("নতুন অপশনের নাম *", placeholder="যেমন: 400 GSM Swedish Board")
                orate = st.number_input("রেট / চার্জ (BDT)", min_value=0.0, value=0.05, step=0.005, format="%.3f")
                if st.form_submit_button("➕ ক্যাটাগরিতে যোগ করুন"):
                    if oname.strip():
                        conn = get_conn()
                        conn.execute(
                            "INSERT OR REPLACE INTO custom_options (category, option_name, rate) VALUES (?, ?, ?)",
                            (ckey, oname.strip(), orate)
                        )
                        conn.commit()
                        conn.close()
                        st.success("✅ নতুন রিকোয়ারমেন্ট অপশন যুক্ত হয়েছে!")
                        st.rerun()
        with rc2:
            conn = get_conn()
            odf = pd.read_sql_query("SELECT id, category, option_name, rate FROM custom_options ORDER BY category", conn)
            conn.close()
            st.dataframe(odf, use_container_width=True)

    elif admin_page == "📊 ট্রাফিক (Traffic)":
        st.markdown("### 📊 ওয়েবসাইট ভিজিটর ও ট্রাফিক অ্যানালিটিক্স")
        tc1, tc2, tc3 = st.columns(3)
        tc1.metric("আজকের ভিজিটর", to_bn_num(today_vis))
        tc2.metric("মোট পেজ ভিউ", to_bn_num(page_vw))
        tc3.metric("এখন সাইটে লাইভ", to_bn_num(live_usr))

        with st.form("traffic_update"):
            st.markdown("#### ⚙️ ট্রাফিক কাউন্টার আপডেট / সিমুলেশন")
            u_vis = st.number_input("আজকের ভিজিটর সংখ্যা", value=int(today_vis))
            u_pvw = st.number_input("পেজ ভিউ সংখ্যা", value=int(page_vw))
            u_liv = st.number_input("এখন লাইভ ইউজার", value=int(live_usr))
            if st.form_submit_button("🔄 ট্রাফিক ডাটা সেভ করুন"):
                set_stat("today_visitors", u_vis)
                set_stat("page_views", u_pvw)
                set_stat("live_now", u_liv)
                st.success("✅ ট্রাফিক ডাটা আপডেট হয়েছে!")
                st.rerun()

    elif admin_page == "✨ প্রোডাক্টের আগ্রহ (Interest)":
        st.markdown("### ✨ প্রোডাক্টের আগ্রহ (অর্ডার ক্লিক বনাম অর্ডার)")
        st.info(f"মোট কাস্টমাইজ/অর্ডার বাটন ক্লিক: **{to_bn_num(ord_clicks)} বার** | খাতায় তোলা কনফার্ম অর্ডার: **{to_bn_num(order_count)} টি**")
        st.dataframe(
            catalog_df[["id", "title", "code", "material", "clicks"]].sort_values(by="clicks", ascending=False),
            use_container_width=True
        )

    elif admin_page == "🔍 সার্চ (Search)":
        st.markdown("### 🔍 অর্ডার, কাস্টমার বা প্রোডাক্ট সার্চ করুন")
        sq = st.text_input("অর্ডার আইডি, কাস্টমারের নাম, ফোন নম্বর বা বক্সের নাম লিখুন:")
        if sq.strip():
            res_ord = orders_df[
                orders_df["customer_name"].str.contains(sq, case=False, na=False) |
                orders_df["phone"].str.contains(sq, case=False, na=False) |
                orders_df["order_id"].str.contains(sq, case=False, na=False)
            ]
            st.markdown("#### 📋 অর্ডার সার্চ রেজাল্ট:")
            st.dataframe(res_ord, use_container_width=True)

    elif admin_page == "🌐 এসইও (SEO)":
        st.markdown("### 🌐 ওয়েবসাইট এসইও (Google SEO & Meta Tags)")
        with st.form("seo_form"):
            s_title = st.text_input("SEO Website Title", value=get_stat("seo_title"))
            s_keys = st.text_input("Target Keywords (কমা দিয়ে লিখুন)", value=get_stat("seo_keywords"))
            s_desc = st.text_area("Meta Description", value=get_stat("seo_desc"))
            if st.form_submit_button("🚀 SEO সেটিংস সেভ করুন"):
                set_stat("seo_title", s_title)
                set_stat("seo_keywords", s_keys)
                set_stat("seo_desc", s_desc)
                st.success("✅ এসইও কনফিগারেশন সেভ হয়েছে!")

    elif admin_page == "⚙️ সেটিংস (Settings)":
        st.markdown("### ⚙️ ফ্যাক্টরি ও সিস্টেম সেটিংস")
        with st.form("sys_settings"):
            f_phn = st.text_input("ফ্যাক্টরি হটলাইন / হোয়াটসঅ্যাপ নম্বর", value=get_stat("factory_phone"))
            ord_clk = st.number_input("মেসেঞ্জার/কল ট্যাপ কাউন্টার", value=int(ord_clicks))
            if st.form_submit_button("💾 সেটিংস সেভ করুন"):
                set_stat("factory_phone", f_phn)
                set_stat("order_clicks", ord_clk)
                st.success("✅ সেটিংস আপডেট হয়েছে!")
