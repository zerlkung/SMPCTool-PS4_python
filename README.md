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
# Step 1: Build hash DB from dag (run once — ~12 sec, produces 44 MB file)
python3 smps4tool.py build-hashdb --dag dag

# Step 2: Verify
python3 smps4tool.py info
```

> The included `PS4AssetHashes.txt` is a pre-built hash DB (386,344 entries). You can skip step 1 if you already have it.

---

## Commands

### `info` — TOC summary
```bash
python3 smps4tool.py info
```

### `list` — Search assets
```bash
python3 smps4tool.py list --search "vulture"
python3 smps4tool.py list --archive g00s000
python3 smps4tool.py list --archive g00s008 --named-only --limit 20
```

### `extract` — Extract assets
```bash
# Extract entire archive
python3 smps4tool.py extract --archive-dir /game --archive p000045 --output out/

# Extract by name / ID / search
python3 smps4tool.py extract --archive-dir /game --name "characters\hero\hero_spiderman\hero_spiderman.model" --output out/
python3 smps4tool.py extract --archive-dir /game --id 0x800035F1EBDCBCEC --output out/
python3 smps4tool.py extract --archive-dir /game --search "npc_vulture" --output out/

# Flat output (no subdirectories)
python3 smps4tool.py extract --archive-dir /game --archive p000045 --output out/ --flat

# Skip unnamed assets (hex IDs only)
python3 smps4tool.py extract --archive-dir /game --archive p000045 --output out/ --skip-hex
```

**Localization language detection**: When extracting archives with duplicate filenames (e.g. `localization_all.localization` × 32 languages), the tool automatically detects the actual language from file content using the `TEST_ALL_LANG` key inside each file, and appends the correct suffix:

```
localization_all.localization.en-US     ← English (US)
localization_all.localization.ja        ← Japanese
localization_all.localization.fr        ← French
localization_all.localization.de        ← German
localization_all.localization.zh-Hant   ← Chinese Traditional
localization_all.localization.ko        ← Korean
localization_all.localization.es-LA     ← Spanish (Latin America)
localization_all.localization.pt-BR     ← Portuguese (Brazil)
...
```

All 32 language variants are correctly identified, including distinguishing between regional variants (en-US/en-GB, fr/fr-CA, es/es-LA, pt/pt-BR).

### `repack` — Rebuild archive from original
```bash
python3 smps4tool.py repack --archive-dir /game --archive p000045 \
    --output-archive p000045_new --output-toc toc.new

# Exclude hex-ID assets
python3 smps4tool.py repack --archive-dir /game --archive p000045 \
    --output-archive p000045_new --output-toc toc.new --skip-hex
```

### `repack-dir` — Rebuild archive from extracted directory
```bash
python3 smps4tool.py repack-dir --archive-dir /game --archive p000045 \
    --dir extracted/ --output-archive p000045_new --output-toc toc.new --flat
```

Files not found in the directory are read from the original archive. Language suffixes on localization files are stripped automatically during repack.

### `loc-export` — Export localization → CSV
```bash
python3 smps4tool.py loc-export localization_all.localization.en-US strings.csv
# Exported 54,010 strings to strings.csv
```

Output CSV has 3 columns: `key`, `source`, `translation`. Open in Excel or Google Sheets and fill in the `translation` column.

### `loc-import` — Import translated CSV → localization file
```bash
python3 smps4tool.py loc-import original.localization translated.csv output.localization
```

Only rows with a non-empty `translation` column are imported. All other strings keep their original values.

### Other commands

| Command | Description |
|---|---|
| `build-hashdb` | Build hash DB from dag (run once) |
| `csv` | Export full asset list to CSV |
| `hash` | Compute CRC-64 hash for a path string |
| `dag` | Search DAG asset names |

---

## Translation Workflow

Full workflow to translate the game into another language:

```bash
# 1. Extract localization files from archive
python3 smps4tool.py extract --archive-dir /game --archive p000115 --output loc/ --flat

# 2. Export English strings to CSV (54,010 strings)
python3 smps4tool.py loc-export loc/localization_localization_all.localization.en-US strings.csv

# 3. Translate: fill in the "translation" column in strings.csv

# 4. Import translations back into the English localization file
python3 smps4tool.py loc-import \
    loc/localization_localization_all.localization.en-US \
    strings.csv \
    loc/localization_localization_all.localization.en-US

# 5. Repack archive + TOC
python3 smps4tool.py repack-dir --archive-dir /game --archive p000115 \
    --dir loc/ --output-archive p000115_new --output-toc toc.new --flat
```

---

## Python Library Usage

```python
from smps4tool import TOC, ArchiveReader, sm_hash, loc_export, loc_import

# Load TOC
toc = TOC('toc', hashdb_path='PS4AssetHashes.txt')
toc.load()

# Find and read an asset
asset = toc.get_by_name(r'characters\hero\hero_spiderman\hero_spiderman.model')
reader = ArchiveReader('/path/to/game')
data = reader.read_asset(asset)

# Search
for a in toc.search('vulture'):
    print(a.filename)

# Hash
h = sm_hash(r'characters\hero\hero_spiderman\hero_spiderman.model')
print(f'0x{h:016X}')

# Localization
loc_export('localization.en-US', 'strings.csv')
loc_import('localization.en-US', 'translated.csv', 'localization_new.en-US')
```

---

## PS4 File Structure

```
toc                         ← Master index of all assets
  Magic: 0xAF12AF77 → zlib → DAT1 (6 sections, stride 24 bytes)

dag                         ← Asset name strings (386k names)
  Magic: 0x891F77AF → zlib → null-terminated strings from offset 102

g00s000, g00s001, ...       ← Large archives (gameplay, textures, models)
p000026, p000027, ...       ← Small archives (localization, configs)
a00s019.us, a00s020.fr, ... ← Locale-specific archives

Archive format: Raw concat   (PC uses RDPA + custom LZ)
Asset format:   LZ4 header (0x24 bytes) + compressed DAT1 content
```

### Localization format

Each `.localization` asset is LZ4-compressed DAT1 containing:

| Section ID | Type | Contents |
|---|---|---|
| `0x4D73CEBD` | String data | Key strings (asset path keys) |
| `0xA4EA55B2` | int[] | Key offsets |
| `0x70A382B8` | String data | Translation strings |
| `0xF80DEEB4` | int[] | Translation offsets |

Compatible with [team-waldo/InsomniacArchive](https://github.com/team-waldo/InsomniacArchive) format. Works with both PS4 and PC localization files (same LZ4+DAT1 structure).

---

## Bugfixes

**Archive name truncation** — Original read archive names as fixed 8 bytes. Archives with longer names (`a00s019.us`, `a00s020.fr`, etc.) were truncated and could not be found. Fixed by reading null-terminated strings.

**Language detection** — Originally used PS4 system language index which did not match the actual language order in game archives. Now detects language from file content using the `TEST_ALL_LANG` key inside each localization asset. Verified 32/32 files correctly identified.

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
python3 smps4tool.py build-hashdb --dag dag    # รันครั้งเดียว
python3 smps4tool.py info                       # ตรวจสอบ
```

---

### คำสั่งทั้งหมด

| คำสั่ง | คำอธิบาย |
|---|---|
| `build-hashdb` | สร้าง hash DB จาก dag (รันครั้งเดียว) |
| `info` | ดูข้อมูล TOC |
| `list` | ค้นหา asset (`--search`, `--archive`, `--named-only`) |
| `extract` | Extract asset (`--skip-hex`, `--flat`) |
| `repack` | สร้าง archive ใหม่จาก original (`--skip-hex`) |
| `repack-dir` | สร้าง archive ใหม่จาก directory (`--flat`) |
| `loc-export` | แปลง localization → CSV สำหรับแปลภาษา |
| `loc-import` | นำเข้า CSV ที่แปลแล้ว → localization ใหม่ |
| `csv` | Export รายการ asset ทั้งหมดเป็น CSV |
| `hash` | คำนวณ CRC-64 hash |
| `dag` | ค้นหาชื่อ asset จาก dag |

---

### ตรวจจับภาษาอัตโนมัติ

เมื่อ extract ไฟล์ localization ที่ชื่อซ้ำกัน (32 ภาษา) tool จะตรวจจับภาษาจริงจากเนื้อหาไฟล์โดยอ่าน key `TEST_ALL_LANG` ที่อยู่ภายใน แล้วตั้งชื่อ suffix ให้ถูกต้อง:

```
localization_all.localization.en-US     ← English (US)
localization_all.localization.en-GB     ← English (UK)
localization_all.localization.ja        ← Japanese
localization_all.localization.fr        ← French
localization_all.localization.fr-CA     ← French (Canada)
localization_all.localization.es        ← Spanish
localization_all.localization.es-LA     ← Spanish (Latin America)
localization_all.localization.pt        ← Portuguese
localization_all.localization.pt-BR     ← Portuguese (Brazil)
...
```

ทดสอบแล้ว 32/32 ไฟล์ถูกต้อง รวมถึงแยก regional variants ได้ (en-US/en-GB, fr/fr-CA, es/es-LA, pt/pt-BR)

---

### ขั้นตอนแปลภาษา

```bash
# 1. Extract ไฟล์ localization จาก archive p000115
python3 smps4tool.py extract --archive-dir /game --archive p000115 --output loc/ --flat

# 2. Export เป็น CSV (54,010 strings)
python3 smps4tool.py loc-export loc/localization_localization_all.localization.en-US strings.csv

# 3. แปลภาษา: เปิด strings.csv ใน Excel แล้วใส่คำแปลในคอลัมน์ "translation"

# 4. Import กลับ
python3 smps4tool.py loc-import \
    loc/localization_localization_all.localization.en-US \
    strings.csv \
    loc/localization_localization_all.localization.en-US

# 5. Repack archive + TOC
python3 smps4tool.py repack-dir --archive-dir /game --archive p000115 \
    --dir loc/ --output-archive p000115_new --output-toc toc.new --flat
```

---

### Bugfixes

- **Archive name truncation** — ชื่อ archive ที่ยาวกว่า 8 ตัวอักษร (เช่น `a00s019.us`) ถูกตัด → แก้แล้ว
- **Language detection** — เดิมใช้ PS4 system language index ซึ่งไม่ตรงกับลำดับจริง → แก้เป็นตรวจจับจากเนื้อหาไฟล์ด้วย `TEST_ALL_LANG` key ทดสอบ 32/32 ถูกต้อง

---

### Credits

- **[jedijosh920](https://www.nexusmods.com/marvelsspidermanremastered/mods/51)** — SMPCTool ต้นฉบับ (PC)
- **[Phew](https://github.com/Phew/SMPCTool-src)** — ซอร์สโค้ด SMPCTool
- **[zerlkung](https://github.com/zerlkung/SMPCTool-PS4)** — SMPCTool-PS4 เวอร์ชัน C#
- **[team-waldo / akintos](https://github.com/team-waldo/InsomniacArchive)** — InsomniacArchive & SpidermanLocalizationTool (อ้างอิง section IDs ของ localization DAT1, LZ4 asset format, workflow export/import CSV)
- Hash algorithm reverse-engineered จาก SMPS4HashTool.exe
