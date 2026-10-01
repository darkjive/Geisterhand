"""Geisterhand: Browser per KI-Agent (browser-use) automatisch steuern."""
import argparse
import asyncio
import os
import platform
import sys

from dotenv import load_dotenv


def chrome_user_data_dir() -> str:
    system = platform.system()
    if system == "Darwin":
        return os.path.expanduser("~/Library/Application Support/Google/Chrome")
    if system == "Windows":
        return os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    return os.path.expanduser("~/.config/google-chrome")


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
    p.add_argument("task", help='Aufgabe, z.B. "Suche auf Google nach ..."')
    g = p.add_mutually_exclusive_group()
    g.add_argument("--cdp-url", default=os.getenv("CHROME_CDP_URL"),
                   help="Laufenden Chrome übernehmen, z.B. http://localhost:9222")
    g.add_argument("--profile", help='Chrome-Profil nutzen, z.B. "Default" (Chrome vorher schließen)')
    p.add_argument("--chrome-path", help="Pfad zur Chrome-Binary (optional)")
    p.add_argument("--headless", action="store_true", help="Ohne sichtbares Fenster (nur frische Instanz)")
    p.add_argument("--max-steps", type=int, default=50)
    asyncio.run(run(p.parse_args()))


if __name__ == "__main__":
    main()
