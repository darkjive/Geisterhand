# Geisterhand

Steuert deinen Browser automatisch per KI-Agent mit [browser-use](https://github.com/browser-use/browser-use).

## Installation (lokal auf deinem Rechner)

```bash
git clone <dieses-repo> && cd Geisterhand
uv sync
cp .env.example .env      # API-Key eintragen
```

> Wichtig: Der Agent muss auf dem Rechner laufen, auf dem dein Browser läuft.
> Eine Cloud-Session kann deinen lokalen Browser nicht steuern.

## Nutzung

```bash
# 1) Frische, isolierte Browser-Instanz
uv run geisterhand "Öffne news.ycombinator.com und nenne die Top 3 Titel"

# 2) Dein laufenden Chrome übernehmen (inkl. Logins)
#    Chrome zuerst mit Debug-Port starten:
#    macOS:   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=$HOME/.chrome-geisterhand
#    Linux:   google-chrome --remote-debugging-port=9222 --user-data-dir=$HOME/.chrome-geisterhand
#    Windows: chrome.exe --remote-debugging-port=9222 --user-data-dir=%USERPROFILE%\.chrome-geisterhand
uv run geisterhand --cdp-url http://localhost:9222 "Prüfe meinen Posteingang"

# 3) Dein bestehendes Chrome-Profil (Chrome vorher komplett schließen)
uv run geisterhand --profile Default "..."
```

Neueres Chrome (136+) erlaubt den Debug-Port nur mit eigenem `--user-data-dir`; logge dich dort einmal ein.
