"""
AssetChain - Blockchain Asset Tokenization DApp
Flask Backend Application
DAS5003 - Section 3(a)
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import hashlib
import json
import os
import datetime
import random
import string

app = Flask(__name__)
app.secret_key = "assetchain_secret_2026"

# ─────────────────────────────────────────
# SIMULATED DATABASE (in-memory)
# ─────────────────────────────────────────

USERS = {
    "ashan@assetchain.io": {
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "first_name": "Ashan",
        "last_name": "Perera",
        "wallet": "0x3f4a8c2d9b2c",
        "role": "Asset Owner / Issuer",
    }
}

ASSETS = [
    {"id": "AST-0021", "name": "Marina Bay Tower A",     "type": "Real Estate",  "location": "Singapore",    "valuation": 2400000, "token_name": "MarinaBay Token", "symbol": "MBT", "supply": 1000000, "sold": 640000, "price": 2.40,  "emoji": "🏢", "color": "#3B82F6", "status": "Active"},
    {"id": "AST-0022", "name": "Colombo Hilton Suite 14","type": "Hospitality",  "location": "Sri Lanka",    "valuation":  980000, "token_name": "ColomboHilton",   "symbol": "CHS", "supply":  500000, "sold": 240000, "price": 1.96,  "emoji": "🏨", "color": "#F59E0B", "status": "Active"},
    {"id": "AST-0023", "name": "Industrial Warehouse K7","type": "Industrial",   "location": "London, UK",   "valuation": 1750000, "token_name": "WarehouseK7",     "symbol": "IWK", "supply":  750000, "sold": 540000, "price": 2.33,  "emoji": "🏭", "color": "#8B5CF6", "status": "Partial"},
    {"id": "AST-0024", "name": "Green Valley Villa",     "type": "Residential",  "location": "Dubai, UAE",   "valuation":  650000, "token_name": "GreenValley",     "symbol": "GVV", "supply":  250000, "sold":  75000, "price": 2.60,  "emoji": "🏠", "color": "#10B981", "status": "Active"},
    {"id": "AST-0025", "name": "Tech Park Block C",      "type": "Commercial",   "location": "Bangalore, IN","valuation": 3600000, "token_name": "TechPark",        "symbol": "TPK", "supply": 2000000, "sold": 300000, "price": 1.80,  "emoji": "🏗", "color": "#EF4444", "status": "IPO"},
    {"id": "AST-0026", "name": "Retail Hub Plaza",       "type": "Retail",       "location": "Tokyo, JP",    "valuation": 1240000, "token_name": "RetailHub",       "symbol": "RHP", "supply":  400000, "sold": 220000, "price": 3.10,  "emoji": "🏪", "color": "#3B82F6", "status": "Active"},
]

TOP_HOLDERS = [
    {"rank": 1,  "address": "0x3f4a...9b2c", "mbt": "128K", "chs": "62K",  "iwk": "54K", "gvv": "40K", "total": "284,500", "pct": "11.9%", "value": "$682K"},
    {"rank": 2,  "address": "0x8c1d...4e7f", "mbt": "98K",  "chs": "48K",  "iwk": "38K", "gvv": "26K", "total": "210,300", "pct": "8.8%",  "value": "$504K"},
    {"rank": 3,  "address": "0x2b9e...7a1d", "mbt": "82K",  "chs": "40K",  "iwk": "32K", "gvv": "24K", "total": "178,200", "pct": "7.4%",  "value": "$427K"},
    {"rank": 4,  "address": "0x5f2c...3b8a", "mbt": "64K",  "chs": "32K",  "iwk": "26K", "gvv": "20K", "total": "142,100", "pct": "5.9%",  "value": "$341K"},
    {"rank": 5,  "address": "0x9d4f...6c2e", "mbt": "54K",  "chs": "26K",  "iwk": "22K", "gvv": "17K", "total": "118,900", "pct": "5.0%",  "value": "$285K"},
    {"rank": 6,  "address": "0x1a7b...0f5d", "mbt": "44K",  "chs": "22K",  "iwk": "18K", "gvv": "14K", "total": "97,400",  "pct": "4.1%",  "value": "$234K"},
    {"rank": 7,  "address": "0x6e3d...2c9b", "mbt": "38K",  "chs": "19K",  "iwk": "16K", "gvv": "11K", "total": "84,200",  "pct": "3.5%",  "value": "$202K"},
    {"rank": 8,  "address": "0x4c8a...1d6f", "mbt": "32K",  "chs": "16K",  "iwk": "14K", "gvv": "10K", "total": "71,500",  "pct": "3.0%",  "value": "$172K"},
    {"rank": 9,  "address": "0x7f1e...9a4c", "mbt": "26K",  "chs": "14K",  "iwk": "11K", "gvv": "7K",  "total": "58,300",  "pct": "2.4%",  "value": "$140K"},
    {"rank": 10, "address": "0x0b5d...7e2a", "mbt": "20K",  "chs": "10K",  "iwk": "9K",  "gvv": "5K",  "total": "44,100",  "pct": "1.8%",  "value": "$106K"},
]

TRANSACTIONS = [
    {"type": "Purchase", "type_color": "#10B981", "asset": "Marina Bay Tower A",     "symbol": "MBT", "from_addr": "0x3f4a...9b2c", "to_addr": "0x8c1d...4e7f", "tokens": "10,000", "value": "$24,000",  "time": "2m ago",   "tx_hash": "0xabc123..."},
    {"type": "Transfer", "type_color": "#3B82F6", "asset": "Green Valley Villa",     "symbol": "GVV", "from_addr": "0x5f2c...3b8a", "to_addr": "0x9d4f...6c2e", "tokens": "5,500",  "value": "$14,300",  "time": "18m ago",  "tx_hash": "0xdef456..."},
    {"type": "Sell",     "type_color": "#EF4444", "asset": "Industrial Warehouse K7","symbol": "IWK", "from_addr": "0x2b9e...7a1d", "to_addr": "0x1a7b...0f5d", "tokens": "20,000", "value": "$46,600",  "time": "1h ago",   "tx_hash": "0xghi789..."},
    {"type": "Purchase", "type_color": "#10B981", "asset": "Colombo Hilton Suite",   "symbol": "CHS", "from_addr": "0x6e3d...2c9b", "to_addr": "0x4c8a...1d6f", "tokens": "8,200",  "value": "$16,072",  "time": "3h ago",   "tx_hash": "0xjkl012..."},
    {"type": "Transfer", "type_color": "#3B82F6", "asset": "Marina Bay Tower A",     "symbol": "MBT", "from_addr": "0x7f1e...9a4c", "to_addr": "0x0b5d...7e2a", "tokens": "3,000",  "value": "$7,200",   "time": "5h ago",   "tx_hash": "0xmno345..."},
]

NOTIFICATIONS = [
    {"icon": "⬡", "color": "rgba(59,130,246,0.15)", "icon_color": "#3B82F6", "title": "Token Purchase Confirmed",   "sub": "10,000 MBT purchased · Block #937,219",              "time": "2m ago",  "unread": True},
    {"icon": "▲", "color": "rgba(245,158,11,0.15)",  "icon_color": "#F59E0B", "title": "You entered Top 10 Holders", "sub": "0x3f4a...9b2c is now ranked #1 for MBT",             "time": "18m ago", "unread": True},
    {"icon": "⇄", "color": "rgba(16,185,129,0.15)",  "icon_color": "#10B981", "title": "Transfer Received",          "sub": "5,000 GVV tokens received from 0x5f2c...3b8a",       "time": "1h ago",  "unread": True},
    {"icon": "◈", "color": "rgba(139,92,246,0.15)",  "icon_color": "#8B5CF6", "title": "Asset Tokenized",            "sub": "Industrial Warehouse K7 (IWK) is now live",          "time": "3h ago",  "unread": False},
    {"icon": "⛽", "color": "rgba(107,127,163,0.15)", "icon_color": "#6B7FA3", "title": "Gas Price Alert",            "sub": "Ethereum gas dropped to 12 gwei",                    "time": "5h ago",  "unread": False},
    {"icon": "✓", "color": "rgba(16,185,129,0.15)",  "icon_color": "#10B981", "title": "Asset Definition Confirmed", "sub": "Green Valley Villa (GVV) successfully defined",       "time": "1d ago",  "unread": False},
]

PORTFOLIO = [
    {"emoji": "🏢", "name": "Marina Bay Tower A",     "type": "Real Estate · Singapore",  "symbol": "MBT", "sym_color": "#3B82F6", "tokens": 28400, "avg_cost": 2.20, "current": 2.40, "value": "$68,160", "pl": "+$5,680", "pl_color": "#10B981"},
    {"emoji": "🏨", "name": "Colombo Hilton Suite",   "type": "Hospitality · Sri Lanka",   "symbol": "CHS", "sym_color": "#F59E0B", "tokens": 15200, "avg_cost": 1.85, "current": 1.96, "value": "$29,792", "pl": "+$1,672", "pl_color": "#10B981"},
    {"emoji": "🏭", "name": "Industrial Warehouse K7","type": "Industrial · London",        "symbol": "IWK", "sym_color": "#8B5CF6", "tokens": 10500, "avg_cost": 2.50, "current": 2.33, "value": "$24,465", "pl": "-$1,785", "pl_color": "#EF4444"},
    {"emoji": "🏠", "name": "Green Valley Villa",     "type": "Residential · Dubai",        "symbol": "GVV", "sym_color": "#10B981", "tokens": 5200,  "avg_cost": 2.40, "current": 2.60, "value": "$13,520", "pl": "+$1,040", "pl_color": "#10B981"},
]

# ─────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────

def generate_asset_id():
    """Generate unique Asset ID"""
    return "AST-" + str(random.randint(1000, 9999))

def generate_tx_hash():
    """Simulate a blockchain transaction hash"""
    return "0x" + ''.join(random.choices(string.hexdigits.lower(), k=64))

def format_currency(value):
    """Format number as USD currency string"""
    return "${:,.2f}".format(value)

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def is_logged_in():
    """Check if user is logged in"""
    return "user" in session

def get_current_user():
    """Get current logged-in user data"""
    if is_logged_in():
        return USERS.get(session["user"])
    return None

def get_stats():
    """Calculate dashboard statistics"""
    return {
        "total_assets": len(ASSETS),
        "total_tokens": sum(a["sold"] for a in ASSETS),
        "total_value":  sum(a["valuation"] for a in ASSETS),
        "unique_holders": 347,
    }

# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.route("/")
def index():
    if is_logged_in():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ── AUTH ──

@app.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user     = USERS.get(email)
        if user and user["password"] == hash_password(password):
            session["user"] = email
            return redirect(url_for("dashboard"))
        error = "Invalid email or password. Please try again."
    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    if is_logged_in():
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        first  = request.form.get("first_name", "").strip()
        last   = request.form.get("last_name", "").strip()
        email  = request.form.get("email", "").strip()
        pw     = request.form.get("password", "")
        pw2    = request.form.get("confirm_password", "")
        wallet = request.form.get("wallet", "").strip()
        role   = request.form.get("role", "Asset Owner / Issuer")

        if not first or not last or not email or not pw:
            error = "All fields are required."
        elif pw != pw2:
            error = "Passwords do not match."
        elif email in USERS:
            error = "An account with this email already exists."
        else:
            USERS[email] = {
                "password":   hash_password(pw),
                "first_name": first,
                "last_name":  last,
                "wallet":     wallet or "Not connected",
                "role":       role,
            }
            session["user"] = email
            return redirect(url_for("dashboard"))
    return render_template("register.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── DASHBOARD ──

@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))
    stats = get_stats()
    return render_template("dashboard.html",
        user=get_current_user(),
        assets=ASSETS[:4],
        top_holders=TOP_HOLDERS,
        transactions=TRANSACTIONS[:3],
        stats=stats,
        active="dashboard"
    )


# ── DEFINE ASSET ──

@app.route("/define-asset", methods=["GET", "POST"])
def define_asset():
    if not is_logged_in():
        return redirect(url_for("login"))
    success = None
    error   = None
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        atype    = request.form.get("type", "")
        location = request.form.get("location", "").strip()
        val_str  = request.form.get("valuation", "0").replace(",","").replace("$","")
        desc     = request.form.get("description", "").strip()
        try:
            valuation = float(val_str)
        except ValueError:
            valuation = 0
        if not name or not location or valuation <= 0:
            error = "Please fill in all required fields with valid values."
        else:
            new_asset = {
                "id":         generate_asset_id(),
                "name":       name,
                "type":       atype,
                "location":   location,
                "valuation":  valuation,
                "token_name": name.replace(" ", "") + " Token",
                "symbol":     name[:3].upper(),
                "supply":     0,
                "sold":       0,
                "price":      0,
                "emoji":      "🏢",
                "color":      "#3B82F6",
                "status":     "Defined",
                "description": desc,
            }
            ASSETS.append(new_asset)
            success = f"Asset '{name}' successfully defined on-chain! Asset ID: {new_asset['id']}"
    return render_template("define_asset.html",
        user=get_current_user(),
        assets=ASSETS,
        success=success,
        error=error,
        active="define"
    )


# ── TOKENIZE ──

@app.route("/tokenize", methods=["GET", "POST"])
def tokenize():
    if not is_logged_in():
        return redirect(url_for("login"))
    success = None
    error   = None
    defined_assets = [a for a in ASSETS if a["supply"] == 0 or a["status"] == "Defined"]
    if request.method == "POST":
        asset_id    = request.form.get("asset_id")
        token_name  = request.form.get("token_name", "").strip()
        symbol      = request.form.get("symbol", "").strip().upper()
        supply_str  = request.form.get("supply", "0").replace(",","")
        price_str   = request.form.get("price", "0")
        try:
            supply = int(supply_str)
            price  = float(price_str)
        except ValueError:
            supply, price = 0, 0
        asset = next((a for a in ASSETS if a["id"] == asset_id), None)
        if not asset:
            error = "Asset not found. Please select a valid asset."
        elif supply <= 0 or price <= 0:
            error = "Supply and price must be greater than 0."
        elif not token_name or not symbol:
            error = "Token name and symbol are required."
        else:
            asset["token_name"] = token_name
            asset["symbol"]     = symbol
            asset["supply"]     = supply
            asset["price"]      = price
            asset["status"]     = "Active"
            tx_hash = generate_tx_hash()
            success = f"✓ {supply:,} {symbol} tokens minted successfully! TX: {tx_hash[:20]}..."
    return render_template("tokenize.html",
        user=get_current_user(),
        assets=ASSETS,
        defined_assets=defined_assets,
        success=success,
        error=error,
        active="tokenize"
    )


# ── TRANSFER / BUY / SELL ──

@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    if not is_logged_in():
        return redirect(url_for("login"))
    success = None
    error   = None
    if request.method == "POST":
        action    = request.form.get("action", "Buy")
        asset_id  = request.form.get("asset_id")
        recipient = request.form.get("recipient", "").strip()
        amount_s  = request.form.get("amount", "0").replace(",","")
        try:
            amount = int(amount_s)
        except ValueError:
            amount = 0
        asset = next((a for a in ASSETS if a["id"] == asset_id), None)
        if not asset:
            error = "Please select a valid asset."
        elif amount <= 0:
            error = "Token amount must be greater than 0."
        elif action in ("Buy", "Transfer") and not recipient:
            error = "Recipient address is required."
        else:
            value = amount * asset["price"]
            tx_hash = generate_tx_hash()
            tx = {
                "type":       action,
                "type_color": "#10B981" if action == "Buy" else "#EF4444" if action == "Sell" else "#3B82F6",
                "asset":      asset["name"],
                "symbol":     asset["symbol"],
                "from_addr":  get_current_user()["wallet"],
                "to_addr":    recipient or "self",
                "tokens":     f"{amount:,}",
                "value":      format_currency(value),
                "time":       "Just now",
                "tx_hash":    tx_hash,
            }
            TRANSACTIONS.insert(0, tx)
            if action == "Buy":
                asset["sold"] = min(asset["sold"] + amount, asset["supply"])
            success = f"✓ {action} of {amount:,} {asset['symbol']} confirmed! TX: {tx_hash[:20]}..."
    return render_template("transfer.html",
        user=get_current_user(),
        assets=ASSETS,
        transactions=TRANSACTIONS,
        success=success,
        error=error,
        active="transfer"
    )


# ── MARKETPLACE ──

@app.route("/marketplace")
def marketplace():
    if not is_logged_in():
        return redirect(url_for("login"))
    filter_type = request.args.get("type", "All")
    filtered = ASSETS if filter_type == "All" else [a for a in ASSETS if a["type"] == filter_type]
    asset_types = ["All"] + list(set(a["type"] for a in ASSETS))
    return render_template("marketplace.html",
        user=get_current_user(),
        assets=filtered,
        asset_types=asset_types,
        active_filter=filter_type,
        active="marketplace"
    )


# ── PORTFOLIO ──

@app.route("/portfolio")
def portfolio():
    if not is_logged_in():
        return redirect(url_for("login"))
    total_value   = 142400
    total_tokens  = sum(p["tokens"] for p in PORTFOLIO)
    total_gain    = 11840
    return render_template("portfolio.html",
        user=get_current_user(),
        portfolio=PORTFOLIO,
        total_value=total_value,
        total_tokens=total_tokens,
        total_gain=total_gain,
        active="portfolio"
    )


# ── TOP HOLDERS ──

@app.route("/top-holders")
def top_holders():
    if not is_logged_in():
        return redirect(url_for("login"))
    return render_template("top_holders.html",
        user=get_current_user(),
        holders=TOP_HOLDERS,
        active="top_holders"
    )


# ── TRANSACTIONS ──

@app.route("/transactions")
def transactions():
    if not is_logged_in():
        return redirect(url_for("login"))
    return render_template("transactions.html",
        user=get_current_user(),
        transactions=TRANSACTIONS,
        active="transactions"
    )


# ── NOTIFICATIONS ──

@app.route("/notifications")
def notifications():
    if not is_logged_in():
        return redirect(url_for("login"))
    unread_count = sum(1 for n in NOTIFICATIONS if n["unread"])
    return render_template("notifications.html",
        user=get_current_user(),
        notifications=NOTIFICATIONS,
        unread_count=unread_count,
        active="notifications"
    )


# ── PROFILE ──

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not is_logged_in():
        return redirect(url_for("login"))
    user   = get_current_user()
    success = None
    if request.method == "POST":
        email = session["user"]
        USERS[email]["first_name"] = request.form.get("first_name", user["first_name"])
        USERS[email]["last_name"]  = request.form.get("last_name",  user["last_name"])
        USERS[email]["wallet"]     = request.form.get("wallet",     user["wallet"])
        success = "Profile updated successfully!"
        user = get_current_user()
    return render_template("profile.html",
        user=user,
        success=success,
        total_assets=len(ASSETS),
        active="profile"
    )


# ── API ENDPOINTS (JSON) ──

@app.route("/api/assets")
def api_assets():
    return jsonify(ASSETS)

@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())

@app.route("/api/top-holders")
def api_top_holders():
    return jsonify(TOP_HOLDERS)


# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  AssetChain DApp - Running on http://127.0.0.1:5000")
    print("  Login: ashan@assetchain.io / password123")
    print("=" * 50)
    app.run(debug=True, port=5000)
