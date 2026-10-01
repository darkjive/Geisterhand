# Geisterhand

Steuert deinen Browser automatisch per KI-Agent mit [browser-use](https://github.com/browser-use/browser-use).

## Installation (lokal auf deinem Rechner)

```bash
git clone <dieses-repo> && cd Geisterhand
uv sync
cp .env.example .env      # OpenRouter-Key oder Ollama-Modell eintragen
```

> Wichtig: Der Agent muss auf dem Rechner laufen, auf dem dein Browser läuft.
> Eine Cloud-Session kann deinen lokalen Browser nicht steuern.

## LLM-Anbieter

In `.env` einstellen: `OPENROUTER_API_KEY` (Modell per `GEISTERHAND_MODEL`, Standard `anthropic/claude-sonnet-4.5`)
oder lokal mit Ollama: `GEISTERHAND_PROVIDER=ollama`, `GEISTERHAND_MODEL=<modell>`. Auch Anthropic, OpenAI
und browser-use Cloud gehen. Mit Ollama bleiben Seiteninhalte (z.B. Mails) auf deinem Rechner, kleine Modelle
steuern Browser aber deutlich schlechter.

## Schnellstart mit deinem Chrome und Logins

```bash
uv run geisterhand --login                 # einmalig: Chrome öffnet sich, bei deinen Seiten einloggen
uv run geisterhand --chrome "Aufgabe"      # ab dann: nutzt dieses Chrome inkl. gespeicherter Logins
```

`--chrome` startet Chrome mit Debug-Port und dem Profil `~/.geisterhand/chrome-profile`
(bzw. übernimmt es, falls es schon läuft). Die Logins bleiben dort dauerhaft gespeichert.
Dein normales Chrome-Standardprofil lässt sich nicht freigeben, weil Chrome 136+ den Debug-Port
dafür sperrt.

## Domains einschränken

Mit deinen Logins kann der Agent auf deinen Namen handeln. Beschränke ihn auf vertrauenswürdige Seiten:

```bash
uv run geisterhand --chrome --allow-domain github.com --allow-domain "*.github.com" "Zeige meine offenen PRs"
```

Ohne `--allow-domain` ist keine Einschränkung aktiv.

## Weitere Optionen

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
