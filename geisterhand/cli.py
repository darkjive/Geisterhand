"""Geisterhand: Browser per KI-Agent (browser-use) automatisch steuern."""
import argparse
import asyncio
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from dotenv import load_dotenv


def chrome_user_data_dir() -> str:
    system = platform.system()
    if system == "Darwin":
        return os.path.expanduser("~/Library/Application Support/Google/Chrome")
    if system == "Windows":
        return os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    return os.path.expanduser("~/.config/google-chrome")


CDP_PORT = 9222
CDP_URL = f"http://127.0.0.1:{CDP_PORT}"
# Eigenes Profil: Chrome 136+ erlaubt den Debug-Port nicht für das Standardprofil.
# Einmal einloggen, danach bleiben die Logins hier gespeichert.
GH_PROFILE_DIR = Path.home() / ".geisterhand" / "chrome-profile"


def find_chrome() -> str | None:
    system = platform.system()
    if system == "Darwin":
        cands = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    elif system == "Windows":
        roots = [os.environ.get(k, "") for k in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA")]
        cands = [os.path.join(r, r"Google\Chrome\Application\chrome.exe") for r in roots if r]
    else:
        cands = [shutil.which(n) or "" for n in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")]
    return next((c for c in cands if c and os.path.exists(c)), None)


def cdp_alive(url: str = CDP_URL) -> bool:
    try:
        urllib.request.urlopen(f"{url}/json/version", timeout=1)
        return True
    except Exception:
        return False


def ensure_chrome(chrome_path: str | None = None) -> str:
    """Startet Chrome mit Debug-Port und Geisterhand-Profil, falls nicht schon aktiv."""
    if cdp_alive():
        return CDP_URL
    exe = chrome_path or find_chrome()
    if not exe:
        sys.exit("Chrome nicht gefunden. Pfad mit --chrome-path angeben.")
    GH_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.Popen(
        [exe, f"--remote-debugging-port={CDP_PORT}", f"--user-data-dir={GH_PROFILE_DIR}",
         "--no-first-run", "--no-default-browser-check"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        if cdp_alive():
            return CDP_URL
        time.sleep(0.5)
    sys.exit("Chrome startete nicht mit Debug-Port. Läuft evtl. schon eine Chrome-Instanz mit diesem Profil?")


def make_llm():
    from browser_use import ChatAnthropic, ChatBrowserUse, ChatOpenAI

    if os.getenv("ANTHROPIC_API_KEY"):
        return ChatAnthropic(model=os.getenv("GEISTERHAND_MODEL", "claude-sonnet-4-5"))
    if os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model=os.getenv("GEISTERHAND_MODEL", "gpt-4.1"))
    if os.getenv("BROWSER_USE_API_KEY"):
        return ChatBrowserUse()
    sys.exit("Kein API-Key gefunden. Setze ANTHROPIC_API_KEY, OPENAI_API_KEY oder BROWSER_USE_API_KEY (siehe .env.example).")


def make_browser(args):
    from browser_use import Browser

    if args.cdp_url:  # laufenden Chrome übernehmen
        return Browser(cdp_url=args.cdp_url, keep_alive=True)
    if args.chrome:  # eigenes Geisterhand-Chrome (mit gespeicherten Logins) starten/übernehmen
        return Browser(cdp_url=ensure_chrome(args.chrome_path), keep_alive=True)
    if args.profile:  # eigenes Chrome-Profil (Logins, Cookies) -> Chrome vorher schließen!
        return Browser(
            executable_path=args.chrome_path or None,
            user_data_dir=chrome_user_data_dir(),
            profile_directory=args.profile,
            headless=False,
        )
    return Browser(headless=args.headless)  # frische, isolierte Instanz


async def run(args):
    from browser_use import Agent

    agent = Agent(task=args.task, llm=make_llm(), browser=make_browser(args))
    history = await agent.run(max_steps=args.max_steps)
    print("\n=== Ergebnis ===\n" + (history.final_result() or "(kein Ergebnis)"))


def main():
    load_dotenv()
    p = argparse.ArgumentParser(prog="geisterhand", description=__doc__)
    p.add_argument("task", nargs="?", default=None, help='Aufgabe, z.B. "Suche auf Google nach ..."')
    g = p.add_mutually_exclusive_group()
    g.add_argument("--cdp-url", default=os.getenv("CHROME_CDP_URL"),
                   help="Laufenden Chrome übernehmen, z.B. http://localhost:9222")
    g.add_argument("--chrome", action="store_true",
                   help="Chrome mit dauerhaftem Geisterhand-Profil nutzen (empfohlen, Logins bleiben erhalten)")
    g.add_argument("--profile", help='Chrome-Profil nutzen, z.B. "Default" (Chrome vorher schließen)')
    p.add_argument("--chrome-path", help="Pfad zur Chrome-Binary (optional)")
    p.add_argument("--headless", action="store_true", help="Ohne sichtbares Fenster (nur frische Instanz)")
    p.add_argument("--max-steps", type=int, default=50)
    p.add_argument("--login", action="store_true",
                   help="Nur Chrome öffnen, damit du dich einmalig bei deinen Seiten einloggen kannst")
    args = p.parse_args()
    if args.login:
        ensure_chrome(args.chrome_path)
        print(f"Chrome läuft. Logge dich jetzt bei deinen Seiten ein (Profil: {GH_PROFILE_DIR}).")
        return
    if not args.task:
        p.error("Aufgabe fehlt")
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
