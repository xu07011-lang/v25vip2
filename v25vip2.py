import threading
import base64
import os
import time
import re
import requests
import socket
import sys
from time import sleep
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
from collections import Counter, defaultdict
from urllib.parse import urlparse, parse_qs
import random
import math

# Imports from get_device_id.py
import platform
import subprocess
import hashlib

# Check and install necessary libraries
try:
    from faker import Faker
    from requests import session
    from colorama import Fore, Style
    import pystyle
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.style import Style
    from rich.text import Text
except ImportError:
    os.system("pip install faker requests colorama bs4 pystyle rich")
    os.system("pip3 install requests pysocks")
    print('__Vui Lòng Chạy Lại Tool__')
    sys.exit()

# =====================================================================================
# CONFIGURATION FOR VIP KEY
# =====================================================================================
VIP_KEY_URL = "https://raw.githubusercontent.com/DUONGKP2401/KEY-VIP.txt/main/KEY-VIP.txt"
VIP_CACHE_FILE = 'vip_cache.json'
# =====================================================================================

# Encrypt and decrypt data using base64
def encrypt_data(data):
    return base64.b64encode(data.encode()).decode()

def decrypt_data(encrypted_data):
    return base64.b64decode(encrypted_data.encode()).decode()

# Colors for display
xnhac = "\033[1;36m"
do = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
xduong = "\033[1;34m"
hong = "\033[1;35m"
trang = "\033[1;39m"
end = '\033[0m'

def banner():
    os.system("cls" if os.name == "nt" else "clear")
    banner_text = f"""
{luc}████████╗ ██████╗░░ ██╗░░██╗░
{luc}╚══██╔══╝ ██╔══██╗░ ██║██╔╝░░
{luc}░░░██║░░░ ██║░░██║░ █████╔╝░░
{luc}░░░██║░░░ ██║░░██║░ ██╔═██╗░░
{luc}░░░██║░░░ ██║░░██║░ ██║░╚██╗░
{luc}░░░╚═╝░░░ ╚█████╔╝░ ╚═╝░░╚═╝░
{trang}══════════════════════════

{vang}Admin: DUONG PHUNG
{vang}Nhóm Zalo: https://zalo.me/g/ddxsyp497
{vang}Tele: @tankeko12
{trang}══════════════════════════
"""
    for char in banner_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        sleep(0.0001)

# =====================================================================================
# DEVICE ID AND IP ADDRESS FUNCTIONS
# =====================================================================================
def get_device_id():
    """Generates a stable device ID based on CPU information."""
    system = platform.system()
    try:
        if system == "Windows":
            cpu_info = subprocess.check_output('wmic cpu get ProcessorId', shell=True, text=True, stderr=subprocess.DEVNULL)
            cpu_info = ''.join(line.strip() for line in cpu_info.splitlines() if line.strip() and "ProcessorId" not in line)
        else:
            try:
                cpu_info = subprocess.check_output("cat /proc/cpuinfo", shell=True, text=True)
            except:
                cpu_info = platform.processor()
        if not cpu_info:
            cpu_info = platform.processor()
    except Exception:
        cpu_info = "Unknown"

    hash_hex = hashlib.sha256(cpu_info.encode()).hexdigest()
    only_digits = re.sub(r'\D', '', hash_hex)
    if len(only_digits) < 16:
        only_digits = (only_digits * 3)[:16]
    
    return f"DEVICE-{only_digits[:16]}"

def get_ip_address():
    """Gets the user's public IP address."""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip_data = response.json()
        return ip_data.get('ip')
    except Exception as e:
        print(f"{do}Lỗi khi lấy địa chỉ IP: {e}{trang}")
        return None

def display_machine_info(ip_address, device_id):
    """Displays the banner, IP address, and Device ID."""
    banner()
    if ip_address:
        print(f"{trang}[{do}<>{trang}] {do}Địa chỉ IP: {vang}{ip_address}{trang}")
    else:
        print(f"{do}Không thể lấy địa chỉ IP của thiết bị.{trang}")
    
    if device_id:
        print(f"{trang}[{do}<>{trang}] {do}Mã Máy: {vang}{device_id}{trang}")
    else:
        print(f"{do}Không thể lấy Mã Máy của thiết bị.{trang}")

# =====================================================================================
# VIP KEY HANDLING FUNCTIONS
# =====================================================================================

def save_vip_key_info(device_id, key, expiration_date_str):
    """Saves VIP key information to a local cache file."""
    data = {'device_id': device_id, 'key': key, 'expiration_date': expiration_date_str}
    encrypted_data = encrypt_data(json.dumps(data))
    with open(VIP_CACHE_FILE, 'w') as file:
        file.write(encrypted_data)
    print(f"{luc}Đã lưu thông tin Key VIP cho lần đăng nhập sau.{trang}")

def load_vip_key_info():
    """Loads VIP key information from the local cache file."""
    try:
        with open(VIP_CACHE_FILE, 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return None

def display_remaining_time(expiry_date_str):
    """Calculates and displays the remaining time for a VIP key."""
    try:
        expiry_date = datetime.strptime(expiry_date_str, '%d/%m/%Y').replace(hour=23, minute=59, second=59)
        now = datetime.now()
        
        if expiry_date > now:
            delta = expiry_date - now
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            print(f"{xnhac}Key VIP của bạn còn lại: {luc}{days} ngày, {hours} giờ, {minutes} phút.{trang}")
        else:
            print(f"{do}Key VIP của bạn đã hết hạn.{trang}")
    except ValueError:
        print(f"{vang}Không thể xác định ngày hết hạn của key.{trang}")

def check_vip_key(machine_id, user_key):
    """
    Checks the VIP key from the URL on GitHub.
    Returns:
        (status, expiration_date_str): Tuple containing status and expiry date string.
    """
    print(f"{vang}Đang kiểm tra Key VIP...{trang}")
    try:
        response = requests.get(VIP_KEY_URL, timeout=10)
        if response.status_code != 200:
            print(f"{do}Lỗi: Không thể tải danh sách key. Vui lòng liên hệ admin.{trang}")
            return 'error', None

        key_list = response.text.strip().split('\n')
        for line in key_list:
            parts = line.strip().split('|')
            if len(parts) >= 4:
                key_ma_may, key_value, _, key_ngay_het_han = parts
                
                if key_ma_may == machine_id and key_value == user_key:
                    try:
                        expiry_date = datetime.strptime(key_ngay_het_han, '%d/%m/%Y')
                        if expiry_date.date() >= datetime.now().date():
                            return 'valid', key_ngay_het_han
                        else:
                            return 'expired', None
                    except ValueError:
                        continue
        return 'not_found', None
    except requests.exceptions.RequestException as e:
        print(f"{do}Lỗi kết nối hoặc không tìm thấy máy chủ. Vui lòng kiểm tra lại mạng.{trang}")
        return 'error', None

# =====================================================================================
# MAIN AUTHENTICATION FLOW
# =====================================================================================
def main_authentication():
    ip_address = get_ip_address()
    device_id = get_device_id()
    display_machine_info(ip_address, device_id)

    if not ip_address or not device_id:
        print(f"{do}Không thể lấy thông tin thiết bị cần thiết. Vui lòng kiểm tra kết nối mạng.{trang}")
        return False

    cached_vip_info = load_vip_key_info()
    if cached_vip_info and cached_vip_info.get('device_id') == device_id:
        try:
            expiry_date = datetime.strptime(cached_vip_info['expiration_date'], '%d/%m/%Y')
            if expiry_date.date() >= datetime.now().date():
                print(f"{luc}Đã tìm thấy Key VIP hợp lệ, tự động đăng nhập...{trang}")
                display_remaining_time(cached_vip_info['expiration_date'])
                sleep(3)
                return True
            else:
                print(f"{vang}Key VIP đã lưu đã hết hạn. Vui lòng nhập key mới.{trang}")
        except (ValueError, KeyError):
            print(f"{do}Lỗi file lưu key. Vui lòng nhập lại key.{trang}")

    while True:
        try:
            print(f"{trang}═══════════════════════════════════")
            vip_key_input = input(f'{trang}[{do}<>{trang}] {vang}Vui lòng nhập Key VIP của bạn: {luc}')
            
            if not vip_key_input:
                print(f"{vang}Key không được để trống. Vui lòng nhập lại.{trang}")
                continue

            status, expiry_date_str = check_vip_key(device_id, vip_key_input)
            
            if status == 'valid':
                print(f"{luc}Xác thực Key VIP thành công!{trang}")
                save_vip_key_info(device_id, vip_key_input, expiry_date_str)
                display_remaining_time(expiry_date_str)
                sleep(3)
                return True
            elif status == 'expired':
                print(f"{do}Key VIP của bạn đã hết hạn. Vui lòng liên hệ admin.{trang}")
            elif status == 'not_found':
                print(f"{do}Key VIP không hợp lệ hoặc không tồn tại cho mã máy này.{trang}")
            else: # status == 'error'
                print(f"{do}Đã xảy ra lỗi trong quá trình xác thực. Vui lòng thử lại.{trang}")
            
            sleep(2)

        except KeyboardInterrupt:
            print(f"\n{trang}[{do}<>{trang}] {do}Cảm ơn bạn đã dùng Tool !!!{trang}")
            sys.exit()

# SECTION 1: UI & UTILITIES
# ==============================================================================
console = Console()
STYLE_SUCCESS, STYLE_ERROR, STYLE_WARNING, STYLE_INFO, STYLE_HEADER, STYLE_VALUE = \
    Style(color="green"), Style(color="red"), Style(color="yellow"), Style(color="cyan"), \
    Style(color="magenta", bold=True), Style(color="blue", bold=True)

def clear_console(): os.system("cls" if os.name == "nt" else "clear")
def show_header():
    header = Text("Tool Xworld Vua thoát hiểm V2.5S - admin: DUONG PHUNG nhóm zalo: https://zalo.me/g/ddxsyp497  telegram: @tankeko12 -Lưu ý : Hãy quản lí vốn thật tốt; không tham lam, biết điểm dừng. Chúc bạn dùng tool vui vẻ!!", style=STYLE_HEADER, justify="center")
    console.print(Panel(header, border_style="magenta", expand=False)); console.print()

# ==============================================================================
# SECTION 2: CONFIGURATION
# ==============================================================================
CONFIG_FILE = "config.json"
def load_or_create_config():
    if os.path.exists(CONFIG_FILE):
        if console.input(f"🔎 Đã tìm thấy file config. Dùng lại? ([bold green]Y[/bold green]/n): ").strip().lower() in ["y", "yes", ""]:
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # Thêm kiểm tra các key mới cần thiết nếu có
                    if all(k in config for k in ["stop_profit", "stop_loss", "max_lose_streak", "play_rounds", "pause_rounds"]):
                        # Đảm bảo cờ cho tính năng mới luôn tồn tại
                        if "random_skip_after_loss" not in config:
                            config["random_skip_after_loss"] = True
                        return config
            except (json.JSONDecodeError, KeyError):
                console.print("⚠️ File config bị lỗi hoặc không hợp lệ. Vui lòng tạo mới.", style=STYLE_WARNING)

    console.print("⚠️ Không tìm thấy config hoặc config cũ. Vui lòng tạo mới.", style=STYLE_WARNING)
    config = {
        "url_game": console.input(f"[{STYLE_INFO}]Nhập Link Game:[/] ").strip(),
        "bet_type": console.input(f"[{STYLE_INFO}]Nhập Loại Tiền cược (BUILD/USDT/WORLD):[/] ").strip().upper(),
        "base_bet": float(console.input(f"[{STYLE_INFO}]Nhập Số Tiền Cược cơ bản:[/] ").strip()),
        "multiplier": float(console.input(f"[{STYLE_INFO}]Nhập Cấp số nhân sau khi thua:[/] ").strip()),
        "max_lose_streak": int(console.input(f"[{STYLE_WARNING}]Nhập Giới hạn chuỗi thua để DỪNG/RESET (ví dụ: 5):[/] ").strip()),
        "stop_profit": float(console.input(f"[{STYLE_SUCCESS}]Nhập Số LÃI mục tiêu để DỪNG (ví dụ: 50):[/] ").strip()),
        "stop_loss": float(console.input(f"[{STYLE_ERROR}]Nhập Mức LỖ tối đa để DỪNG (ví dụ: 100):[/] ").strip()),
        "random_skip_after_loss": True # THÊM CỜ CHO CƠ CHẾ NGHỈ RANDOM
    }

    while True:
        try:
            config["play_rounds"] = int(console.input(f"[{STYLE_INFO}]Nhập số ván muốn chơi trước khi tạm nghỉ (nhập 0 để chơi liên tục):[/] ").strip())
            config["pause_rounds"] = int(console.input(f"[{STYLE_INFO}]Nhập số ván muốn nghỉ sau mỗi phiên:[/] ").strip())
            if config["play_rounds"] > 0 and config["pause_rounds"] <= 0:
                console.print("🔥 Nếu đã cài số ván chơi, số ván nghỉ phải lớn hơn 0. Vui lòng nhập lại.", style=STYLE_WARNING)
                continue
            if config["play_rounds"] < 0 or config["pause_rounds"] < 0:
                 console.print("🔥 Vui lòng nhập số dương.", style=STYLE_WARNING)
                 continue
            break
        except ValueError:
            console.print("🔥 Vui lòng nhập một số hợp lệ.", style=STYLE_ERROR)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(config, f, indent=4)
    console.print(f"✅ Đã lưu config vào file [bold cyan]{CONFIG_FILE}[/bold cyan]", style=STYLE_SUCCESS)
    return config

# ==============================================================================
# SECTION 3: PREDICTION LOGIC (Adaptive Strategy Engine)
# ==============================================================================
def choose_safe_room(recent_100, lose_streak=0, last_win_room=None, user_id=None, issue_id=None):
    """
    Phân tích và chọn phòng cho lần cược ĐẦU TIÊN.
    """
    full_history = [int(r["killed_room_id"]) for r in recent_100 if "killed_room_id" in r] if isinstance(recent_100, list) else []
    if len(full_history) < 20:
        # Nếu lịch sử quá ngắn, chọn ngẫu nhiên
        return random.randint(1, 8)

    last_killed = full_history[0]

    if lose_streak >= 2:
        console.print("🟡 [bold yellow]Chuỗi thua >= 2. Dùng chiến lược [Phòng thủ] cho cược đầu...[/bold yellow]")
        candidates = set(range(1, 9))
        candidates.discard(last_killed)
        candidates -= set(full_history[:5]) # Loại 5 phòng gần nhất
        hot_rooms = {r for r, c in Counter(full_history[:15]).items() if c >= 2} # Loại phòng nổ 2 lần trong 15 ván
        candidates -= hot_rooms
        if candidates:
            # Chọn phòng có khoảng cách nổ xa nhất trong các phòng an toàn
            gaps = {r: full_history.index(r) if r in full_history else 100 for r in candidates}
            return max(gaps, key=gaps.get)

    console.print("🟢 [bold green]Trạng thái ổn định. Dùng chiến lược [Phân tích] cho cược đầu...[/bold green]")
    candidates = set(range(1, 9))
    candidates.discard(last_killed)
    
    if not candidates:
        candidates = set(range(1, 9)); candidates.discard(last_killed)

    # Chọn phòng có khoảng cách nổ xa nhất
    gaps = {r: full_history.index(r) if r in full_history else 100 for r in candidates}
    return max(gaps, key=gaps.get)

def choose_different_room_for_final_bet(recent_100, initial_room):
    """
    Luôn luôn chọn một phòng KHÁC với phòng ban đầu.
    Sau đó mới áp dụng phân tích an toàn trên các phòng còn lại.
    """
    full_history = [int(r["killed_room_id"]) for r in recent_100 if "killed_room_id" in r] if isinstance(recent_100, list) else []
    
    candidate_rooms = set(range(1, 9))
    candidate_rooms.discard(initial_room)
    
    if not full_history:
        return random.choice(list(candidate_rooms))

    last_killed = full_history[0]
    candidate_rooms.discard(last_killed)
    
    if len(candidate_rooms) == 1:
        return candidate_rooms.pop()
    
    if not candidate_rooms:
        fallback_rooms = set(range(1, 9))
        fallback_rooms.discard(initial_room)
        return random.choice(list(fallback_rooms))

    counts_12 = Counter(full_history[:12])
    hot_rooms = {r for r, c in counts_12.items() if c >= 2}
    safe_candidates = candidate_rooms - hot_rooms
    
    if safe_candidates:
        gaps = {r: full_history.index(r) if r in full_history else 100 for r in safe_candidates}
        return max(gaps, key=gaps.get)
    else:
        gaps = {r: full_history.index(r) if r in full_history else 100 for r in candidate_rooms}
        return max(gaps, key=gaps.get)

# ==============================================================================
# SECTION 4: API & DATA HANDLING
# ==============================================================================
def make_api_request(session, method, url, max_retries=3, **kwargs):
    base_delay = 1
    for attempt in range(max_retries):
        time.sleep(random.uniform(0.3, 0.7))
        try:
            response = session.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            if attempt == max_retries - 1: return None
            time.sleep((base_delay * 2 ** attempt) + random.uniform(0.5, 1.0))
    return None

def get_wallet_balance(session, url, bet_type):
    resp = make_api_request(session, "GET", url)
    if not resp or resp.get("code") not in [0, 200]: return None
    wallet = resp.get("data", {}).get("cwallet")
    if wallet is None: return None
    key_map = {"USDT": "ctoken_kusdt", "WORLD": "ctoken_kther", "BUILD": "ctoken_contribute"}
    balance_str = wallet.get(key_map.get(bet_type))
    return float(balance_str) if balance_str is not None else None

def display_summary(session_state, round_data, config, room_names_map):
    BET_TYPE, MAX_LOSE_STREAK = config["bet_type"], config["max_lose_streak"]
    win_rate = (session_state['wins'] / (session_state['wins'] + session_state['losses']) * 100) if (session_state['wins'] + session_state['losses']) > 0 else 0
    
    summary_table = Table(title=f"[bold]Tóm Tắt Vòng {session_state['round']}[/]", show_header=True, header_style="bold magenta")
    summary_table.add_column("Chỉ số", width=15); summary_table.add_column("Thống kê")
    summary_table.add_row("Ván đấu", f"#{round_data.get('issue_id', 'N/A')}")
    summary_table.add_row("Hành động", round_data.get('action', Text("---")))
    if round_data.get('result'):
        killed_room_id = round_data['result'].get('killed_room_id', 'N/A')
        killed_room_name = room_names_map.get(str(killed_room_id), '?')
        summary_table.add_row("Phòng Sát Thủ", f"{killed_room_id} ({killed_room_name})")
    
    if round_data.get('final_balance') is not None:
        summary_table.add_row("Số dư Hiện tại", f"{round_data.get('final_balance', 0):.4f} {BET_TYPE}")

    summary_table.add_row("Kết quả", round_data.get('outcome', Text("---")))
    summary_table.add_row("Tiền cược", f"{round_data.get('bet_amount', 0):.4f} {BET_TYPE}")
    profit_text = Text(f"{round_data.get('round_profit', 0):+.4f}", style=STYLE_SUCCESS if round_data.get('round_profit', 0) >= 0 else STYLE_ERROR)
    summary_table.add_row("Lời/Lỗ Vòng", profit_text)
    total_profit_text = Text(f"{session_state.get('cumulative_profit', 0):+.4f}", style=STYLE_SUCCESS if session_state.get('cumulative_profit', 0) >= 0 else STYLE_ERROR)
    summary_table.add_row("Tổng Lời/Lỗ", total_profit_text)
    summary_table.add_row("Thắng/Thua", f"{session_state['wins']}/{session_state['losses']} ({win_rate:.2f}%)")
    summary_table.add_row("Chuỗi thắng", f"{session_state['win_streak']} (Max: {session_state['max_win_streak']})")
    
    lose_streak_text = Text(f"{session_state['lose_streak']}", style=STYLE_ERROR)
    if session_state.get('rounds_to_skip_after_loss', 0) > 0:
         lose_streak_text = Text(f"{session_state['lose_streak']} (Nghỉ: {session_state['rounds_to_skip_after_loss']})", style=Style(color="yellow", bold=True))
         
    summary_table.add_row("Chuỗi thua", f"{lose_streak_text}/{MAX_LOSE_STREAK}")
    console.print(summary_table); console.print("-" * 60)

# ==============================================================================
# SECTION 5: MAIN LOGIC
# ==============================================================================
def main():
    if not main_authentication():
        print("\n\033[1;31mXác thực thất bại. Thoát chương trình.")
        sys.exit()
    
    print("\n\033[1;32mĐăng nhập thành công! Bắt đầu chạy chức năng chính của tool...")
    
    clear_console(); show_header(); config = load_or_create_config()
    try:
        params = parse_qs(urlparse(config["url_game"]).query)
        user_id, secret_key = params.get("userId", [None])[0], params.get("secretKey", [None])[0]
        if not user_id or not secret_key: raise ValueError("Invalid Link")
    except (ValueError, IndexError, TypeError):
        console.print("[red]LỖI: Link game không hợp lệ.[/red]"); return

    BET_TYPE, BASE_BET, MULTIPLIER, STOP_PROFIT, STOP_LOSS, MAX_LOSE_STREAK, PLAY_ROUNDS, PAUSE_ROUNDS = \
        config["bet_type"], config["base_bet"], config["multiplier"], \
        config["stop_profit"], config["stop_loss"], config["max_lose_streak"], \
        config["play_rounds"], config["pause_rounds"]
    RANDOM_SKIP_AFTER_LOSS = config.get("random_skip_after_loss", False) # Lấy cờ cho tính năng mới
    
    ROUND_DURATION = 48 

    ROOM_NAMES = {"1":"Nhà Kho", "2":"Phòng Họp", "3":"PhGĐ", "4":"PhTròChuyện", "5":"PhGiámSát", "6":"VănPhòng", "7":"PhTàiVụ", "8":"PhNhânSự"}

    API_BASE = "https://api.escapemaster.net/escape_game"
    URL_USER_INFO = "https://user.3games.io/user/regist?is_cwallet=1"
    URL_BET = f"{API_BASE}/bet"
    URL_RECENT_10 = f"{API_BASE}/recent_10_issues?asset={BET_TYPE}"
    URL_RECENT_100 = f"{API_BASE}/recent_issues?limit=100&asset={BET_TYPE}"
    
    title = "[bold cyan]Cấu Hình Hoạt Động[/]"
    play_pause_text = f"Chơi {PLAY_ROUNDS} ván, nghỉ {PAUSE_ROUNDS} ván" if PLAY_ROUNDS > 0 else "Chơi liên tục"
    random_skip_text = "Có (2-5 ván)" if RANDOM_SKIP_AFTER_LOSS else "Không"
    text = (f"Loại Tiền Cược : {BET_TYPE}\nCược Cơ Bản    : {BASE_BET}\nCấp số nhân    : x{MULTIPLIER}\n"
            f"Chế độ chơi     : {play_pause_text}\n"
            f"Nghỉ sau thua   : {random_skip_text}\n"
            f"[yellow]Giới hạn thua   : {MAX_LOSE_STREAK} ván[/yellow]\n"
            f"[green]Mục tiêu Lãi   : +{STOP_PROFIT}[/green]\n[red]Ngưỡng Cắt Lỗ  : -{STOP_LOSS}[/red]")
    console.print(Panel(Text(text, style="white"), title=title, border_style="cyan", expand=False))

    api_session = requests.Session()
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    ]
    api_session.headers.update({"user-id": user_id, "user-secret-key": secret_key, "user-agent": random.choice(USER_AGENTS)})
    
    console.print("🔄 [italic]Đang quét số dư ban đầu làm mốc...[/italic]")
    initial_balance = get_wallet_balance(api_session, URL_USER_INFO, BET_TYPE)
    if initial_balance is None:
        console.print("❌ [red]Không thể lấy số dư ban đầu. Vui lòng kiểm tra lại Link Game và kết nối.[/red]"); return
    console.print(f"✅ [green]Số dư ban đầu được ghi nhận: [bold]{initial_balance:.4f} {BET_TYPE}[/bold][/green]\n")
    
    session_state = { 
        "round": 0, "wins": 0, "losses": 0, "cumulative_profit": 0.0, "lose_streak": 0, 
        "win_streak": 0, "max_win_streak": 0, "last_known_issue_id": None, "last_bet_on": None, 
        "balance_before_bet": initial_balance, "initial_balance": initial_balance, 
        "rounds_played_this_session": 0, "rounds_to_skip": 0, 
        "rounds_to_skip_after_loss": 0, # BIẾN MỚI CHO CƠ CHẾ NGHỈ RANDOM SAU THUA
        "last_win_room": None,
        "current_bet_amount": BASE_BET,
        "last_initial_bet_amount": BASE_BET
    }

    while True:
        try:
            resp10 = make_api_request(api_session, "GET", URL_RECENT_10)
            if not resp10 or not resp10.get("data"):
                console.print("[yellow]Không thể lấy lịch sử 10 ván, đang chờ...[/yellow]", end="\r"); time.sleep(5); continue
            
            latest_result = resp10["data"][0]
            latest_issue_id = str(latest_result.get("issue_id"))

            if latest_issue_id != session_state["last_known_issue_id"]:
                round_start_time = time.time()
                session_state["round"] += 1
                console.print(f"\n--- Vòng {session_state['round']}: Xử lý kết quả ván #{latest_issue_id} ---", style="bold yellow")
                
                round_data = {"issue_id": latest_issue_id, "bet_amount": 0, "round_profit": 0, "result": latest_result, "action": Text("---"), "outcome": Text("Không cược", style="dim")}
                last_bet = session_state.get("last_bet_on")
                
                if last_bet and str(last_bet["issue_id"]) == latest_issue_id:
                    if PLAY_ROUNDS > 0: session_state["rounds_played_this_session"] += 1
                    killed_room_id = latest_result.get("killed_room_id")

                    # Lấy tổng tiền cược từ state đã lưu
                    final_bet_room, total_bet_for_round, balance_before = last_bet['room'], last_bet['amount'], session_state['balance_before_bet']
                    round_data["bet_amount"] = total_bet_for_round

                    console.print("[cyan]... Chờ máy chủ cập nhật số dư ...[/cyan]", end="\r"); time.sleep(4)
                    final_balance = get_wallet_balance(api_session, URL_USER_INFO, BET_TYPE)
                    console.print(" " * 60, end="\r")
                    
                    is_win = (killed_room_id is not None and int(killed_room_id) != int(final_bet_room))
                    
                    if is_win:
                        round_data["outcome"] = Text("THẮNG", style=STYLE_SUCCESS)
                        session_state.update({"wins": session_state["wins"]+1, "lose_streak": 0, "win_streak": session_state["win_streak"]+1, "last_win_room": final_bet_room})
                        session_state["max_win_streak"] = max(session_state["max_win_streak"], session_state["win_streak"])
                        session_state["current_bet_amount"] = BASE_BET
                        session_state["rounds_to_skip_after_loss"] = 0 # Reset nghỉ sau thua
                        
                        # Tính lợi nhuận dựa trên số dư thực tế hoặc tính toán dự phòng
                        round_profit = (final_balance - balance_before) if final_balance is not None and balance_before is not None else (total_bet_for_round - last_bet['initial_amount']) * 0.95 - last_bet['initial_amount']

                    else: # THUA
                        round_data["outcome"] = Text("THUA", style=STYLE_ERROR)
                        session_state.update({"losses": session_state["losses"]+1, "lose_streak": session_state["lose_streak"]+1, "win_streak": 0})
                        session_state["current_bet_amount"] = session_state["last_initial_bet_amount"] * MULTIPLIER
                        
                        # Tiền lỗ là tổng của cả 2 lần cược
                        round_profit = -(total_bet_for_round)
                        
                        # --- CƠ CHẾ NGHỈ RANDOM SAU THUA 1 VÁN (YÊU CẦU MỚI) ---
                        if session_state["lose_streak"] == 1 and RANDOM_SKIP_AFTER_LOSS:
                            skip_count = random.randint(2, 5) # Ngẫu nhiên 2 đến 5 ván
                            session_state["rounds_to_skip_after_loss"] = skip_count
                            console.print(f"⚠️ [bold yellow]THUA VÁN ĐẦU![/bold yellow] Kích hoạt cơ chế nghỉ ngẫu nhiên: [bold magenta]Nghỉ {skip_count} ván[/bold magenta] để bảo toàn vốn.")

                    
                    session_state["cumulative_profit"] = (final_balance - session_state["initial_balance"]) if final_balance is not None else session_state["cumulative_profit"] + round_profit
                    
                    # Tạo văn bản hành động để hiển thị cả 2 lần cược
                    initial_room_display = last_bet["initial_room"]
                    final_room_display = last_bet["room"]
                    action_text = Text(f"Cược: P.{initial_room_display} -> P.{final_room_display} ({ROOM_NAMES.get(str(final_room_display), '?')})", style=STYLE_INFO)
                    
                    round_data.update({ "action": action_text, "round_profit": round_profit, "final_balance": final_balance })
                
                display_summary(session_state, round_data, config, ROOM_NAMES)
                
                # KIỂM TRA GIỚI HẠN THUA
                if 0 < MAX_LOSE_STREAK <= session_state['lose_streak']:
                    console.print(Panel(f"BẠN ĐÃ THUA LIÊN TIẾP {session_state['lose_streak']} VÁN!", title="[bold yellow]ĐẠT GIỚI HẠN CHUỖI THUA[/bold yellow]", border_style="yellow"))
                    choice = console.input("Bạn muốn [bold green]Chơi tiếp[/bold green] (reset tiền cược) hay [bold red]Nghỉ[/bold red]? (mặc định là Chơi tiếp) [C/N]: ").strip().lower()
                    if choice in ['n', 'nghi']: console.print("[yellow]Bot đã dừng theo yêu cầu của người dùng.[/yellow]"); return
                    else: 
                        session_state['lose_streak'] = 0
                        session_state["current_bet_amount"] = BASE_BET
                        session_state["rounds_to_skip_after_loss"] = 0 # Reset nghỉ sau thua
                        console.print("[green]Đã reset chuỗi thua và tiền cược về mức ban đầu. Tiếp tục chơi...[/green]\n")

                # KIỂM TRA MỤC TIÊU/CẮT LỖ
                if session_state['cumulative_profit'] >= STOP_PROFIT: console.print(Panel(f"✅ ĐÃ ĐẠT MỤC TIÊU LỢI NHUẬN! (Tổng lãi: {session_state['cumulative_profit']:.4f} {BET_TYPE})", title="[bold green]DỪNG TOOL[/bold green]", border_style="green")); return
                if session_state['cumulative_profit'] <= -STOP_LOSS: console.print(Panel(f"❌ ĐÃ CHẠM NGƯỠNG CẮT LỖ! (Tổng lỗ: {session_state['cumulative_profit']:.4f} {BET_TYPE})", title="[bold red]DỪNG TOOL[/bold red]", border_style="red")); return

                session_state["last_known_issue_id"] = latest_issue_id
                next_round_id = int(latest_issue_id) + 1
                
                # BỎ QUA VÁN ĐẦU TIÊN
                if session_state["round"] <= 3:
                    console.print(f"🧐 Ván {session_state['round']}/3: Đang chờ và phân tích chu kỳ đầu. Bỏ qua cược.")
                    session_state["last_bet_on"] = None; time.sleep(5); continue
                
                # NGHỈ SAU MỘT SỐ VÁN CHƠI THEO CẤU HÌNH (PAUSE_ROUNDS)
                if PLAY_ROUNDS > 0 and session_state["rounds_played_this_session"] >= PLAY_ROUNDS:
                    console.print(Panel(f"Đã hoàn thành {session_state['rounds_played_this_session']} ván. Bắt đầu nghỉ {PAUSE_ROUNDS} ván.", title="[bold cyan]TẠM NGHỈ[/bold cyan]", border_style="cyan"))
                    session_state["rounds_to_skip"] = PAUSE_ROUNDS; session_state["rounds_played_this_session"] = 0

                if session_state["rounds_to_skip"] > 0:
                    console.print(f"😴 [yellow]Đang trong thời gian nghỉ theo cấu hình. Còn lại [bold]{session_state['rounds_to_skip']}[/bold] ván nghỉ...[/yellow]")
                    session_state["rounds_to_skip"] -= 1; session_state["last_bet_on"] = None; time.sleep(5); continue

                # --- NGHỈ SAU THUA 1 VÁN (CƠ CHẾ MỚI) ---
                if session_state["rounds_to_skip_after_loss"] > 0:
                    console.print(f"😴 [yellow]Đang trong thời gian nghỉ sau thua. Còn lại [bold]{session_state['rounds_to_skip_after_loss']}[/bold] ván nghỉ...[/yellow]")
                    session_state["rounds_to_skip_after_loss"] -= 1; session_state["last_bet_on"] = None; time.sleep(5); continue
                
                current_balance = get_wallet_balance(api_session, URL_USER_INFO, BET_TYPE)
                if current_balance is None:
                    console.print(f"⚠️ Không thể xác minh số dư, tạm bỏ qua ván #{next_round_id} để đảm bảo an toàn.", style=STYLE_WARNING); session_state["last_bet_on"] = None; time.sleep(10); continue
                
                session_state['balance_before_bet'] = current_balance
                console.print(f"💰 Số dư hiện tại: [bold green]{current_balance:.4f} {BET_TYPE}[/bold green] | Chuẩn bị cho ván: [bold]#{next_round_id}[/bold]")
                
                resp100 = make_api_request(api_session, "GET", URL_RECENT_100)
                recent_100_hist = resp100.get("data") if resp100 and resp100.get("data") else []
                
                # ==============================================================================
                # LOGIC CƯỢC 2 LẦN (ĐÃ SỬA)
                # ==============================================================================
                
                # --- CƯỢC LẦN 1: CƯỢC BAN ĐẦU ---
                initial_room_choice = choose_safe_room(recent_100_hist, session_state['lose_streak'])
                initial_bet_amount = round(session_state["current_bet_amount"], 4)
                session_state["last_initial_bet_amount"] = initial_bet_amount

                # Kiểm tra số dư cho TỔNG CỘNG 2 lần cược
                total_required_for_round = initial_bet_amount + 0.1
                if total_required_for_round > current_balance:
                    console.print(f"⚠️ Không đủ số dư ({current_balance:.4f}). Cần {total_required_for_round:.4f} cho cả 2 lần cược. Bỏ qua ván.", style=STYLE_WARNING)
                    session_state["last_bet_on"] = None
                    continue
                
                console.print(f"🎯 [bold]Cược Lần 1:[/bold] Cược [bold blue]{initial_bet_amount:.4f} {BET_TYPE}[/bold blue] vào phòng [bold blue]{initial_room_choice} ({ROOM_NAMES.get(str(initial_room_choice), '?')})[/bold blue] cho ván [bold]#{next_round_id}[/bold]...")
                bet1_payload = { "asset_type": BET_TYPE, "user_id": int(user_id), "room_id": initial_room_choice, "bet_amount": initial_bet_amount }
                bet1_response = make_api_request(api_session, "POST", URL_BET, json=bet1_payload)

                if not (bet1_response and bet1_response.get("code") == 0):
                    console.print(f"❌ Cược lần 1 thất bại! Phản hồi: {bet1_response}", style="red")
                    session_state["last_bet_on"] = None
                    continue
                
                console.print("✅ Cược lần 1 thành công. Chờ 15 giây để đổi phòng...", style="green")
                time.sleep(15)

                # --- CƯỢC LẦN 2: CƯỢC CUỐI CÙNG ĐỂ ĐỔI PHÒNG (CỐ ĐỊNH 0.1) ---
                final_bet_amount = 0.1
                # Phân tích lại để chọn phòng tốt nhất, khác với phòng ban đầu
                final_room_choice = choose_different_room_for_final_bet(recent_100_hist, initial_room_choice)

                console.print(f"🎯 [bold]Cược Lần 2 (Chốt):[/bold] Đổi sang phòng [bold magenta]{final_room_choice} ({ROOM_NAMES.get(str(final_room_choice), '?')})[/bold magenta] với [bold magenta]{final_bet_amount:.1f} {BET_TYPE}[/bold magenta]...")
                bet2_payload = { "asset_type": BET_TYPE, "user_id": int(user_id), "room_id": final_room_choice, "bet_amount": final_bet_amount }
                bet2_response = make_api_request(api_session, "POST", URL_BET, json=bet2_payload)

                if not (bet2_response and bet2_response.get("code") == 0):
                    console.print(f"❌ Cược lần 2 thất bại! Phản hồi: {bet2_response}. Kết quả ván này có thể không chính xác.", style="red")
                    session_state["last_bet_on"] = None # Coi như không cược để an toàn
                    continue

                console.print("✅ Cược lần 2 thành công. Chốt kèo!", style="green")

                # Lưu thông tin cược cuối cùng để xử lý kết quả ở vòng lặp sau
                total_bet_for_round = initial_bet_amount + final_bet_amount
                session_state["last_bet_on"] = {
                    "issue_id": next_round_id, 
                    "room": final_room_choice,              # Kết quả tính theo phòng cuối cùng
                    "amount": total_bet_for_round,         # Tổng tiền cược cho việc tính Lời/Lỗ
                    "initial_room": initial_room_choice,     # Lưu phòng ban đầu để hiển thị
                    "initial_amount": initial_bet_amount   # Lưu cược đầu để tính P/L dự phòng
                }
                # ==============================================================================

            else:
                next_issue_id_to_wait_for = int(latest_issue_id) + 1
                console.print(f"🔄 [yellow]... Chờ kết quả ván #{next_issue_id_to_wait_for} ...[/yellow]", end="\r")
                time.sleep(3)
        except Exception as e:
            console.print(f"\n[red]Gặp lỗi trong vòng lặp chính: {e}. Đang thử lại sau 10 giây...[/red]"); time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\nBot đã dừng bởi người dùng.", style="bold yellow")
    except Exception as e:
        console.print(f"\nĐã xảy ra lỗi không mong muốn:", style=STYLE_ERROR)
        console.print_exception(show_locals=False)
