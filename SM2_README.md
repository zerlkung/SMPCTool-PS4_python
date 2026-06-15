# SMPS2Tool — Marvel's Spider-Man 2 (PS5/PC) 🕷️🕸️

**Spider-Man 2 Asset Tool** — for extracting, translating, and injecting assets into Marvel's Spider-Man 2 (PS5/PC).

Uses the **I29 TOC format** (same as Ratchet & Clank: Rift Apart). Single-file Python 3.

---

## What Works

| Feature | Status |
|---|---|
| TOC parsing (225 archives, 1.4M assets) | ✅ |
| Extract assets (font, localization, any) | ✅ |
| loc-export (92,760 strings → CSV) | ✅ |
| loc-import (CSV → .loc) | ✅ |
| Patch/inject assets into archive | ✅ |
| Font replacement (TTF/OTF) | ✅ |

## What's Different from SM1/MM

| | SM1/MM | SM2 |
|---|---|---|
| TOC magic | 0xAF12AF77 / 0x34E89035 | 0x34E89035 |
| Compression | zlib | none (raw DAT1) |
| Archive names | flat / 72-byte stride | 66-byte stride (ASCII) |
| SizeEntry | chain AssetID→Size→Offset | direct (size, arch_idx, offset, flags) |
| Font format | GFX/Scaleform | **TTF/OTF** |
| Loc format | LZ4 + DAT1 / LZ4 raw | direct DAT1 (no wrapper) |
| Loc sections | 4-9 | 9 |
| Strings | 54K / 34K / 56K | **92,760** |

## Unknowns

- Which language slot the game reads (need to test in-game: 0, 1, 2...)
- DAG compression algorithm (Oodle? not needed — use hashes.txt from ModdingTool)
- Full section mapping for all 8 TOC sections

## Quick Start

```bash
# Setup: put hashes.txt from ModdingTool in project root
# https://www.nexusmods.com/marvelsspiderman2/mods/32

# TOC info
python smps2tool.py --toc "SM2_PS5\toc" info

# Extract font (Azbuka Pro Medium Italic, TTF)
python smps2tool.py --toc "SM2_PS5\toc" extract --archive-dir "SM2_PS5" --id 0x8143F7F3648B4470 --output extracted/

# Extract localization (first language slot = English)
python smps2tool.py --toc "SM2_PS5\toc" extract --archive-dir "SM2_PS5" --id 0xBE55D94F171BF8DE --output extracted/

# Export to CSV
python smps2tool.py loc-export extracted/localization_all.localization strings.csv

# Translate: edit strings.csv → fill translation column → save as UTF-8

# Import CSV → .loc
python smps2tool.py loc-import extracted/localization_all.localization strings.csv modified.loc

# Inject back (slot 0 — try 0,1,2 until game shows translation)
python smps2tool.py --toc "SM2_PS5\toc" patch --archive-dir "SM2_PS5" --files "0xBE55D94F171BF8DE=modified.loc" --asset-index 0 --output-toc "SM2_PS5\toc.new"

# Inject font
python smps2tool.py --toc "SM2_PS5\toc" patch --archive-dir "SM2_PS5" --files "0x8143F7F3648B4470=font.ttf" --output-toc "SM2_PS5\toc.new"
```

## Fonts (22 in d\userinterface)

| Hash | Name | Size | Format |
|---|---|---|---|
| `0x8143F7F3648B4470` | Azbuka Pro Medium Italic | 173 KB | TTF |
| — | Azbuka Pro | 172 KB | TTF |
| — | Azbuka Pro Bold | 173 KB | TTF |
| — | Azbuka Pro Medium | 170 KB | TTF |
| — | Azbuka Pro Black | 181 KB | TTF |
| — | Neue Frutiger World Medium | 286 KB | TTF |
| — | Neue Frutiger World Bold | 283 KB | TTF |
| — | CJK font | 22 MB | TTF |
| — | Japanese (Morisawa) | 4.2 MB | OTF |

- **Latin text**: replace `0x8143F7F3648B4470` (Azbuka Pro Medium Italic)
- **UI/HUD**: replace Neue Frutiger World fonts
- **Edit fonts** with FontForge — SM2 uses standard TTF/OTF (no GFX conversion needed!)

## Known Asset Hashes

| Asset | Hash |
|---|---|
| Localization (all languages) | `0xBE55D94F171BF8DE` |
| Font (Azbuka Pro Medium Italic) | `0x8143F7F3648B4470` |

## Credits

- **[Overstrike / ModdingTool](https://github.com/Tkachov/Overstrike)** — TOC format reverse-engineering, hashes database
- **[ModdingTool on Nexus Mods](https://www.nexusmods.com/marvelsspiderman2/mods/32)** — SM2 asset extraction GUI
- **[jedijosh920](https://www.nexusmods.com/marvelsspidermanremastered/mods/51)** — Original SMPCTool (PC)
- **[team-waldo / akintos](https://github.com/team-waldo/InsomniacArchive)** — DAT1 section IDs, localization format
- `smps4tool.py` / `smps5tool.py` — codebase this tool builds upon
