# SM Tool — Spider-Man Asset Tool 🕷️

Python tool for extracting, translating, and injecting assets in Marvel's Spider-Man games.

> 🇹🇭 [ไทย / Thai](#ภาษาไทย) | 🚧 [Spider-Man 2 (WIP)](SM2_README.md)

---

## Quick Start

```bash
pip install lz4                                   # required for localization
python sm_tool.py                                  # GUI mode (recommended)
python sm_tool.py --game smr info --toc toc        # CLI mode
```

## Supported Games

| ID | Game | Tool | Stride | Strings |
|---|---|---|---|---|
| `sm1` | SM - PS4 | `sm1.py` | 24 | 54,010 |
| `mm` | MM - PS4 | `mm.py` | 72 | 34,079 |
| `smr` | SMR - PS5/PC | `smr.py` | 72 | 56,417 |
| `mm_ps5` | MM - PS5/PC | `smr.py` | 72 | 34,076 |
| `sm2` | SM2 - PS5 🚧 | `sm2.py` | 66 | 92,760 |

## GUI Usage

```
python sm_tool.py
```
1. Select game version
2. Browse TOC file + archive directory
3. Click: Extract Loc → Export CSV → translate → Import CSV → Patch Loc

**All patches output to `toc.new` — never overwrites original.**

## CLI Usage

```bash
# Extract font
python sm_tool.py --game smr --toc toc extract --archive-dir game/ --id 0xB1BC4746124FA7ED --output out/

# Extract localization
python sm_tool.py --game smr --toc toc extract --archive-dir game/ --id 0xBE55D94F171BF8DE --output out/

# Export/Import CSV
python sm_tool.py --game smr loc-export loc.localization strings.csv
python sm_tool.py --game smr loc-import loc.localization strings.csv modified.loc

# Patch (slot selection)
python sm_tool.py --game smr --toc toc patch --archive-dir game/ --files "0xBE55D94F171BF8DE=modified.loc" --asset-index 1 --output-toc toc.new
```

## Language Slot Reference

| Game | Active Slot | `--asset-index` |
|---|---|---|
| SM - PS4 | — | `--all-lang` (32 slots) |
| MM - PS4 | — | `--all-lang` (32 slots) |
| SMR - PS5/PC | 1 | `--asset-index 1` |
| MM - PS5/PC | 2 | `--asset-index 2` |
| SM2 - PS5 🚧 | ? | TBD |

## Key Asset Hashes

| Asset | Hash |
|---|---|
| Localization (all games) | `0xBE55D94F171BF8DE` |
| Font Latin (SM1, MM, SMR) | `0xB1BC4746124FA7ED` |
| Font Latin (SM2) | `0x8143F7F3648B4470` |

## Files

| File | Purpose |
|---|---|
| `sm_tool.py` | Unified GUI + CLI launcher |
| `sm1.py` | SM - PS4 backend |
| `mm.py` | MM - PS4 backend |
| `smr.py` | SMR + MM PS5/PC backend |
| `sm2.py` | SM2 - PS5 backend 🚧 |
| `fix_thai_chars.py` | Fix Thai tone mark errors |

## Credits

- [Overstrike / ModdingTool](https://github.com/Tkachov/Overstrike) — TOC format, hashes
- [SMPCTool-PS4](https://github.com/zerlkung/SMPCTool-PS4) — Original C# tool
- [team-waldo / InsomniacArchive](https://github.com/team-waldo/InsomniacArchive) — DAT1 format
- [jedijosh920](https://www.nexusmods.com/marvelsspidermanremastered/mods/51) — SMPCTool PC

---

# ภาษาไทย

## SM Tool — Spider-Man Asset Tool 🕷️

เครื่องมือ Python สำหรับ extract, แปลภาษา, และ inject ไฟล์เกม Marvel's Spider-Man

## เริ่มต้น

```bash
pip install lz4
python sm_tool.py                         # GUI (แนะนำ)
python sm_tool.py --game smr info --toc toc  # CLI
```

## เกมที่รองรับ

| ID | เกม | Tool |
|---|---|---|
| `sm1` | SM - PS4 | `sm1.py` |
| `mm` | MM - PS4 | `mm.py` |
| `smr` | SMR - PS5/PC | `smr.py` |
| `mm_ps5` | MM - PS5/PC | `smr.py` |
| `sm2` | SM2 - PS5 🚧 | `sm2.py` |

## การใช้งาน GUI

1. เลือกเกม → Browse TOC + archive folder
2. Extract Loc → Export CSV → แปลภาษาใน CSV (save UTF-8)
3. Import CSV → Patch Loc (output `toc.new`)

## Slot ที่เกมอ่าน

| เกม | Slot |
|---|---|
| SM, MM PS4 | `--all-lang` |
| SMR PS5/PC | `--asset-index 1` |
| MM PS5/PC | `--asset-index 2` |
| SM2 | รอทดสอบ |

## Credits

- [Overstrike / ModdingTool](https://github.com/Tkachov/Overstrike)
- [SMPCTool-PS4](https://github.com/zerlkung/SMPCTool-PS4)
- [team-waldo](https://github.com/team-waldo/InsomniacArchive)
- [jedijosh920](https://www.nexusmods.com/marvelsspidermanremastered/mods/51)
