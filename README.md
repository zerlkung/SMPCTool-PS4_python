# SMPCTool-PS4 Python 🕷️ | WIP

**Spider-Man PS4 Asset Tool** — A Python rewrite of [SMPCTool-PS4](https://github.com/zerlkung/SMPCTool-PS4) (C#) for managing Marvel's Spider-Man game files on PS4.

Single-file, pure Python 3. Works as both a CLI tool and a Python library.

> 🇹🇭 [อ่านเป็นภาษาไทย / Thai version](#ภาษาไทย)

---

## ⚠️ Work In Progress

| Feature | Status |
|---|---|
| Extract / repack / patch | ✅ Working |
| Font replacement (`0xB1BC4746124FA7ED`) | ✅ Working — verified in-game |
| Localization export (`loc-export`) | ✅ Working |
| Localization import (`loc-import`) | 🚧 WIP — pipeline complete, in-game display under investigation |
| CP874 / Thai encoding support | ✅ Implemented |
| Format B (wrapper + raw DAT1) | ✅ Implemented |

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
# Patch localization — patches both en-copy (slot 0) and en-US (slot 1)
python3 smps4tool.py patch --archive-dir /game --mod-name modmycon \
    --files "localization_localization_all.localization.en-US=modified.loc" \
            "localization_localization_all.localization.en-US_2=modified.loc" \
    --output-toc toc.new

# Patch font + localization together
python3 smps4tool.py patch --archive-dir /game --mod-name modmycon \
    --files "localization_localization_all.localization.en-US=modified.loc" \
            "localization_localization_all.localization.en-US_2=modified.loc" \
            "0xB1BC4746124FA7ED=myfont.gfx" \
    --output-toc toc.new
```

Creates a small archive with ONLY modified files, then patches the TOC to redirect those assets. All other 657,000+ assets remain untouched.

**Note:** When patching translated localization files, `p000115` must be present in `--archive-dir` for language detection. If it is not available, the tool falls back to **archive-offset ordering** — `.en-US` → 1st copy, `.en-US_2` → 2nd copy.

### `repack` / `repack-dir` — Rebuild entire archive
```bash
python3 smps4tool.py repack --archive-dir /game --archive p000045 \
    --output-archive p000045_new --output-toc toc.new --skip-hex

python3 smps4tool.py repack-dir --archive-dir /game --archive p000045 \
    --dir extracted/ --output-archive p000045_new --output-toc toc.new --flat
```

### `loc-export` / `loc-import` — Localization translation ⚠️ WIP
```bash
# Export to CSV (54,010 strings)
python3 smps4tool.py loc-export localization_all.localization.en-US strings.csv

# Import translated CSV back
python3 smps4tool.py loc-import original.localization translated.csv output.localization
```

**Known issues:**
- If the source CSV was saved in CP874/TIS-620 encoding instead of UTF-8, tone marks will be garbled (ฃ→่, ฅ→้, ๎→็, ๏→ี, ๚→๊, ๛→๋). Use `fix_thai_chars.py` to repair after import.
- Characters that become U+FFFD during import cannot be auto-fixed — re-save the CSV as UTF-8 before importing.

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

# 3. Translate: fill "translation" column in strings.csv
#    IMPORTANT: save as UTF-8 encoding (not CP874/TIS-620)

# 4. Import back
python3 smps4tool.py loc-import \
    loc/localization_localization_all.localization.en-US \
    strings.csv \
    modified.loc

# 5. (Optional) Fix Thai keyboard-mapping errors if tone marks are garbled
python3 fix_thai_chars.py modified.loc fixed.loc

# 6. Patch into game
python3 smps4tool.py patch --archive-dir /game --mod-name modmycon \
    --files "localization_localization_all.localization.en-US=fixed.loc" \
            "localization_localization_all.localization.en-US_2=fixed.loc" \
    --output-toc toc.new

# 7. Copy toc.new → toc, place modmycon in game archive directory
```

---

## Known Asset Locations

### Localization (text strings)

| Asset | Archive | Asset ID | Note |
|---|---|---|---|
| `localization\localization_all.localization` | `p000115` | `0xBE55D94F171BF8DE` | 32 copies, one per language |

Each copy is LZ4-compressed DAT1 with key/translation string tables (54,010 entries). Language is auto-detected via `TEST_ALL_LANG` key inside each file.

Language slots: en-US (slot 1), en-GB (2), da (3), nl (4), fi (5), fr (6), de (7), it (8), ja (9), ko (10), no (11), pl (12), pt-BR (13), ru (14), es (15), sv (16), pt (18), en-GB copy (19), es-LA (21), zh-Hans (22), zh-Hant (23), fr-CA (24), cs (25), hu (26), el (27).

### Fonts (GFX/Scaleform)

| Asset | Archive | Asset ID | Format | Status |
|---|---|---|---|---|
| Font_LatinAS3 (Azbuka Pro Bold Italic) | `p000026` | `0xB1BC4746124FA7ED` | GFX | ✅ Working in-game |

Additional font candidates in `p000026` (hex-ID assets, likely GFX, CJK/Cyrillic/Arabic):

```
0x84E2C94F88EE239B    257 KB
0x9D1311A64950EC6F    248 KB
0x92BDFC3963702AFF    247 KB
0x9876B52CAF4F51E0    246 KB
0xAD8C5B044177EEF6    244 KB
0x9A03FE065EC606AF    154 KB
0xA2700DBFAB093950    153 KB
```

---

## Localization File Formats

**Format A — LZ4 compressed** (original game files)
```
0x00  AB B0 2B 12  ← LZ4 magic (0x122BB0AB)
0x04  raw_size (uint32)
0x08  padding (28 bytes)
0x24  LZ4 compressed DAT1 data
```

**Format B — Wrapper + raw DAT1** (some translated files)
```
0x00  B5 AF 20 BA  ← Asset wrapper magic (0xBA20AFB5)
0x04  raw_size (uint32, == file_size - 0x24, NOT compressed)
0x08  padding (28 bytes)
0x24  DAT1 directly (raw, not LZ4)
```

Both formats are handled automatically.

### DAT1 Section IDs

| Section ID | Contents |
|---|---|
| `0x4D73CEBD` | Key strings |
| `0xA4EA55B2` | Key offsets (int[]) |
| `0x70A382B8` | Translation strings |
| `0xF80DEEB4` | Translation offsets (int[]) |

---

## PS4 File Structure

```
toc                         ← Master index (zlib → DAT1, 6 sections, stride 24)
dag                         ← Asset names (386k strings)
g00s000, g00s001, ...       ← Large archives (gameplay, textures, models)
p000026, p000027, ...       ← Small archives (localization, configs, fonts)
a00s019.us, a00s020.fr, ... ← Locale-specific archives
```

---

## Bugfixes

- **Archive name truncation** — Names longer than 8 bytes were cut off (9 locale-suffixed archives affected). Fixed: null-terminated read.
- **Language detection** — PS4 system language index didn't match game's actual order. Fixed: content-based detection via `TEST_ALL_LANG` key. 32/32 verified correct.
- **Wrapper auto-strip** — Files with `0xBA20AFB5` wrapper are auto-stripped in `patch` command.
- **Format B support** — `loc-export`/`loc-import` now handle both LZ4 (Format A) and raw DAT1 (Format B) localization files.
- **CP874 encoding** — `loc-export` auto-detects and decodes CP874-as-UTF8 pairs. `loc-import` auto-detects and re-encodes correctly.
- **Translated file detection** — `_match_lang_duplicate` falls back to archive-offset ordering when `TEST_ALL_LANG` has been translated (making content-based detection unavailable).

---

## Files

| File | Description |
|---|---|
| `smps4tool.py` | Main tool |
| `fix_thai_chars.py` | Repair Thai keyboard-mapping errors in imported loc files |
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

## ⚠️ สถานะการพัฒนา

| ฟีเจอร์ | สถานะ |
|---|---|
| Extract / repack / patch | ✅ ใช้งานได้ |
| Font replacement | ✅ ใช้งานได้ — ทดสอบในเกมแล้ว |
| loc-export | ✅ ใช้งานได้ |
| loc-import (นำเข้าการแปล) | 🚧 WIP — pipeline ครบแล้ว อยู่ระหว่างตรวจสอบการแสดงผลในเกม |

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
| `repack` | สร้าง archive ใหม่จาก original |
| `repack-dir` | สร้าง archive ใหม่จาก directory |
| `loc-export` | แปลง localization → CSV (54,010 strings) |
| `loc-import` | นำเข้า CSV ที่แปลแล้ว → localization ใหม่ ⚠️ WIP |
| `info` | ดูข้อมูล TOC |
| `list` | ค้นหา asset |
| `build-hashdb` | สร้าง hash DB จาก dag |
| `csv` | Export รายการ asset เป็น CSV |
| `hash` | คำนวณ CRC-64 hash |
| `dag` | ค้นหาชื่อจาก dag |

---

### ขั้นตอนแปลภาษา

```bash
# 1. Extract
python3 smps4tool.py extract --archive-dir /game --archive p000115 --output loc/ --flat

# 2. Export CSV
python3 smps4tool.py loc-export loc/localization_localization_all.localization.en-US strings.csv

# 3. แปลภาษาใน CSV (คอลัมน์ translation) — บันทึกเป็น UTF-8 เท่านั้น!

# 4. Import
python3 smps4tool.py loc-import \
    loc/localization_localization_all.localization.en-US \
    strings.csv modified.loc

# 5. แก้ tone mark ถ้าผิด (ฃ→่, ฅ→้, ๎→็)
python3 fix_thai_chars.py modified.loc fixed.loc

# 6. Patch เข้าเกม
python3 smps4tool.py patch --archive-dir /game --mod-name modmycon \
    --files "localization_localization_all.localization.en-US=fixed.loc" \
            "localization_localization_all.localization.en-US_2=fixed.loc" \
    --output-toc toc.new
```

---

### ตำแหน่งไฟล์สำคัญ

| ไฟล์ | Archive | Asset ID | หมายเหตุ |
|---|---|---|---|
| Localization (ข้อความ) | `p000115` | `0xBE55D94F171BF8DE` | 32 ภาษา, LZ4+DAT1 |
| Font หลัก (Azbuka Pro) | `p000026` | `0xB1BC4746124FA7ED` | GFX/Scaleform, 438 KB |

---

### Bugfixes

- **Archive name truncation** — ชื่อยาวกว่า 8 bytes ถูกตัด → แก้แล้ว
- **Language detection** — PS4 index ไม่ตรง → แก้เป็นตรวจจับจากเนื้อหา `TEST_ALL_LANG` (32/32 ถูกต้อง)
- **Format B support** — รองรับ localization format B (wrapper + raw DAT1)
- **CP874 encoding** — auto-detect และ decode/encode ภาษาไทยที่เก็บเป็น CP874-as-UTF8
- **Translated file detection** — fallback ด้วย archive-offset ordering เมื่อ `TEST_ALL_LANG` ถูกแปลแล้ว

---

### Credits

- **[jedijosh920](https://www.nexusmods.com/marvelsspidermanremastered/mods/51)** — SMPCTool ต้นฉบับ (PC)
- **[Phew](https://github.com/Phew/SMPCTool-src)** — ซอร์สโค้ด SMPCTool
- **[zerlkung](https://github.com/zerlkung/SMPCTool-PS4)** — SMPCTool-PS4 เวอร์ชัน C#
- **[team-waldo / akintos](https://github.com/team-waldo/InsomniacArchive)** — InsomniacArchive & SpidermanLocalizationTool
- Hash algorithm reverse-engineered จาก SMPS4HashTool.exe
