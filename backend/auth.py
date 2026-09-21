"""
Accounts and sessions.

Two kinds of user. A candidate signs up and gets a ghost. A company signs up
and gets a balance. Either way the browser keeps one token and sends it on
every request as X-Token. Logging in issues a new token, which quietly logs
out any other browser.

Passwords are never stored. A salted PBKDF2 hash is, using only the standard
library, so there is nothing extra to install and nothing clever to get wrong.
"""

import hashlib
import secrets

import db
import ghosts

UNMASK_PRICE_PKR = 1500
DEMO_TOPUP_PKR = 10000


# ── Passwords ────────────────────────────────────────────────────────────

def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return salt + "$" + digest.hex()


def check_password(password, stored):
    salt, digest = stored.split("$", 1)
    attempt = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return secrets.compare_digest(attempt.hex(), digest)


# ── Sessions ─────────────────────────────────────────────────────────────

def session_for(user):
    """What the browser keeps. Enough to draw the nav without another call."""
    out = {
        "token": user["token"],
        "user_id": user["id"],
        "role": user["role"],
        "email": user["email"],
        "name": user["company_name"] if user["role"] == "company" else "",
        "balance_pkr": user["balance_pkr"],
        "ghost_id": "",
    }
    if user["role"] == "candidate":
        g = ghosts.for_user(user["id"])
        if g:
            out["name"] = g["name"]
            out["ghost_id"] = g["ghost_id"]
    return out


def issue_token(user_id):
    token = secrets.token_urlsafe(32)
    db.execute("UPDATE users SET token = %s WHERE id = %s", (token, user_id))
    return token


def by_token(token):
    if not token:
        return None
    rows = db.query("SELECT * FROM users WHERE token = %s", (token,))
    return rows[0] if rows else None


def by_email(email):
    rows = db.query("SELECT * FROM users WHERE email = %s", (email.strip().lower(),))
    return rows[0] if rows else None


# ── Sign up and log in ───────────────────────────────────────────────────

def signup(email, password, role, company_name=""):
    """Returns a session, or a string saying what went wrong."""
    email = email.strip().lower()
    if "@" not in email or len(email) < 5:
        return "that does not look like an email"
    if len(password) < 6:
        return "use at least six characters"
    if role not in ("candidate", "company"):
        return "role must be candidate or company"
    if role == "company" and not company_name.strip():
        return "a company needs a name"
    if by_email(email):
        return "that email already has an account"

    user_id = db.execute(
        "INSERT INTO users (email, password_hash, role, company_name)"
        " VALUES (%s, %s, %s, %s) RETURNING id",
        (email, hash_password(password), role, company_name.strip()),
    )
    if role == "candidate":
        ghosts.create(user_id)

    issue_token(user_id)
    return session_for(by_email(email))


def login(email, password):
    user = by_email(email)
    if not user or not check_password(password, user["password_hash"]):
        return "wrong email or password"
    issue_token(user["id"])
    return session_for(by_email(email))


def logout(user_id):
    db.execute("UPDATE users SET token = NULL WHERE id = %s", (user_id,))


# ── Money ────────────────────────────────────────────────────────────────

def charge(user_id, amount):
    """Take rupees off a company. False if they do not have enough."""
    rows = db.query("SELECT balance_pkr FROM users WHERE id = %s", (user_id,))
    if not rows or rows[0]["balance_pkr"] < amount:
        return False
    db.execute(
        "UPDATE users SET balance_pkr = balance_pkr - %s WHERE id = %s",
        (amount, user_id),
    )
    return True


def topup(user_id, amount):
    db.execute(
        "UPDATE users SET balance_pkr = balance_pkr + %s WHERE id = %s",
        (amount, user_id),
    )
