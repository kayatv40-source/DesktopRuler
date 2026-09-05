from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    import customtkinter as ctk
except ImportError as exc:
    raise SystemExit(
        "CustomTkinter kurulu değil. Komut satırında şu komutu çalıştırın: pip install customtkinter"
    ) from exc


# ============================================================
# AYARLAR VE DİL SEÇENEKLERİ
# ============================================================

APP_NAME = "Desktop Ruler"
APP_DIR = Path(os.getenv("APPDATA", Path.home())) / "DesktopRuler"
DB_PATH = APP_DIR / "desktop_ruler.db"
APP_DIR.mkdir(parents=True, exist_ok=True)

COLORS = {
    "background": "#0f1117",
    "background_light": "#171a23",
    "card": "#1d2230",
    "card_hover": "#252c3d",
    "primary": "#3b82f6",
    "primary_hover": "#2563eb",
    "secondary": "#303746",
    "secondary_hover": "#3b4558",
    "text": "#f5f7fb",
    "text_secondary": "#9ca7b8",
    "success": "#35c98a",
    "danger": "#ff5d73",
    "warning": "#f0b429",
    "border": "#2c3444",
}

TRANSLATIONS = {
    "TR": {
        "login_title": "Giriş Yap",
        "login_sub": "Devam etmek için hesabınızla giriş yapın.",
        "register_title": "Hoş Geldiniz",
        "register_sub": "İlk kullanım için Desktop Ruler hesabınızı oluşturun.",
        "username_ph": "Kullanıcı adı",
        "password_ph": "Şifre",
        "login_btn": "Giriş Yap",
        "register_btn": "Hesap Oluştur",
        "apps_title": "Uygulamalar",
        "search_ph": "Uygulama ara…",
        "refresh_btn": "⟳ Yenile",
        "logout_btn": "Çıkış",
        "not_found": "Aramanızla eşleşen uygulama bulunamadı.\nMasaüstündeki .lnk, .url veya .exe dosyaları taranır.",
        "theme_dark": "Karanlık",
        "theme_light": "Aydınlık",
        "theme_custom": "Özel Renk Seç",
        "developed_by": "Developed by Mergen Studios",
        "preparing": "Hazırlanıyor…",
        "app_count": "uygulama",
        "user_err_short": "Kullanıcı adı en az 3 karakter olmalı.",
        "user_err_long": "Kullanıcı adı en fazla 32 karakter olabilir.",
        "user_err_char": "Kullanıcı adı sadece harf, sayı ve _ içerebilir.",
        "pass_err": "Şifre en az 6 karakter olmalı.",
        "reg_exist": "Bu kullanıcı adı zaten kullanılıyor.",
        "reg_success": "Hesap başarıyla oluşturuldu.",
        "log_fail": "Kullanıcı adı veya şifre hatalı.",
        "log_success": "Giriş başarılı.",
        "launch_fail": "Uygulama veya kısayol artık mevcut değil.",
        "launch_ok": "Uygulama başlatıldı.",
        "too_many": "Çok fazla başarısız deneme.",
        "wait_sec": "sn sonra tekrar deneyin.",
        "wait_10": "10 saniye bekleyin.",
        "subtitle": "Uygulamalarınız.\nTek bir panelde."
    },
    "EN": {
        "login_title": "Login",
        "login_sub": "Log in with your account to continue.",
        "register_title": "Welcome",
        "register_sub": "Create your Desktop Ruler account for first use.",
        "username_ph": "Username",
        "password_ph": "Password",
        "login_btn": "Login",
        "register_btn": "Create Account",
        "apps_title": "Applications",
        "search_ph": "Search apps…",
        "refresh_btn": "⟳ Refresh",
        "logout_btn": "Logout",
        "not_found": "No application found matching your search.\nScans .lnk, .url, or .exe files on desktop.",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "theme_custom": "Custom Color",
        "developed_by": "Developed by Mergen Studios",
        "preparing": "Preparing…",
        "app_count": "apps",
        "user_err_short": "Username must be at least 3 characters.",
        "user_err_long": "Username cannot exceed 32 characters.",
        "user_err_char": "Username can only contain letters, numbers, and _.",
        "pass_err": "Password must be at least 6 characters.",
        "reg_exist": "This username is already taken.",
        "reg_success": "Account created successfully.",
        "log_fail": "Invalid username or password.",
        "log_success": "Login successful.",
        "launch_fail": "Application or shortcut no longer exists.",
        "launch_ok": "Application launched.",
        "too_many": "Too many failed attempts.",
        "wait_sec": "sec to try again.",
        "wait_10": "Wait 10 seconds.",
        "subtitle": "Your applications.\nIn a single panel."
    },
    "RU": {
        "login_title": "Войти",
        "login_sub": "Войдите в свою учетную запись, чтобы продолжить.",
        "register_title": "Добро пожаловать",
        "register_sub": "Создайте учетную запись Desktop Ruler для первого использования.",
        "username_ph": "Имя пользователя",
        "password_ph": "Пароль",
        "login_btn": "Войти",
        "register_btn": "Создать аккаунт",
        "apps_title": "Приложения",
        "search_ph": "Поиск приложений…",
        "refresh_btn": "⟳ Обновить",
        "logout_btn": "Выйти",
        "not_found": "Приложение не найдено.\nСканируются файлы .lnk, .url, .exe на рабочем столе.",
        "theme_dark": "Темная",
        "theme_light": "Светлая",
        "theme_custom": "Свой цвет",
        "developed_by": "Разработано Mergen Studios",
        "preparing": "Подготовка…",
        "app_count": "приложений",
        "user_err_short": "Имя пользователя должно содержать не менее 3 символов.",
        "user_err_long": "Имя пользователя не может превышать 32 символа.",
        "user_err_char": "Имя пользователя может содержать только буквы, цифры и _.",
        "pass_err": "Пароль должен содержать не менее 6 символов.",
        "reg_exist": "Это имя пользователя уже занято.",
        "reg_success": "Аккаунт успешно создан.",
        "log_fail": "Неверное имя пользователя или пароль.",
        "log_success": "Успешный вход.",
        "launch_fail": "Приложение или ярлык больше не существует.",
        "launch_ok": "Приложение запущено.",
        "too_many": "Слишком много неудачных попыток.",
        "wait_sec": "сек. до следующей попытки.",
        "wait_10": "Подождите 10 секунд.",
        "subtitle": "Ваши приложения.\nВ одной панели."
    }
}

# ============================================================
# VERİTABANI / HESAP SİSTEMİ
# ============================================================

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        conn.commit()

def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 180_000
    ).hex()

def user_exists() -> bool:
    with get_connection() as conn:
        row = conn.execute("SELECT 1 FROM users LIMIT 1").fetchone()
    return row is not None

def register_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()

    if len(username) < 3: return False, "user_err_short"
    if len(username) > 32: return False, "user_err_long"
    if not username.replace("_", "").isalnum(): return False, "user_err_char"
    if len(password) < 6: return False, "pass_err"

    salt = secrets.token_bytes(16)
    password_hash = _hash_password(password, salt)

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, salt, created_at) VALUES (?, ?, ?, ?)",
                (username, password_hash, salt.hex(), time.time()),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        return False, "reg_exist"

    return True, "reg_success"

def login_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT username, password_hash, salt FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    if row is None:
        return False, "log_fail"

    salt = bytes.fromhex(row["salt"])
    password_hash = _hash_password(password, salt)

    if secrets.compare_digest(password_hash, row["password_hash"]):
        return True, "log_success"
    return False, "log_fail"


# ============================================================
# UYGULAMA TARAYICI
# ============================================================

def _windows_desktop() -> Path:
    desktop = Path.home() / "Desktop"
    if desktop.exists():
        return desktop

    one_drive = os.getenv("OneDrive")
    if one_drive:
        candidate = Path(one_drive) / "Desktop"
        if candidate.exists():
            return candidate

    return desktop

def _start_menu_dirs() -> list[Path]:
    dirs: list[Path] = []
    program_data = os.getenv("ProgramData")
    app_data = os.getenv("APPDATA")

    if program_data:
        dirs.append(Path(program_data) / "Microsoft" / "Windows" / "Start Menu" / "Programs")
    if app_data:
        dirs.append(Path(app_data) / "Microsoft" / "Windows" / "Start Menu" / "Programs")
    return [p for p in dirs if p.exists()]

def _display_name(path: Path) -> str:
    name = path.stem
    if name.endswith(" (1)"):
        name = name[:-4]
    return name.replace("_", " ").strip() or path.name

def _scan_directory(directory: Path, recursive: bool = False) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    try:
        entries = directory.rglob("*") if recursive else directory.iterdir()
        for path in entries:
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".lnk", ".url", ".exe"}:
                continue
            result.append(
                {"name": _display_name(path), "path": str(path)}
            )
    except (OSError, PermissionError):
        pass
    return result

def scan_desktop() -> list[dict[str, str]]:
    apps: dict[str, dict[str, str]] = {}

    desktop = _windows_desktop()
    for app in _scan_directory(desktop):
        apps[os.path.normcase(app["path"])] = app

    for start_dir in _start_menu_dirs():
        for app in _scan_directory(start_dir, recursive=True):
            apps.setdefault(os.path.normcase(app["path"]), app)

    sorted_apps = sorted(apps.values(), key=lambda x: x["name"].lower())
    return sorted_apps

_APPLICATIONS: list[dict[str, str]] = []

def get_applications() -> list[dict[str, str]]:
    return list(_APPLICATIONS)


# ============================================================
# UYGULAMA BAŞLATMA
# ============================================================

def launch_application(path: str) -> tuple[bool, str]:
    target = Path(path)
    if not target.exists():
        return False, "launch_fail"

    try:
        if os.name == "nt":
            os.startfile(str(target))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(target)])
        else:
            subprocess.Popen([str(target)], start_new_session=True)
        return True, "launch_ok"
    except (OSError, subprocess.SubprocessError) as exc:
        return False, "launch_fail"


# ============================================================
# ARAYÜZ
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DesktopRuler(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.current_lang = "TR"
        
        self.title(APP_NAME)
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(fg_color=COLORS["background"])

        self.failed_attempts = 0
        self.locked_until = 0.0
        self.current_apps: list[dict[str, str]] = []
        self.search_entry: ctk.CTkEntry | None = None
        self.apps_frame: ctk.CTkFrame | None = None
        self.status_label: ctk.CTkLabel | None = None

        self.protocol("WM_DELETE_WINDOW", self.close_application)
        self.show_login_screen()

    # ------------------------- DİL & TEMA -------------------------

    def t(self, key: str) -> str:
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS["TR"]).get(key, key)

    def change_language(self, new_lang: str) -> None:
        self.current_lang = new_lang
        if hasattr(self, "search_entry") and self.search_entry and self.search_entry.winfo_exists():
            self.show_dashboard(refresh=False)
        else:
            self.show_login_screen()

    def change_theme(self, choice: str) -> None:
        if choice in [self.t("theme_dark"), "Karanlık", "Dark", "Темная"]:
            ctk.set_appearance_mode("dark")
            COLORS["background"] = "#0f1117"
            COLORS["background_light"] = "#171a23"
            COLORS["card"] = "#1d2230"
            COLORS["card_hover"] = "#252c3d"
            COLORS["text"] = "#f5f7fb"
            COLORS["border"] = "#2c3444"
        elif choice in [self.t("theme_light"), "Aydınlık", "Light", "Светлая"]:
            ctk.set_appearance_mode("light")
            COLORS["background"] = "#f3f4f6"
            COLORS["background_light"] = "#e5e7eb"
            COLORS["card"] = "#ffffff"
            COLORS["card_hover"] = "#f9fafb"
            COLORS["text"] = "#111827"
            COLORS["border"] = "#d1d5db"
        else:
            from tkinter import colorchooser
            color_code = colorchooser.askcolor(title=self.t("theme_custom"), initialcolor=COLORS["primary"])[1]
            if color_code:
                COLORS["primary"] = color_code

        if hasattr(self, "search_entry") and self.search_entry and self.search_entry.winfo_exists():
            self.show_dashboard(refresh=False)
        else:
            self.show_login_screen()

    # ------------------------- GENEL -------------------------

    def clear_screen(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

    def _make_label(
        self,
        parent: Any,
        text: str,
        size: int = 14,
        bold: bool = False,
        color: str | None = None,
    ) -> ctk.CTkLabel:
        return ctk.CTkLabel(
            parent,
            text=text,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            text_color=color or COLORS["text"],
        )

    def _add_footer(self) -> None:
        footer = ctk.CTkFrame(self, fg_color="transparent", height=25)
        footer.pack(side="bottom", fill="x")
        self._make_label(footer, self.t("developed_by"), 11, color=COLORS["text_secondary"]).pack(pady=(2, 6))

    # ------------------------- LOGIN -------------------------

    def show_login_screen(self) -> None:
        self.clear_screen()
        self._add_footer()

        container = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0)
        container.pack(fill="both", expand=True)

        left = ctk.CTkFrame(container, fg_color=COLORS["background_light"], corner_radius=0, width=430)
        left.pack(side="left", fill="both")
        left.pack_propagate(False)

        logo = self._make_label(left, "◈", 72, True, COLORS["primary"])
        logo.pack(pady=(130, 5))
        title = self._make_label(left, APP_NAME, 32, True)
        title.pack()
        subtitle = self._make_label(left, self.t("subtitle"), 16, color=COLORS["text_secondary"])
        subtitle.pack(pady=15)

        right = ctk.CTkFrame(container, fg_color=COLORS["background"], corner_radius=0)
        right.pack(side="right", fill="both", expand=True)

        controls = ctk.CTkFrame(right, fg_color="transparent")
        controls.pack(side="top", anchor="ne", padx=20, pady=20)
        
        lang_values = ["TR", "EN", "RU"]
        self.lang_menu_login = ctk.CTkOptionMenu(
            controls, values=lang_values, command=self.change_language,
            width=70, height=30, fg_color=COLORS["secondary"], button_color=COLORS["secondary"], button_hover_color=COLORS["primary"]
        )
        self.lang_menu_login.set(self.current_lang)
        self.lang_menu_login.pack(side="right", padx=5)

        theme_keys = [self.t("theme_dark"), self.t("theme_light"), self.t("theme_custom")]
        self.theme_menu_login = ctk.CTkOptionMenu(
            controls, values=theme_keys, command=self.change_theme,
            width=100, height=30, fg_color=COLORS["secondary"], button_color=COLORS["secondary"], button_hover_color=COLORS["primary"]
        )
        current_theme = self.t("theme_dark") if ctk.get_appearance_mode() == "Dark" else self.t("theme_light")
        self.theme_menu_login.set(current_theme)
        self.theme_menu_login.pack(side="right", padx=5)

        form = ctk.CTkFrame(right, fg_color=COLORS["card"], corner_radius=20, border_width=1, border_color=COLORS["border"])
        form.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.72)

        if user_exists():
            self.show_login_form(form)
        else:
            self.show_register_form(form)

    def _build_auth_form(self, parent: ctk.CTkFrame, title_text: str, subtitle_text: str, button_text: str, command: Any) -> None:
        self._make_label(parent, title_text, 27, True).pack(pady=(48, 10))
        self._make_label(parent, subtitle_text, 13, color=COLORS["text_secondary"]).pack(pady=(0, 26))

        self.username_entry = ctk.CTkEntry(parent, placeholder_text=self.t("username_ph"), height=45, corner_radius=10)
        self.username_entry.pack(fill="x", padx=35, pady=8)

        self.password_entry = ctk.CTkEntry(parent, placeholder_text=self.t("password_ph"), show="•", height=45, corner_radius=10)
        self.password_entry.pack(fill="x", padx=35, pady=8)

        self.message_label = ctk.CTkLabel(parent, text="", wraplength=300)
        self.message_label.pack(pady=(5, 3))

        button = ctk.CTkButton(
            parent, text=button_text, height=45, corner_radius=10,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"], command=command
        )
        button.pack(fill="x", padx=35, pady=15)

        self.password_entry.bind("<Return>", lambda _event: command())
        self.username_entry.focus_set()

    def show_register_form(self, parent: ctk.CTkFrame) -> None:
        self._build_auth_form(parent, self.t("register_title"), self.t("register_sub"), self.t("register_btn"), self.register)

    def show_login_form(self, parent: ctk.CTkFrame) -> None:
        self._build_auth_form(parent, self.t("login_title"), self.t("login_sub"), self.t("login_btn"), self.login)

    def register(self) -> None:
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        success, msg_key = register_user(username, password)

        self.message_label.configure(
            text=self.t(msg_key),
            text_color=COLORS["success"] if success else COLORS["danger"],
        )
        if success:
            self.after(900, self.show_login_screen)

    def login(self) -> None:
        now = time.time()
        if now < self.locked_until:
            remaining = int(self.locked_until - now) + 1
            self.message_label.configure(
                text=f"{self.t('too_many')} {remaining} {self.t('wait_sec')}",
                text_color=COLORS["warning"],
            )
            return

        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        success, msg_key = login_user(username, password)

        if success:
            self.failed_attempts = 0
            self.show_dashboard()
            return

        self.failed_attempts += 1
        self.message_label.configure(text=self.t(msg_key), text_color=COLORS["danger"])

        if self.failed_attempts >= 5:
            self.failed_attempts = 0
            self.locked_until = time.time() + 10
            self.message_label.configure(text=f"{self.t('too_many')} {self.t('wait_10')}", text_color=COLORS["warning"])
            self.after(10000, lambda: None)

    # ------------------------- DASHBOARD -------------------------

    def show_dashboard(self, refresh: bool = True) -> None:
        self.clear_screen()
        self._add_footer()

        topbar = ctk.CTkFrame(self, height=76, fg_color=COLORS["background_light"], corner_radius=0, border_width=1, border_color=COLORS["border"])
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        self._make_label(topbar, "◈  Desktop Ruler", 24, True).pack(side="left", padx=28)

        exit_button = ctk.CTkButton(
            topbar, text=self.t("logout_btn"), width=75, height=36, corner_radius=9,
            fg_color="transparent", hover_color=COLORS["secondary"], border_width=1, border_color=COLORS["border"], command=self.show_login_screen
        )
        exit_button.pack(side="right", padx=(0, 16))

        refresh_button = ctk.CTkButton(
            topbar, text=self.t("refresh_btn"), width=100, height=36, corner_radius=9,
            fg_color=COLORS["secondary"], hover_color=COLORS["primary"], command=self.refresh_applications
        )
        refresh_button.pack(side="right", padx=8)

        lang_values = ["TR", "EN", "RU"]
        self.lang_menu_dash = ctk.CTkOptionMenu(
            topbar, values=lang_values, command=self.change_language,
            width=70, height=36, fg_color=COLORS["secondary"], button_color=COLORS["secondary"], button_hover_color=COLORS["primary"]
        )
        self.lang_menu_dash.set(self.current_lang)
        self.lang_menu_dash.pack(side="right", padx=8)

        theme_keys = [self.t("theme_dark"), self.t("theme_light"), self.t("theme_custom")]
        self.theme_menu_dash = ctk.CTkOptionMenu(
            topbar, values=theme_keys, command=self.change_theme,
            width=110, height=36, fg_color=COLORS["secondary"], button_color=COLORS["secondary"], button_hover_color=COLORS["primary"]
        )
        current_theme = self.t("theme_dark") if ctk.get_appearance_mode() == "Dark" else self.t("theme_light")
        self.theme_menu_dash.set(current_theme)
        self.theme_menu_dash.pack(side="right", padx=8)

        content = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0)
        content.pack(fill="both", expand=True, padx=24, pady=22)

        heading_row = ctk.CTkFrame(content, fg_color="transparent")
        heading_row.pack(fill="x", pady=(0, 14))

        title = self._make_label(heading_row, self.t("apps_title"), 28, True)
        title.pack(side="left")

        self.status_label = self._make_label(heading_row, self.t("preparing"), 13, color=COLORS["text_secondary"])
        self.status_label.pack(side="right", pady=(8, 0))

        search_row = ctk.CTkFrame(content, fg_color="transparent")
        search_row.pack(fill="x", pady=(0, 12))

        self.search_entry = ctk.CTkEntry(search_row, height=42, corner_radius=10, placeholder_text=self.t("search_ph"))
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", lambda _event: self.render_applications())

        self.apps_frame = ctk.CTkScrollableFrame(content, fg_color="transparent", corner_radius=12)
        self.apps_frame.pack(fill="both", expand=True)

        if refresh:
            self.refresh_applications()
        else:
            self.render_applications()

    def refresh_applications(self) -> None:
        global _APPLICATIONS
        _APPLICATIONS = scan_desktop()
        self.current_apps = list(_APPLICATIONS)
        self.render_applications()

    def render_applications(self) -> None:
        if self.apps_frame is None: return

        for widget in self.apps_frame.winfo_children():
            widget.destroy()

        query = self.search_entry.get().strip().lower() if self.search_entry else ""
        apps = [app for app in self.current_apps if query in app["name"].lower()]

        if self.status_label is not None:
            self.status_label.configure(
                text=f"{len(apps)} {self.t('app_count')}" + (f" / {len(self.current_apps)}" if query else "")
            )

        if not apps:
            empty = ctk.CTkFrame(self.apps_frame, fg_color=COLORS["card"], corner_radius=15)
            empty.pack(fill="x", padx=6, pady=25)
            self._make_label(empty, self.t("not_found"), 14, color=COLORS["text_secondary"]).pack(pady=30)
            return

        columns = 4
        for column in range(columns):
            self.apps_frame.grid_columnconfigure(column, weight=1)

        for index, app in enumerate(apps):
            row, column = divmod(index, columns)
            self.create_app_card(self.apps_frame, app, row, column)

    def create_app_card(self, parent: ctk.CTkFrame, app: dict[str, str], row: int, column: int) -> None:
        card = ctk.CTkFrame(parent, fg_color=COLORS["card"], corner_radius=15, border_width=1, border_color=COLORS["border"])
        card.grid(row=row, column=column, padx=7, pady=7, sticky="nsew")

        app_initial = app["name"][0].upper() if app["name"] else "?"
        icon = self._make_label(card, app_initial, 34, True, COLORS["primary"])
        icon.pack(pady=(18, 3))

        name = self._make_label(card, app["name"], 14, True)
        name.pack(padx=10)

        path_text = app["path"]
        short_path = path_text if len(path_text) <= 34 else "…" + path_text[-31:]
        path_label = self._make_label(card, short_path, 10, color=COLORS["text_secondary"])
        path_label.pack(padx=10, pady=(3, 14))

        def on_enter(_event: Any) -> None: card.configure(fg_color=COLORS["card_hover"])
        def on_leave(_event: Any) -> None: card.configure(fg_color=COLORS["card"])

        def on_click(_event: Any) -> None:
            ok, msg_key = launch_application(app["path"])
            if self.status_label is not None:
                self.status_label.configure(text=self.t(msg_key), text_color=COLORS["success"] if ok else COLORS["danger"])
                self.after(2500, lambda: self.status_label.configure(
                    text=f"{len(self.current_apps)} {self.t('app_count')}",
                    text_color=COLORS["text_secondary"],
                ) if self.status_label is not None and self.status_label.winfo_exists() else None)

        for widget in (card, icon, name, path_label):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

    def close_application(self) -> None:
        self.destroy()

# ============================================================
# BAŞLANGIÇ
# ============================================================

def main() -> None:
    initialize_database()
    app = DesktopRuler()
    app.mainloop()

if __name__ == "__main__":
    main()