import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
import base64

# ডার্ক থিম ও ফোল্ডার কনফিগ
os.makedirs(".streamlit", exist_ok=True)
os.makedirs("product_images", exist_ok=True)
os.makedirs("customer_files", exist_ok=True)

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
    initial_sidebar_state="collapsed"
)

DB_NAME = "packxebec_erp_v4.db"

# ==========================================================
# ১. SQLITE DATABASE ENGINE
# ==========================================================
def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            phone TEXT PRIMARY KEY,
            name TEXT,
            password TEXT,
            join_date TEXT,
            total_orders INTEGER DEFAULT 0
        )
    """)

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
            discount_saved REAL,
            paid_amount REAL,
            due_amount REAL,
            prod_cost REAL,
            profit REAL,
            design_file TEXT,
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
        ("factory_phone", "01XXXXXXXXX"),
        ("enable_customer_login", "1")
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

    c.execute("SELECT COUNT(*) FROM customers")
    if c.fetchone()[0] == 0:
        demo_custs = [
            ("01711000001", "Aarong Artisan", "1234", "2026-10-01", 2),
            ("01819000002", "Glow Cosmetics BD", "1234", "2026-10-15", 1)
        ]
        c.executemany(
            "INSERT OR IGNORE INTO customers VALUES (?,?,?,?,?)",
            demo_custs
        )

    c.execute("SELECT COUNT(*) FROM orders")
    if c.fetchone()[0] == 0:
        demo_orders = [
            ("PX-1101", "2026-11-10 11:20", "Aarong Artisan", "01711000001",
             "Tuck End Box (সুইডিশ বোর্ড স্ট্যান্ডার্ড)", "300 GSM Swedish Board (Best Seller)",
             "12x9x4", "Glossy Lamination (গ্লসি ফিনিশ)", "4 Color (CMYK Full Print)",
             6000, 12.5, 75000.0, 3500.0, 60000.0, 15000.0, 54000.0, 21000.0,
             "aarong_box_die.pdf", "Urgent Glossy Batch", "Delivered"),
            ("PX-1102", "2026-11-12 15:40", "Glow Cosmetics BD", "01819000002",
             "Mailer Box (ই-কমার্স প্রিমিয়াম লক)", "350 GSM Art Card",
             "7x5x2.5", "Matte Lamination (ম্যাট ফিনিশ)", "4 Color (CMYK Full Print)",
             2000, 16.2, 32400.0, 0.0, 19700.0, 12700.0, 23500.0, 8900.0,
             "glow_logo_ai.png", "Logo on top flap", "In Printing"),
            ("PX-1103", "2026-11-14 18:10", "BakeHouse Dhaka", "01912000003",
             "Food / Sweet Packaging Box", "300 GSM Swedish Board (Best Seller)",
             "8x8x3", "Glossy Lamination (গ্লসি ফিনিশ)", "Single Color Brand Print",
             500, 14.0, 7000.0, 0.0, 0.0, 7000.0, 5100.0, 1900.0,
             "No File", "Asked for price quote", "Quotation")
        ]
        c.executemany(
            "INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
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

def check_returning_customer(phone_str):
    if not phone_str or len(phone_str.strip()) < 6:
        return None
    p = phone_str.strip()
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT name, total_orders FROM customers WHERE phone=?", (p,))
    cust_row = c.fetchone()
    c.execute(
        "SELECT COUNT(*), SUM(total_price), SUM(paid_amount), SUM(due_amount) "
        "FROM orders WHERE phone=? AND status != 'Quotation'",
        (p,)
    )
    ord_row = c.fetchone()
    conn.close()

    ord_cnt = ord_row[0] if ord_row and ord_row[0] else 0
    if cust_row or ord_cnt > 0:
        name_val = cust_row[0] if cust_row else "Returning Client"
        return {
            "name": name_val,
            "phone": p,
            "order_count": max(ord_cnt, cust_row[1] if cust_row else 0),
            "total_billed": ord_row[1] or 0.0,
            "total_paid": ord_row[2] or 0.0,
            "total_due": ord_row[3] or 0.0
        }
    return None

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
if "cust_user" not in st.session_state:
    st.session_state.cust_user = None

# ==========================================================
# ৩. FULL-WIDTH NO-SIDEBAR DARK UI CSS
# ==========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #f8fafc;
}
.stApp {
    background: radial-gradient(circle at top center, #1e1b4b 0%, #090d16 45%, #060911 100%);
    color: #f8fafc;
}

section[data-testid="stSidebar"],
button[data-testid="collapsedControl"] {
    display: none !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}
h1, h2, h3, h4, h5, label, .stMarkdown p, div[data-testid="stWidgetLabel"] p {
    color: #f8fafc !important;
    font-weight: 600 !important;
}

.hero-logo-banner {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.92) 0%, rgba(19, 28, 49, 0.95) 100%);
    border: 1px solid #26334d;
    border-radius: 22px;
    padding: 28px 32px;
    text-align: center;
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.55);
    position: relative;
    overflow: hidden;
    margin-bottom: 22px;
}
.hero-logo-banner::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 5px;
    background: linear-gradient(90deg, #ec4899, #8b5cf6, #3b82f6);
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
    padding: 6px 15px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    border: 1px solid rgba(74, 222, 128, 0.28);
    display: inline-block;
}
.vip-badge {
    background: linear-gradient(90deg, rgba(236, 72, 153, 0.2), rgba(139, 92, 246, 0.2));
    color: #f472b6 !important;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    border: 1px solid rgba(244, 114, 182, 0.4);
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
# ৪. BIG CENTER BRAND LOGO HEADER (ক্লিন ব্যানার - নোট ছাড়া)
# ==========================================================
st.markdown(
    f'<div class="hero-logo-banner">'
    f'<img src="{LOGO_SRC}" style="width:280px; max-width:85%; height:auto; margin-bottom:10px;">'
    f'<div style="color:#cbd5e1; font-size:1.02rem; font-weight:500; margin-bottom:12px;">'
    f'Custom Packaging Configurator • 300 GSM Swedish Board • Direct Factory Printing'
    f'</div>'
    f'<div>'
    f'<span class="live-badge">● Online Ordering Active</span>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True
)

# ==========================================================
# PART A: CUSTOMER STUDIO (শুধুমাত্র যখন অ্যাডমিন মোড অফ থাকে)
# ==========================================================
if not st.session_state.admin_logged_in:
    # অ্যাডমিন সেটিংস থেকে কাস্টমার লগইন অপশন চালু থাকলে তবেই দেখাবে (এবং কোনো বাড়তি নোট বক্স ছাড়া)
    if get_stat("enable_customer_login", "1") == "1":
        if st.session_state.cust_user:
            u = st.session_state.cust_user
            c_top1, c_top2 = st.columns([3, 1])
            with c_top1:
                st.markdown(
                    f'<div class="dark-glass-card" style="padding:16px 22px;">'
                    f'<span class="vip-badge">👑 মেম্বার প্রোফাইল</span>'
                    f'<h4 style="margin:6px 0 2px 0;">স্বাগতম, {u["name"]} ({u["phone"]})</h4>'
                    f'<div style="font-size:0.84rem; color:#cbd5e1;">'
                    f'পূর্ববর্তী অর্ডার: <b>{u["order_count"]} টি</b> | '
                    f'মোট বিল: <b>৳{u["total_billed"]:,.0f}</b> | '
                    f'বর্তমান বাকি: <b style="color:#f472b6;">৳{u["total_due"]:,.0f}</b>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
            with c_top2:
                if st.button("🚪 কাস্টমার লগআউট"):
                    st.session_state.cust_user = None
                    st.rerun()

            with st.expander("📜 আপনার পূর্ববর্তী অর্ডারের রেকর্ড দেখুন"):
                conn = get_conn()
                my_ords = pd.read_sql_query(
                    "SELECT order_id, date, box_type, dimensions, quantity, total_price, discount_saved, paid_amount, due_amount, design_file, status "
                    "FROM orders WHERE phone=? ORDER BY date DESC",
                    conn, params=(u["phone"],)
                )
                conn.close()
                if not my_ords.empty:
                    st.dataframe(my_ords, use_container_width=True)
        else:
            with st.expander("👤 কাস্টমার মেম্বার লগইন / রেজিস্ট্রেশন", expanded=False):
                auth_tab1, auth_tab2 = st.tabs(["🔑 মেম্বার লগইন", "➕ নতুন অ্যাকাউন্ট"])
                with auth_tab1:
                    l_c1, l_c2 = st.columns(2)
                    l_phone = l_c1.text_input("মোবাইল নম্বর", placeholder="01XXXXXXXXX", key="lp")
                    l_pass = l_c2.text_input("পাসওয়ার্ড", type="password", key="lps")
                    if st.button("লগইন করুন", key="lbtn"):
                        conn = get_conn()
                        c = conn.cursor()
                        c.execute("SELECT name FROM customers WHERE phone=? AND password=?", (l_phone.strip(), l_pass.strip()))
                        r = c.fetchone()
                        conn.close()
                        rec = check_returning_customer(l_phone.strip())
                        if r or rec:
                            st.session_state.cust_user = rec if rec else {
                                "name": r[0], "phone": l_phone.strip(),
                                "order_count": 1, "total_billed": 0.0, "total_paid": 0.0, "total_due": 0.0
                            }
                            st.rerun()
                        else:
                            st.error("❌ এই নম্বরে কোনো অ্যাকাউন্ট পাওয়া যায়নি।")

                with auth_tab2:
                    r_c1, r_c2, r_c3 = st.columns(3)
                    r_name = r_c1.text_input("আপনার নাম / ব্র্যান্ডের নাম", key="rn")
                    r_phone = r_c2.text_input("মোবাইল নম্বর", key="rp")
                    r_pass = r_c3.text_input("পাসওয়ার্ড সেট করুন", type="password", key="rps")
                    if st.button("অ্যাকাউন্ট তৈরি করুন", key="rbtn"):
                        if r_name.strip() and r_phone.strip() and r_pass.strip():
                            conn = get_conn()
                            conn.execute(
                                "INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, 1)",
                                (r_phone.strip(), r_name.strip(), r_pass.strip(), datetime.now().strftime("%Y-%m-%d"))
                            )
                            conn.commit()
                            conn.close()
                            st.session_state.cust_user = check_returning_customer(r_phone.strip())
                            st.rerun()
                        else:
                            st.warning("সবগুলো ঘর পূরণ করুন।")

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

    left_col, right_col = st.columns([1.25, 1], gap="large")

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

        st.markdown("#### 📝 ৩. কাস্টমার তথ্য ও ডিজাইন ফাইল আপলোড")
        default_name = st.session_state.cust_user["name"] if st.session_state.cust_user else ""
        default_phone = st.session_state.cust_user["phone"] if st.session_state.cust_user else ""

        fc1, fc2 = st.columns(2)
        cust_phone = fc1.text_input("মোবাইল নম্বর *", value=default_phone, placeholder="01XXXXXXXXX")
        live_old_record = st.session_state.cust_user or check_returning_customer(cust_phone)
        if live_old_record and not default_name:
            default_name = live_old_record["name"]

        cust_name = fc2.text_input("আপনার নাম / ব্র্যান্ডের নাম *", value=default_name)

        design_upload = st.file_uploader(
            "📂 আপনার বক্সের ডিজাইন / লোগো ফাইল যুক্ত করুন (.pdf, .ai, .psd, .png, .jpg, .zip)",
            type=["pdf", "ai", "eps", "psd", "png", "jpg", "jpeg", "zip"]
        )

        req_type = st.radio("রিকোয়েস্টের ধরন:", ["অর্ডার কনফার্ম (Order)", "খোলা কোটেশন (Price Quotation Only)"], horizontal=True)
        advance_pay = st.number_input("অ্যাডভান্স পেমেন্ট (যদি থাকে - BDT)", min_value=0.0, value=0.0, step=500.0)
        cust_notes = st.text_area("কাস্টম রিকোয়ারমেন্ট বা ডিজাইন নির্দেশনা (ঐচ্ছিক)", height=70)

        surface_area = 2 * ((length * width) + (length * height) + (width * height)) * 1.25
        board_cost = surface_area * mat_dict.get(material, 0.045)
        lam_cost = surface_area * finish_dict.get(finish, 0.015)
        raw_setup_cost = print_dict.get(printing, 2500.0)
        making_cost = 1.50 + box_dict.get(box_type, 0.0)

        margin = 1.35 if quantity < 1000 else (1.25 if quantity < 3000 else 1.18)

        reg_unit_cost = board_cost + lam_cost + making_cost + (raw_setup_cost / quantity)
        reg_unit_price = round(reg_unit_cost * margin, 2)
        reg_total_price = round(reg_unit_price * quantity, 2)

        if live_old_record:
            discounted_setup = raw_setup_cost * 0.40
            vip_unit_cost = board_cost + lam_cost + making_cost + (discounted_setup / quantity)
            unit_selling_price = round((vip_unit_cost * margin) * 0.95, 2)
            total_selling_price = round(unit_selling_price * quantity, 2)
            discount_saved = round(reg_total_price - total_selling_price, 2)
            total_prod_cost = round(vip_unit_cost * quantity, 2)
        else:
            unit_selling_price = reg_unit_price
            total_selling_price = reg_total_price
            discount_saved = 0.0
            total_prod_cost = round(reg_unit_cost * quantity, 2)

        estimated_profit = round(total_selling_price - total_prod_cost, 2)

        if st.button("🚀 অর্ডার ও ফাইল সাবমিট করুন"):
            if not cust_name.strip() or not cust_phone.strip():
                st.error("⚠️ অনুগ্রহ করে আপনার নাম এবং মোবাইল নম্বর দিন।")
            else:
                order_id = f"PX-{datetime.now().strftime('%m%d%H%M%S')}"
                status_val = "Quotation" if "কোটেশন" in req_type else "Pending"
                due_val = max(0.0, total_selling_price - advance_pay)

                saved_design_name = "No File"
                if design_upload is not None:
                    saved_design_name = f"{order_id}_{design_upload.name}"
                    save_f_path = os.path.join("customer_files", saved_design_name)
                    with open(save_f_path, "wb") as f:
                        f.write(design_upload.getbuffer())

                conn = get_conn()
                conn.execute(
                    "INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        order_id, datetime.now().strftime("%Y-%m-%d %H:%M"),
                        cust_name.strip(), cust_phone.strip(), box_type, material,
                        f"{length}x{width}x{height}", finish, printing,
                        quantity, unit_selling_price, total_selling_price,
                        discount_saved, advance_pay, due_val, total_prod_cost,
                        estimated_profit, saved_design_name, cust_notes, status_val
                    )
                )
                conn.execute(
                    "INSERT OR IGNORE INTO customers VALUES (?, ?, '1234', ?, 1)",
                    (cust_phone.strip(), cust_name.strip(), datetime.now().strftime("%Y-%m-%d"))
                )
                conn.commit()
                conn.close()
                st.success(f"🎉 অর্ডার সফলভাবে সম্পন্ন হয়েছে! আপনার ট্র্যাকিং আইডি: **{order_id}**")

    with right_col:
        discount_html = ""
        if live_old_record and discount_saved > 0:
            discount_html = (
                f'<div style="background:rgba(34,197,94,0.15); border:1px solid #4ade80; padding:10px 14px; border-radius:10px; margin-top:12px;">'
                f'<div style="color:#4ade80; font-weight:700; font-size:0.88rem;">👑 মেম্বার ডিসকাউন্ট প্রযোজ্য হয়েছে!</div>'
                f'<div style="color:#cbd5e1; font-size:0.82rem;">রেগুলার মূল্য: <del>৳ {reg_total_price:,.2f}</del> | সাশ্রয়: <b>৳ {discount_saved:,.2f}</b></div>'
                f'</div>'
            )

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
            f'{discount_html}'
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
# PART B: ADMIN BACKEND (এখানে কাস্টমার লগইন বক্স সম্পূর্ণ বন্ধ)
# ==========================================================
else:
    top_adm1, top_adm2 = st.columns([3, 1])
    with top_adm1:
        st.markdown("### 🔐 packxebec — অ্যাডমিন ব্যাকএন্ড ও ইআরপি কন্ট্রোল প্যানেল")
    with top_adm2:
        if st.button("🚪 অ্যাডমিন থেকে বের হন (Back to Customer Site)"):
            st.session_state.admin_logged_in = False
            st.rerun()

    admin_page = st.selectbox(
        "🧭 ব্যাকএন্ড মেনু সিলেক্ট করুন:",
        [
            "💠 ওভারভিউ (Overview)",
            "📑 অর্ডার ও কাস্টমার ফাইল (Orders & Files)",
            "👥 কাস্টমার রেকর্ড ও ডিসকাউন্ট খাতা (Customers)",
            "💳 হিসাব খাতা (Accounts & Due)",
            "📦 প্রোডাক্ট ও ছবি আপলোডার (Products CMS)",
            "🏷️ ক্যাটাগরি ও রেট (Categories)",
            "📊 ট্রাফিক (Traffic)",
            "✨ প্রোডাক্টের আগ্রহ (Interest)",
            "🔍 সার্চ (Search)",
            "🌐 এসইও (SEO)",
            "⚙️ সেটিংস (Settings)"
        ]
    )
    st.markdown("<hr style='margin:14px 0; border-color:rgba(255,255,255,0.12);'>", unsafe_allow_html=True)

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

    if "ওভারভিউ" in admin_page:
        r1_c1, r1_c2, r1_c3 = st.columns(3, gap="medium")
        with r1_c1:
            st.markdown(
                f'<div class="ov-card">'
                f'<div class="ov-header"><span>[ মোট বাকি ]</span><span class="ov-link">হিসাব →</span></div>'
                f'<div class="ov-sub">কাস্টমারদের কাছে পাওনা</div>'
                f'<div class="ov-big">৳{to_bn_num(f"{total_due:,.0f}")}</div>'
                f'<div class="ov-foot">সব কাস্টমার মিলিয়ে এখন পর্যন্ত যত টাকা বাকি।</div>'
                f'</div>', unsafe_allow_html=True
            )
        with r1_c2:
            st.markdown(
                f'<div class="ov-card">'
                f'<div class="ov-header"><span>[ এই মাসে আদায় ]</span><span class="ov-link">হিসাব →</span></div>'
                f'<div class="ov-sub">হাতে পাওয়া টাকা</div>'
                f'<div class="ov-big">৳{to_bn_num(f"{total_collected:,.0f}")}</div>'
                f'<div class="ov-foot">এই মাসে কাস্টমারদের কাছ থেকে যত টাকা পাওয়া গেছে।</div>'
                f'</div>', unsafe_allow_html=True
            )
        with r1_c3:
            st.markdown(
                f'<div class="ov-card">'
                f'<div class="ov-header"><span>[ এই মাসের অর্ডার ও বিক্রি ]</span><span class="ov-link">অর্ডার →</span></div>'
                f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                f'<div><div class="ov-sub">অর্ডার</div><div class="ov-big" style="font-size:1.9rem;">{to_bn_num(order_count)}</div></div>'
                f'<div><div class="ov-sub">বিক্রি</div><div class="ov-big" style="font-size:1.9rem;">৳{to_bn_num(f"{total_sales:,.0f}")}</div></div>'
                f'</div>'
                f'<div class="ov-sub" style="margin-top:4px;">খোলা কোটেশন: <strong style="color:#f472b6;">{to_bn_num(quote_count)}</strong></div>'
                f'<div class="ov-foot">দাম জানানো হয়েছে, কাস্টমার এখনো হ্যাঁ বলেননি।</div>'
                f'</div>', unsafe_allow_html=True
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
                f'<div class="ov-foot">পেজ ভিউ: {to_bn_num(page_vw)} | গত ৫ মিনিটে অ্যাক্টিভ</div>'
                f'</div>', unsafe_allow_html=True
            )
        with r2_c2:
            st.markdown(
                f'<div class="ov-card">'
                f'<div class="ov-header"><span>[ অর্ডার ক্লিক বনাম অর্ডার ]</span><span class="ov-link">আগ্রহ →</span></div>'
                f'<div style="display:flex; gap:45px; align-items:center;">'
                f'<div><div class="ov-sub">মেসেঞ্জার/কল/ক্লিক</div><div class="ov-big">{to_bn_num(ord_clicks)}</div></div>'
                f'<div><div class="ov-sub">খাতায় তোলা অর্ডার</div><div class="ov-big">{to_bn_num(order_count)}</div></div>'
                f'</div>'
                f'<div class="ov-foot">কাস্টমাইজ বাটনে যতবার ট্যাপ হয়েছে বনাম কনফার্ম অর্ডার।</div>'
                f'</div>', unsafe_allow_html=True
            )
        with r2_c3:
            st.markdown(
                f'<div class="ov-card">'
                f'<div class="ov-header"><span>[ এই মাসের সেরা প্রোডাক্ট ]</span><span class="ov-link">আগ্রহ →</span></div>'
                f'<div style="font-size:1.05rem; font-weight:800; color:#f8fafc; margin-bottom:10px;">{best_prod_name}</div>'
                f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                f'<div><div class="ov-sub">বিক্রি (পিস)</div><div class="ov-big" style="font-size:1.85rem;">{to_bn_num(f"{best_prod_qty:,}")}</div></div>'
                f'<div><div class="ov-sub">বিক্রির টাকা</div><div class="ov-big" style="font-size:1.85rem;">৳{to_bn_num(f"{best_prod_rev:,.0f}")}</div></div>'
                f'</div></div>', unsafe_allow_html=True
            )

    elif "অর্ডার" in admin_page:
        st.markdown("### 📑 অর্ডার, কোটেশন এবং কাস্টমারের আপলোড করা ডিজাইন ফাইল")
        if orders_df.empty:
            st.info("এখনো কোনো অর্ডার নেই।")
        else:
            st.dataframe(orders_df, use_container_width=True)
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

    elif "কাস্টমার" in admin_page:
        st.markdown("### 👥 রেজিস্টার্ড ও পুরাতন কাস্টমার রেকর্ড")
        conn = get_conn()
        cust_df = pd.read_sql_query("SELECT phone, name, join_date, total_orders FROM customers", conn)
        conn.close()
        st.dataframe(cust_df, use_container_width=True)

        if not orders_df.empty:
            st.markdown("#### 📊 কাস্টমার লেনদেন ও ডিসকাউন্ট সামারি")
            cust_summary = orders_df.groupby(["customer_name", "phone"]).agg(
                মোট_অর্ডার=("order_id", "count"),
                মোট_বিল=("total_price", "sum"),
                মোট_ডিসকাউন্ট_সাশ্রয়=("discount_saved", "sum"),
                মোট_জমা=("paid_amount", "sum"),
                মোট_বাকি=("due_amount", "sum")
            ).reset_index()
            st.dataframe(cust_summary, use_container_width=True)

    elif "হিসাব" in admin_page:
        st.markdown("### 💳 হিসাব খাতা (মোট বাকি ও আদায় ম্যানেজার)")
        if not orders_df.empty:
            p_c1, p_c2, p_c3 = st.columns(3)
            pay_ord = p_c1.selectbox("Order ID সিলেক্ট করুন", orders_df["order_id"].tolist())
            cur_row = orders_df[orders_df["order_id"] == pay_ord].iloc[0]
            p_c2.info(f"কাস্টমার: **{cur_row['customer_name']}** | মোট বিল: ৳{cur_row['total_price']} | বাকি: **৳{cur_row['due_amount']}**")
            new_pay = p_c3.number_input("নতুন জমা টাকা (BDT)", min_value=0.0, value=float(cur_row["paid_amount"]), step=500.0)
            if st.button("✅ পেমেন্ট আপডেট করুন"):
                new_due = max(0.0, float(cur_row["total_price"]) - new_pay)
                conn = get_conn()
                conn.execute("UPDATE orders SET paid_amount=?, due_amount=? WHERE order_id=?", (new_pay, new_due, pay_ord))
                conn.commit()
                conn.close()
                st.success("🎉 পেমেন্ট আপডেট হয়েছে!")
                st.rerun()

    elif "প্রোডাক্ট ও ছবি" in admin_page:
        st.markdown("### 📦 প্রোডাক্ট গ্যালারি ও ছবি আপলোডার")
        col_add, col_edit = st.columns([1.1, 1], gap="large")
        with col_add:
            with st.form("cms_add_box"):
                new_title = st.text_input("বক্সের নাম *")
                new_code = st.text_input("কোড ও সাবটাইটেল *")
                up_file = st.file_uploader("ছবি আপলোড করুন (.jpg, .png, .webp)", type=["jpg", "jpeg", "png", "webp"])
                or_url = st.text_input("অথবা ছবির অনলাইন লিংক দিন:")
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
                    if new_title.strip():
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
                            INSERT INTO catalog (title, code, img_path, box_type, material, finish, printing, length, width, height, clicks)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                        """, (new_title, new_code or "PX-Custom", saved_path, g_box, g_mat, g_fin, g_prt, g_l, g_w, g_h))
                        conn.commit()
                        conn.close()
                        st.success("✅ নতুন বক্স যুক্ত হয়েছে!")
                        st.rerun()

        with col_edit:
            if not catalog_df.empty:
                bmap = {f"{r['id']} - {r['title']}": r["id"] for _, r in catalog_df.iterrows()}
                sel_lbl = st.selectbox("প্রোডাক্ট সিলেক্ট করুন:", list(bmap.keys()))
                sel_id = bmap[sel_lbl]
                rep_photo = st.file_uploader("নতুন ছবি আপলোড করুন:", type=["jpg", "jpeg", "png", "webp"], key="rep_up")
                if st.button("📸 ছবিটি আপডেট করুন") and rep_photo is not None:
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
                    st.rerun()

    elif "ক্যাটাগরি" in admin_page:
        with st.form("cat_form"):
            cat_ch = st.selectbox("ক্যাটাগরি", ["material", "box_type", "finish", "printing"])
            oname = st.text_input("নতুন অপশনের নাম *")
            orate = st.number_input("রেট (BDT)", min_value=0.0, value=0.05, step=0.005, format="%.3f")
            if st.form_submit_button("➕ যোগ করুন") and oname.strip():
                conn = get_conn()
                conn.execute("INSERT OR REPLACE INTO custom_options (category, option_name, rate) VALUES (?, ?, ?)", (cat_ch, oname.strip(), orate))
                conn.commit()
                conn.close()
                st.rerun()

    elif "ট্রাফিক" in admin_page:
        with st.form("traffic_update"):
            u_vis = st.number_input("আজকের ভিজিটর সংখ্যা", value=int(today_vis))
            u_pvw = st.number_input("পেজ ভিউ সংখ্যা", value=int(page_vw))
            u_liv = st.number_input("এখন লাইভ ইউজার", value=int(live_usr))
            if st.form_submit_button("🔄 ট্রাফিক ডাটা সেভ করুন"):
                set_stat("today_visitors", u_vis)
                set_stat("page_views", u_pvw)
                set_stat("live_now", u_liv)
                st.success("✅ ট্রাফিক ডাটা আপডেট হয়েছে!")
                st.rerun()

    elif "আগ্রহ" in admin_page:
        st.dataframe(catalog_df[["id", "title", "code", "material", "clicks"]].sort_values(by="clicks", ascending=False), use_container_width=True)

    elif "সার্চ" in admin_page:
        sq = st.text_input("অর্ডার আইডি, কাস্টমারের নাম বা ফোন নম্বর লিখুন:")
        if sq.strip():
            res_ord = orders_df[
                orders_df["customer_name"].str.contains(sq, case=False, na=False) |
                orders_df["phone"].str.contains(sq, case=False, na=False) |
                orders_df["order_id"].str.contains(sq, case=False, na=False)
            ]
            st.dataframe(res_ord, use_container_width=True)

    elif "এসইও" in admin_page:
        with st.form("seo_form"):
            s_title = st.text_input("SEO Website Title", value=get_stat("seo_title"))
            s_keys = st.text_input("Target Keywords", value=get_stat("seo_keywords"))
            s_desc = st.text_area("Meta Description", value=get_stat("seo_desc"))
            if st.form_submit_button("🚀 SEO সেটিংস সেভ করুন"):
                set_stat("seo_title", s_title)
                set_stat("seo_keywords", s_keys)
                set_stat("seo_desc", s_desc)
                st.success("✅ এসইও কনফিগারেশন সেভ হয়েছে!")

    elif "সেটিংস" in admin_page:
        st.markdown("### ⚙️ সিস্টেম ও কাস্টমার লগইন কন্ট্রোল")
        with st.form("sys_settings"):
            cur_login_state = get_stat("enable_customer_login", "1") == "1"
            toggle_login = st.checkbox("কাস্টমার পেজে 'মেম্বার লগইন' অপশন চালু রাখুন (চেক তুলে দিলে লগইন বক্স সম্পূর্ণ বন্ধ হয়ে যাবে)", value=cur_login_state)
            f_phn = st.text_input("ফ্যাক্টরি হটলাইন নম্বর", value=get_stat("factory_phone"))
            ord_clk = st.number_input("মেসেঞ্জার/কল ট্যাপ কাউন্টার", value=int(ord_clicks))
            if st.form_submit_button("💾 সেটিংস সেভ করুন"):
                set_stat("enable_customer_login", "1" if toggle_login else "0")
                set_stat("factory_phone", f_phn)
                set_stat("order_clicks", ord_clk)
                st.success("✅ সেটিংস সফলভাবে আপডেট হয়েছে!")
                st.rerun()

# ==========================================================
# ৬. DISCREET FOOTER STAFF LOGIN
# ==========================================================
st.markdown("<hr style='margin:40px 0 15px 0; border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
f_col1, f_col2 = st.columns([3, 1])
with f_col1:
    st.caption("© 2026 packxebec Custom Packaging Studio • 300 GSM Swedish Board Specialist")
with f_col2:
    if not st.session_state.admin_logged_in:
        with st.expander("🔐 Staff ERP Portal"):
            adm_pw = st.text_input("Admin Password", type="password", key="footer_adm_pw")
            if st.button("Login to Backend"):
                if adm_pw == "admin123":
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("ভুল পাসওয়ার্ড!")
