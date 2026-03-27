# SMPCTool-PS4 Python 🕷️

**Spider-Man PS4 Asset Tool** — A Python rewrite of [SMPCTool-PS4](https://github.com/zerlkung/SMPCTool-PS4) (C#) for managing Marvel's Spider-Man game files on PS4.

Single-file, pure Python 3. Works as both a CLI tool and a Python library.

> 🇹🇭 [อ่านเป็นภาษาไทย / Thai version](#ภาษาไทย)

---

## Requirements

- Python 3.10+
- `lz4` — required for localization commands (`pip install lz4`)

---

## First-Time Setup

```bash
python3 smps4tool.py build-hashdb --dag dag    # run once (~12 sec, 44 MB)
python3 smps4tool.py info                       # verify
```

> The included `PS4AssetHashes.txt` is a pre-built hash DB (386,344 entries). You can skip build-hashdb if you already have it.

---

## Commands

### `extract` — Extract assets
```bash
python3 smps4tool.py extract --archive-dir /game --archive p000045 --output out/
python3 smps4tool.py extract --archive-dir /game --archive p000045 --output out/ --flat --skip-hex
```

Localization files with duplicate names (32 languages) are automatically detected from content and suffixed: `.en-US`, `.ja`, `.fr`, `.de`, `.ko`, `.es-LA`, `.pt-BR`, etc. (32/32 verified correct)

### `patch` — Replace specific assets (lightweight modding)
```bash
# Patch single file — creates small mod archive + new TOC
python3 smps4tool.py patch --archive-dir /game --mod-name mod_localization \
    --files "0xBE55D94F171BF8DE=modified.localization" --output-toc toc.new

# Patch multiple files at once
python3 smps4tool.py patch --archive-dir /game --mod-name mod_pack \
    --files "0xBE55D94F171BF8DE=new_loc.bin" "0xB1BC4746124FA7ED=new_font.gfx" \
    --output-toc toc.new
```

Creates a small archive with ONLY modified files, then patches the TOC to redirect those assets. All other 657,000+ assets remain untouched. No need to repack the entire archive.

### `repack` / `repack-dir` — Rebuild entire archive
```bash
# From original archive
python3 smps4tool.py repack --archive-dir /game --archive p000045 \
    --output-archive p000045_new --output-toc toc.new --skip-hex

# From extracted directory (modified files + fallback to original)
python3 smps4tool.py repack-dir --archive-dir /game --archive p000045 \
    --dir extracted/ --output-archive p000045_new --output-toc toc.new --flat
```

### `loc-export` / `loc-import` — Localization translation
```bash
# Export to CSV (54,010 strings)
python3 smps4tool.py loc-export localization_all.localization.en-US strings.csv

# Import translated CSV back
python3 smps4tool.py loc-import original.localization translated.csv output.localization
```

### Other commands

| Command | Description |
|---|---|
| `info` | TOC summary |
| `list` | Search assets (`--search`, `--archive`, `--named-only`, `--limit`) |
| `build-hashdb` | Build hash DB from dag |
| `csv` | Export full asset list to CSV |
| `hash` | Compute CRC-64 hash |
| `dag` | Search DAG asset names |

---

## Translation Workflow

```bash
# 1. Extract localization files
python3 smps4tool.py extract --archive-dir /game --archive p000115 --output loc/ --flat

# 2. Export to CSV
python3 smps4tool.py loc-export loc/localization_localization_all.localization.en-US strings.csv

# 3. Translate: fill "translation" column in CSV

# 4. Import back
python3 smps4tool.py loc-import \
    loc/localization_localization_all.localization.en-US strings.csv modified.localization

# 5. Patch into game (lightweight — no full repack needed)
python3 smps4tool.py patch --archive-dir /game --mod-name mod_translation \
    --files "0xBE55D94F171BF8DE=modified.localization" --output-toc toc.new

# 6. Copy toc.new → toc, mod_translation stays in game directory
```

---

## Known Asset Locations

### Localization (text strings)

| Asset | Archive | Asset ID | Note |
|---|---|---|---|
| `localization\localization_all.localization` | `p000115` | `0xBE55D94F171BF8DE` | 32 copies, one per language |

Each copy is LZ4-compressed DAT1 with key/translation string tables (54,010 entries). Language is auto-detected via `TEST_ALL_LANG` key inside each file.

Supported languages: en-US, en-GB, ja, fr, fr-CA, es, es-LA, de, it, nl, pt, pt-BR, ru, ko, zh-Hant, zh-Hans, fi, sv, da, no, pl, cs, el, tr, ar, ro, hu + 5 empty/fallback slots.

### Fonts (GFX/Scaleform)

| Asset | Archive | Asset ID | Format | Note |
|---|---|---|---|---|
| Font_LatinAS3 (Azbuka Pro Bold Italic) | `p000026` | `0xB1BC4746124FA7ED` | GFX (Scaleform) | Main UI font, 438 KB |

Additional font candidates in `p000026` (hex-ID assets, 100–500 KB, likely GFX format for CJK/Cyrillic/Arabic scripts):

```
0x84E2C94F88EE239B    257 KB
0x9D1311A64950EC6F    248 KB
0x92BDFC3963702AFF    247 KB
0x9876B52CAF4F51E0    246 KB
0xAD8C5B044177EEF6    244 KB
0x9A03FE065EC606AF    154 KB
0xA2700DBFAB093950    153 KB
```

GFX files start with magic bytes `47 46 58 0E` ("GFX"). Font glyphs are embedded as vector shapes inside the SWF-based GFX container.

---

## PS4 File Structure

```
toc                         ← Master index (zlib → DAT1, 6 sections, stride 24)
dag                         ← Asset names (386k strings)
g00s000, g00s001, ...       ← Large archives (gameplay, textures, models)
p000026, p000027, ...       ← Small archives (localization, configs, fonts)
a00s019.us, a00s020.fr, ... ← Locale-specific archives
```

### Localization format (LZ4 + DAT1)

| Section ID | Contents |
|---|---|
| `0x4D73CEBD` | Key strings |
| `0xA4EA55B2` | Key offsets (int[]) |
| `0x70A382B8` | Translation strings |
| `0xF80DEEB4` | Translation offsets (int[]) |

Compatible with [team-waldo/InsomniacArchive](https://github.com/team-waldo/InsomniacArchive). Same format on PS4 and PC.

---

## Bugfixes

- **Archive name truncation** — Names longer than 8 bytes were cut off (9 locale-suffixed archives affected). Fixed: null-terminated read.
- **Language detection** — PS4 system language index didn't match game's actual order. Fixed: content-based detection via `TEST_ALL_LANG` key. 32/32 verified correct.

---

## Files

| File | Description |
|---|---|
| `smps4tool.py` | Main tool |
| `PS4AssetHashes.txt` | Pre-built hash DB (386,344 entries, 44 MB) |
| `SMPS4HashTool.exe` | Original native hash tool (reference only) |

---

## Credits

- **[jedijosh920](https://www.nexusmods.com/marvelsspidermanremastered/mods/51)** — Original SMPCTool (PC)
- **[Phew](https://github.com/Phew/SMPCTool-src)** — SMPCTool source code
- **[zerlkung](https://github.com/zerlkung/SMPCTool-PS4)** — SMPCTool-PS4 C# version
- **[team-waldo / akintos](https://github.com/team-waldo/InsomniacArchive)** — InsomniacArchive & SpidermanLocalizationTool (localization DAT1 section IDs, LZ4 asset format, CSV export/import workflow)
- Hash algorithm reverse-engineered from SMPS4HashTool.exe

---
---

# ภาษาไทย

## SMPCTool-PS4 Python 🕷️

**Spider-Man PS4 Asset Tool** — Python rewrite ของ [SMPCTool-PS4](https://github.com/zerlkung/SMPCTool-PS4) (C#) สำหรับจัดการไฟล์เกม Marvel's Spider-Man บน PS4

---

### ติดตั้ง

- Python 3.10+
- `pip install lz4` (จำเป็นสำหรับ loc-export/loc-import)

### ใช้งานครั้งแรก

```bash
python3 smps4tool.py build-hashdb --dag dag
python3 smps4tool.py info
```

---

### คำสั่งทั้งหมด

| คำสั่ง | คำอธิบาย |
|---|---|
| `extract` | Extract asset (`--skip-hex`, `--flat`, auto lang suffix) |
| `patch` | แทนที่เฉพาะไฟล์ที่แก้ → mod archive เล็ก + TOC ใหม่ |
| `repack` | สร้าง archive ใหม่จาก original (`--skip-hex`) |
| `repack-dir` | สร้าง archive ใหม่จาก directory (`--flat`) |
| `loc-export` | แปลง localization → CSV (54,010 strings) |
| `loc-import` | นำเข้า CSV ที่แปลแล้ว → localization ใหม่ |
| `info` | ดูข้อมูล TOC |
| `list` | ค้นหา asset |
| `build-hashdb` | สร้าง hash DB จาก dag |
| `csv` | Export รายการ asset เป็น CSV |
| `hash` | คำนวณ CRC-64 hash |
| `dag` | ค้นหาชื่อจาก dag |

---

### `patch` — แทนที่เฉพาะไฟล์ (ไม่ต้อง repack ทั้ง archive)

```bash
# สร้าง mod archive เล็ก ๆ + TOC ใหม่
python3 smps4tool.py patch --archive-dir /game --mod-name mod_translation \
    --files "0xBE55D94F171BF8DE=modified.localization" --output-toc toc.new

# patch หลายไฟล์พร้อมกัน
python3 smps4tool.py patch --archive-dir /game --mod-name mod_pack \
    --files "0xBE55D94F171BF8DE=new_loc.bin" "0xB1BC4746124FA7ED=new_font.gfx" \
    --output-toc toc.new
```

สร้าง archive เล็ก ๆ ที่มีเฉพาะไฟล์ที่แก้ แล้ว patch TOC ให้ชี้ไป asset อื่น 657,000+ ตัวยังอ่านจาก archive เดิม

---

### ขั้นตอนแปลภาษา

```bash
# 1. Extract localization
python3 smps4tool.py extract --archive-dir /game --archive p000115 --output loc/ --flat

# 2. Export CSV
python3 smps4tool.py loc-export loc/localization_localization_all.localization.en-US strings.csv

# 3. แปลภาษาใน CSV (คอลัมน์ translation)

# 4. Import กลับ
python3 smps4tool.py loc-import \
    loc/localization_localization_all.localization.en-US strings.csv modified.localization

# 5. Patch เข้าเกม (ไม่ต้อง repack ทั้ง archive)
python3 smps4tool.py patch --archive-dir /game --mod-name mod_translation \
    --files "0xBE55D94F171BF8DE=modified.localization" --output-toc toc.new
```

---

### ตำแหน่งไฟล์สำคัญ

| ไฟล์ | Archive | Asset ID | หมายเหตุ |
|---|---|---|---|
| Localization (ข้อความ) | `p000115` | `0xBE55D94F171BF8DE` | 32 ภาษา, LZ4+DAT1 |
| Font หลัก (Azbuka Pro) | `p000026` | `0xB1BC4746124FA7ED` | GFX/Scaleform, 438 KB |
| Font อื่น ๆ (CJK ฯลฯ) | `p000026` | hex IDs 100-500 KB | GFX format (`47 46 58 0E`) |

---

### Bugfixes

- **Archive name truncation** — ชื่อยาวกว่า 8 bytes ถูกตัด → แก้แล้ว
- **Language detection** — PS4 index ไม่ตรง → แก้เป็นตรวจจับจากเนื้อหา `TEST_ALL_LANG` (32/32 ถูกต้อง)

---

### Credits

- **[jedijosh920](https://www.nexusmods.com/marvelsspidermanremastered/mods/51)** — SMPCTool ต้นฉบับ (PC)
- **[Phew](https://github.com/Phew/SMPCTool-src)** — ซอร์สโค้ด SMPCTool
- **[zerlkung](https://github.com/zerlkung/SMPCTool-PS4)** — SMPCTool-PS4 เวอร์ชัน C#
- **[team-waldo / akintos](https://github.com/team-waldo/InsomniacArchive)** — InsomniacArchive & SpidermanLocalizationTool (localization DAT1 section IDs, LZ4 asset format, CSV export/import workflow)
- Hash algorithm reverse-engineered จาก SMPS4HashTool.exe
