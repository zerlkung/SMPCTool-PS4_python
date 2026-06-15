# SMPS4Tool — Spider-Man PS4/PS5/PC Asset Tool 🕷️

**Spider-Man Asset Tool** — Python rewrite of [SMPCTool-PS4](https://github.com/zerlkung/SMPCTool-PS4) (C#) for managing Marvel's Spider-Man game files on PS4, PS5, PC (Remaster), and Miles Morales.

Single-file per platform, pure Python 3. Works as a CLI tool and a Python library.

> 🇹🇭 [อ่านเป็นภาษาไทย / Thai version](#ภาษาไทย)

---

## Tools by Platform

| Tool | Platform | ARCH_STRIDE | Loc Strings |
|---|---|---|---|
| `smps4tool.py` | SM1 PS4 (CUSA11993) | 24 | 54,010 |
| `smps4tool_mm.py` | Miles Morales PS4 | 72 | 34,079 |
| **`smps5tool.py`** | **SM Remaster PS5/PC** | **72** | **56,417** |
| **`smps5tool.py`** | **Miles Morales PS5/PC** | **72** | **34,076 / 35,128** |

> **Note:** `smps5tool.py` works for BOTH Spider-Man Remastered AND Miles Morales on PS5/PC. The TOC format is identical (ARCH_STRIDE=72, path-based archives). MM PS5 has 7 DAT1 sections (1 extra vs SM Remaster's 6) — handled automatically.

---

## ⚠️ Work In Progress

| Feature | SM1 PS4 | MM PS4 | SM PS5/PC | MM PS5/PC |
|---|---|---|---|---|
| Extract / repack / patch | ✅ | ✅ | ✅ | ✅ |
| Font replacement (`0xB1BC4746124FA7ED`) | ✅ | ✅ | ✅ | ✅ |
| Localization export (`loc-export`) | ✅ | ✅ | ✅ | ✅ |
| Localization import (`loc-import`) | ✅ | ✅ | ✅ | ✅ |
| `--all-lang` (patch all language slots) | ✅ 32 slots | ✅ 32 slots | — | — |
| CP874 / Thai encoding support | ✅ | ✅ | — | — |
| Format B (wrapper + raw DAT1) | ✅ | ✅ | — | — |
| Raw DAT1 (PS5 loc format) | — | — | ✅ | ✅ |
| Multi-section loc preservation | — | — | 9 sections | 9 sections |
| `--asset-index` slot selection | — | — | ✅ 31 slots | ✅ 30 slots |

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
python3 smps4tool.py patch --archive-dir /game --mod-name <mod-name> \
    --files "localization_localization_all.localization.en-US=modified.loc" \
            "localization_localization_all.localization.en-US_2=modified.loc" \
    --output-toc toc.new

# Patch font + localization together
python3 smps4tool.py patch --archive-dir /game --mod-name <mod-name> \
    --files "localization_localization_all.localization.en-US=modified.loc" \
            "localization_localization_all.localization.en-US_2=modified.loc" \
            "0xB1BC4746124FA7ED=myfont.gfx" \
    --output-toc toc.new
```

Creates a small archive with ONLY modified files, then patches the TOC to redirect those assets. All other 657,000+ assets remain untouched.

**`--all-lang`** — patch all 32 language slots at once with the same file. Recommended for localization mods since the game may load a different language slot depending on system/region:

```
python3 smps4tool.py patch --archive-dir /game --mod-name <mod-name> --files "localization_localization_all.localization.en-US=thai.loc" "0xB1BC4746124FA7ED=font.gfx" --all-lang --output-toc toc.new
```

**Note:** When patching translated localization files, `p000115` must be present in `--archive-dir` for language detection. If it is not available, the tool falls back to **archive-offset ordering** — `.en-US` → 1st copy, `.en-US_2` → 2nd copy.

### `repack` / `repack-dir` — Rebuild entire archive
```bash
python3 smps4tool.py repack --archive-dir /game --archive p000045 \
    --output-archive p000045_new --output-toc toc.new --skip-hex

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

# 6. Patch into game (--all-lang patches all 32 language slots)
python3 smps4tool.py patch --archive-dir /game --mod-name <mod-name> --files "localization_localization_all.localization.en-US=fixed.loc" "0xB1BC4746124FA7ED=font.gfx" --all-lang --output-toc toc.new

# 7. Copy toc.new → toc, place <mod-name> file in game archive directory
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
- **`--all-lang` flag** — patches all 32 language slots simultaneously with the same file. Recommended since the game may load a different slot depending on region or system language setting.

---

## Files

| File | Description |
|---|---|
| `smps4tool.py` | Main tool — Marvel's Spider-Man (2018) PS4 |
| `smps4tool_mm.py` | Main tool — Marvel's Spider-Man: Miles Morales PS4 |
| `smps5tool.py` | Main tool — Marvel's Spider-Man Remastered PS5/PC |
| `fix_thai_chars.py` | Repair Thai keyboard-mapping errors in imported loc files |
| `PS4AssetHashes.txt` | Pre-built hash DB for SM1 (386,344 entries, 44 MB) |
| `MilesAssetHashes.txt` | Pre-built hash DB for MM (296,044 entries, 33 MB) |
| `SMPS4HashTool.exe` | Original native hash tool (reference only) |

---

## Miles Morales PS4 ✅

`smps4tool_mm.py` is a separate tool for **Marvel's Spider-Man: Miles Morales (PS4)**.
It is identical to `smps4tool.py` except for `ARCH_STRIDE = 72` (vs 24 for SM1).

| | SM1 PS4 | MM PS4 |
|---|---|---|
| Tool | `smps4tool.py` | `smps4tool_mm.py` |
| Hash DB | `PS4AssetHashes.txt` | `MilesAssetHashes.txt` |
| Archive stride | 24 bytes | 72 bytes |
| Loc archive | `p000115` | `p000065` |
| Loc hash | `0xBE55D94F171BF8DE` | `0xBE55D94F171BF8DE` (same) |
| Strings per lang | 54,010 | 34,079 |
| Font hash | `0xB1BC4746124FA7ED` | `0xB1BC4746124FA7ED` (same) |
| Font archive | `p000026` | `g00s012` |
| Font size | 438 KB | 272 KB |

Usage is identical — just replace `smps4tool.py` with `smps4tool_mm.py` and use `MilesAssetHashes.txt`:

```
python smps4tool_mm.py build-hashdb --dag dag --output MilesAssetHashes.txt
python smps4tool_mm.py info
```

### Known Asset Locations (MM PS4)

| Asset | Archive | Hash |
|---|---|---|
| Localization (32 languages) | `p000065` | `0xBE55D94F171BF8DE` |
| Font (GFX/Scaleform) | `g00s012` | `0xB1BC4746124FA7ED` |

### Translation Workflow (MM PS4)

```
python smps4tool_mm.py loc-export p000065_en.loc strings.csv
```
_(edit CSV — save as UTF-8)_
```
python smps4tool_mm.py loc-import p000065_en.loc strings.csv imported.loc
python fix_thai_chars.py imported.loc fixed.loc
python smps4tool_mm.py patch --archive-dir asset_archive --mod-name <mod-name> --files "localization_localization_all.localization.en=fixed.loc" "0xB1BC4746124FA7ED=0xB1BC4746124FA7ED" --all-lang --output-toc toc.new
```

**Note:** `g00s012` must be present in `--archive-dir` for font patching. Language detection uses `ABANDON_CONFIRM_HEADER` (MM has no `TEST_ALL_LANG` key). Use `--all-lang` when patching localization to ensure the game loads the correct slot.

---

## PS5 / PC Remaster ✅

`smps5tool.py` works for both **Spider-Man Remastered** AND **Miles Morales** on PS5/PC. Both use the same TOC format (ARCH_STRIDE=72, path-based archives). MM PS5 has 7 DAT1 sections vs 6 for SM Remaster — handled automatically.

| | SM1 PS4 | SM Remaster PS5/PC | MM PS5/PC |
|---|---|---|---|
| Tool | `smps4tool.py` | `smps5tool.py` | `smps5tool.py` |
| ARCH_STRIDE | 24 | 72 | 72 |
| Archives | 118 flat | 174 path (`d\xxx`) | 174 path (`d\xxx`) |
| Assets | 657,831 | 814,061 | 583,237 |
| TOC sections | 6 | 6 | 7 |
| Loc hash | `0xBE55D94F171BF8DE` | same | same |
| Loc sections | 4 (LZ4) | 9 (raw DAT1) | 9 (raw DAT1) |
| Strings per lang | 54,010 | 56,417 | 34,076 |
| Font hash | `0xB1BC4746124FA7ED` | same | same |
| Font archive | `p000026` | `d\userinterface` | `d\userinterface` |
| Font size | 438 KB | 442 KB | 273 KB |

Key differences from PS4:
- **Single loc file** per language (not 32 copies) — no `--all-lang` needed
- **Path-based archive names** (`d\userinterface`, `d\localization`) instead of flat
- **Raw uncompressed DAT1** inside LZ4 header (9 sections vs 4)
- **Extra sections preserved** during loc-import (0x06A58050, 0x0CD2CFE9, 0xB0653243, 0xC43731B5, 0xD540A903)

### Setup

```
python smps5tool.py build-hashdb --dag dag --output PS5AssetHashes.txt
python smps5tool.py --toc toc info
```

### Translation Workflow

```
# 1. Extract localization
python smps5tool.py --toc toc extract --archive-dir PS5_Files --id 0xBE55D94F171BF8DE --output extracted/

# 2. Export to CSV (56,417 strings)
python smps5tool.py loc-export extracted/localization/localization_all.localization strings.csv

# 3. Edit strings.csv (fill translation column) — save as UTF-8!

# 4. Import back
python smps5tool.py loc-import extracted/localization/localization_all.localization strings.csv modified.loc

# 5. Patch font + localization into mod archive
python smps5tool.py --toc toc patch --archive-dir PS5_Files --mod-name modmycon \
    --files "0xBE55D94F171BF8DE=modified.loc" \
            "0xB1BC4746124FA7ED=font.gfx" \
    --output-toc toc.new
```

### Language Slot Selection

### Language Slot Reference

Each game has multiple language slots sharing the same hash. The **active slot** (the one the game actually reads) varies:

| Game | Active Slot | `--asset-index` | Note |
|---|---|---|---|
| **SM Remaster PS5** | 1 | `--asset-index 1` | Slot 0 & 2 = English, game reads slot 1 |
| **MM PS5** | 2 | `--asset-index 2` | Slot 0 & 1 = English, game reads slot 2 |
| **MM PS4** | — | (use `--all-lang`) | 32 copies, patch all |
| **SM1 PS4** | — | (use `--all-lang`) | 32 copies, patch all |

**How to find the active slot:** patch each slot 0,1,2 one at a time. If game shows translation = correct slot. If game shows English = wrong slot. If game black screens = slot IS read but file has issues.

### Patch Mechanism

PS5/PC **cannot create new archive entries** — the game rejects TOC modifications that add archives. Instead, `smps5tool.py` appends data to an existing archive (default: `d\userinterface`, index 130) and redirects assets to the new offsets. No `--mod-name` needed.

**Full workflow:**
```
# 1. Extract loc (slot 0, the first match)
python smps5tool.py --toc toc extract --archive-dir game/ --id 0xBE55D94F171BF8DE --output extracted/

# 2. Export to CSV (56,417 strings)
python smps5tool.py loc-export extracted/localization/localization_all.localization strings.csv

# 3. Translate: fill "translation" column in strings.csv — save as UTF-8!

# 4. Import back (raw format, game requires uncompressed DAT1)
python smps5tool.py loc-import extracted/localization/localization_all.localization strings.csv modified.loc

# 5. Patch loc + font (appends to d\userinterface)
python smps5tool.py --toc toc patch --archive-dir game/ \
    --files "0xBE55D94F171BF8DE=modified.loc" \
            "0xB1BC4746124FA7ED=font.gfx" \
    --asset-index 1 \
    --output-toc toc.new

# 6. Replace toc in game directory
copy toc.new toc
```

### Lessons Learned (PS5/PC vs PS4)

| Issue | Symptom | Root Cause | Fix |
|---|---|---|---|
| `add_archive` | Black screen on boot | Game validates archive count; rejects new entries | Append to existing archive (`d\userinterface`) |
| `--all-lang` | Black screen | 31 unique language files expected, not 1 shared | Patch only active slot (`--asset-index`) |
| LZ4 compression | Black screen | Game expects raw DAT1 inside LZ4 header | `_loc_compress` writes uncompressed |
| Wrong slot | Game loads but shows English | Game reads specific slot per system language | `--asset-index` to target correct slot |
| Section preservation | Data corruption / crash | PS5 loc has 9 DAT1 sections (vs 4 on PS4) | Preserve extra sections during import |

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

**Spider-Man PS4 Asset Tool** — Python rewrite ของ [SMPCTool-PS4](https://github.com/zerlkung/SMPCTool-PS4) (C#) สำหรับจัดการไฟล์เกม Marvel's Spider-Man บน PS4 (CUSA11993)

---

## ⚠️ สถานะการพัฒนา

| ฟีเจอร์ | สถานะ |
|---|---|
| Extract / repack / patch | ✅ ใช้งานได้ |
| Font replacement | ✅ ใช้งานได้ — ทดสอบในเกมแล้ว |
| loc-export | ✅ ใช้งานได้ |
| loc-import (นำเข้าการแปล) | ✅ ใช้งานได้ — ใช้ `--all-lang` เพื่อ patch ทุก 32 language slots |
| **Miles Morales PS4** (`smps4tool_mm.py`) | ✅ ใช้งานได้ — ทดสอบ font และ localization ในเกมแล้ว |

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

# 6. Patch เข้าเกม (--all-lang patch ทุก 32 language slots พร้อมกัน)
python3 smps4tool.py patch --archive-dir /game --mod-name <mod-name> --files "localization_localization_all.localization.en-US=fixed.loc" "0xB1BC4746124FA7ED=font.gfx" --all-lang --output-toc toc.new
```

---

### ตำแหน่งไฟล์สำคัญ

| ไฟล์ | Archive | Asset ID | หมายเหตุ |
|---|---|---|---|
| Localization (ข้อความ) | `p000115` | `0xBE55D94F171BF8DE` | 32 ภาษา, LZ4+DAT1 |
| Font หลัก (Azbuka Pro) | `p000026` | `0xB1BC4746124FA7ED` | GFX/Scaleform, 438 KB |

---

## PS5 / PC Remaster (smps5tool.py)

เครื่องมือสำหรับ **Marvel's Spider-Man Remastered (PS5/PC)** — ใช้ `smps5tool.py`

| | SM1 PS4 | PS5/PC |
|---|---|---|
| ARCH_STRIDE | 24 | 72 |
| Archives | 118 (ชื่อแบน) | 174 (path `d\xxx`) |
| Loc hash | `0xBE55D94F171BF8DE` | เหมือนกัน |
| Loc format | LZ4 บีบอัด, 4 sections | RAW ใน LZ4 header, 9 sections |
| ภาษา | 32 ไฟล์แยก | 31 slots ใน `d\localization` |
| Strings | 54,010 | 56,417 |
| Font hash | `0xB1BC4746124FA7ED` | เหมือนกัน |
| Font archive | `p000026` | `d\userinterface` |

### ข้อแตกต่างสำคัญจาก PS4

- **ต่อท้าย archive เดิม** — PS5 ไม่รับ archive ใหม่ใน TOC → ต้องต่อท้าย `d\userinterface` (หรือ archive อื่นที่มีอยู่แล้ว) แทนการสร้าง `modmycon`
- **เลือก slot ด้วย `--asset-index`** — 31 slots ภาษา เกมอ่านเฉพาะ slot ที่ตรงกับระบบ ต้องหาว่า slot ไหนเกมอ่าน (ปกติ slot 1)
- **`--all-lang` ใช้ไม่ได้** — PS5 แต่ละ slot เป็นคนละภาษา ถ้า patch เหมือนกันหมดเกมจะพัง
- **RAW storage** — localization ต้องเก็บแบบไม่บีบอัด (raw DAT1) เกมอ่าน LZ4 compress ไม่ได้
- **9 sections** — PS5 loc มี 9 DAT1 sections (PS4 มี 4) ต้อง preserve ตอน import

### ขั้นตอนแปลภาษา (PS5/PC)

```bash
# 1. Extract localization (slot 0 = English)
python smps5tool.py --toc toc extract --archive-dir game/ --id 0xBE55D94F171BF8DE --output extracted/

# 2. Export CSV (56,417 strings)
python smps5tool.py loc-export extracted/localization/localization_all.localization strings.csv

# 3. แปลภาษาใน CSV (คอลัมน์ translation) — บันทึกเป็น UTF-8 เท่านั้น!

# 4. Import กลับ (เป็น raw format)
python smps5tool.py loc-import extracted/localization/localization_all.localization strings.csv modified.loc

# 5. Patch loc + ฟอนต์ (ต่อท้าย d\userinterface)
python smps5tool.py --toc toc patch --archive-dir game/ \
    --files "0xBE55D94F171BF8DE=modified.loc" \
            "0xB1BC4746124FA7ED=font.gfx" \
    --asset-index 1 \
    --output-toc toc.new

# 6. แทนที่ toc ในโฟลเดอร์เกม
copy toc.new toc
```

### การเลือก Language Slot

แต่ละเกมมีหลาย language slot แชร์ hash เดียวกัน ต้องเลือกให้ถูกว่าเกมอ่าน slot ไหน:

| เกม | Active Slot | `--asset-index` | หมายเหตุ |
|---|---|---|---|
| **SM Remaster PS5** | 1 | `--asset-index 1` | Slot 0,2 = อังกฤษ เกมอ่าน slot 1 |
| **MM PS5** | 2 | `--asset-index 2` | Slot 0,1 = อังกฤษ เกมอ่าน slot 2 |
| **MM PS4** | — | (ใช้ `--all-lang`) | 32 copies |
| **SM1 PS4** | — | (ใช้ `--all-lang`) | 32 copies |

**วิธีหา active slot:** ลอง patch slot 0,1,2 ทีละตัว ถ้าเกมแสดงผลเป็นภาษาแปล = ถูก slot / เป็นอังกฤษ = ผิด slot / จอดำ = ถูก slot แต่ไฟล์มีปัญหา

### บทเรียนจาก PS5 (Lessons Learned)

| ปัญหา | อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|---|
| `add_archive` | จอดำ ไม่เข้าเกม | เกมตรวจสอบจำนวน archive; ไม่รับ archive ใหม่ | ต่อท้าย archive เดิม (`d\userinterface`) |
| `--all-lang` | จอดำ | 31 ไฟล์ภาษาต้องต่างกัน | ใช้ `--asset-index` patch เฉพาะ slot ที่เกมอ่าน |
| LZ4 บีบอัด | จอดำ | เกมคาดหวัง raw DAT1 ใน LZ4 header | `_loc_compress` เขียนแบบไม่บีบอัด |
| ผิด slot | เข้าเกมได้แต่เป็นอังกฤษ | เกมอ่าน slot ตามภาษาเครื่อง | `--asset-index` เลือก slot ที่ถูกต้อง |
| Section ไม่ครบ | ข้อมูลเสียหาย | PS5 มี 9 sections (PS4 มี 4) | Preserve ทุก section ตอน import |

---

### Bugfixes

- **Archive name truncation** — ชื่อยาวกว่า 8 bytes ถูกตัด → แก้แล้ว
- **Language detection** — PS4 index ไม่ตรง → แก้เป็นตรวจจับจากเนื้อหา `TEST_ALL_LANG` (32/32 ถูกต้อง)
- **Format B support** — รองรับ localization format B (wrapper + raw DAT1)
- **CP874 encoding** — auto-detect และ decode/encode ภาษาไทยที่เก็บเป็น CP874-as-UTF8
- **Translated file detection** — fallback ด้วย archive-offset ordering เมื่อ `TEST_ALL_LANG` ถูกแปลแล้ว
- **`--all-lang` flag** — patch ทุก 32 language slots พร้อมกันด้วยไฟล์เดียว เพราะเกมอาจโหลด slot ที่ต่างกันขึ้นอยู่กับ region/system language

---

### Credits

- **[jedijosh920](https://www.nexusmods.com/marvelsspidermanremastered/mods/51)** — SMPCTool ต้นฉบับ (PC)
- **[Phew](https://github.com/Phew/SMPCTool-src)** — ซอร์สโค้ด SMPCTool
- **[zerlkung](https://github.com/zerlkung/SMPCTool-PS4)** — SMPCTool-PS4 เวอร์ชัน C#
- **[team-waldo / akintos](https://github.com/team-waldo/InsomniacArchive)** — InsomniacArchive & SpidermanLocalizationTool
- Hash algorithm reverse-engineered จาก SMPS4HashTool.exe
