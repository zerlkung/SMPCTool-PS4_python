# SMPCTool-PS4 Python 🕷️

**Spider-Man PS4 Asset Tool** — A Python rewrite of [SMPCTool-PS4](https://github.com/zerlkung/SMPCTool-PS4) (C#) for managing Marvel's Spider-Man game files on PS4.

Single-file, pure Python 3, zero external dependencies. Works as both a CLI tool and a Python library.

> 🇹🇭 [อ่านเป็นภาษาไทย / Thai version](#ภาษาไทย)

---

## Differences from the Original (C#)

| | Original (C#) | Python Rewrite |
|---|---|---|
| **Language** | C# (.NET Framework 4.7.2 / .NET 8) | Python 3 (pure, no deps) |
| **Files** | Multi-file solution | Single file, 584 lines |
| **Hash function** | Requires SMPS4HashTool.exe | Native Python (reverse-engineered CRC-64) |
| **Mod system** | Separate GUI/CLI | Built-in: create/install/uninstall .smpcmod |
| **Platform** | Windows only (.NET) | Cross-platform |

## Bugfix from v2 Original

**Archive name truncation** — The original v2 read archive names as a fixed 8-byte field, causing localized audio archives like `a00s019.us`, `a00s020.fr`, `a00s021.de` to be truncated to `a00s019.`, `a00s020.`, `a00s021.` — making them impossible to search or extract by name.

**Fix**: Changed `_parse_archives()` to read null-terminated strings instead of a fixed 8-byte window.

Affected archives (all 9 localized audio):

```
a00s019.us  a00s020.fr  a00s021.de  a00s022.it  a00s024.pl
a00s025.pt  a00s026.ru  a00s027.es  a00s028.ar
```

---

## First-Time Setup

```bash
# Step 1: Build PS4AssetHashes.txt from the dag file
# Run once — takes ~12 seconds, produces a 44 MB file
python3 smps4tool.py build-hashdb --dag dag

# Step 2: Verify everything loads correctly
python3 smps4tool.py info
```

> **Note**: The included `PS4AssetHashes.txt` is a pre-built hash DB (386,344 entries) ready to use — you can skip step 1 if you already have it.

---

## Commands

### `build-hashdb` — Build hash database (run once)
```bash
python3 smps4tool.py build-hashdb --dag dag
# Output: PS4AssetHashes.txt (386,344 entries, 44 MB)
```

### `info` — TOC summary
```bash
python3 smps4tool.py info
```
```
TOC Summary:
  Archives    : 116
  Total assets: 657,831
  Named assets: 222,757 (33%)
  Hash DB     : 386,344 entries
```

### `list` — Search assets
```bash
# Search by name
python3 smps4tool.py list --search "vulture"

# List all assets in an archive
python3 smps4tool.py list --archive g00s000

# Named assets only (skip hex IDs)
python3 smps4tool.py list --archive g00s008 --named-only --limit 20
```

### `extract` — Extract assets
```bash
# Extract entire archive
python3 smps4tool.py extract --archive-dir /path/to/game --archive p000045 --output out/

# Extract by exact name
python3 smps4tool.py extract --archive-dir /path/to/game \
    --name "characters\hero\hero_spiderman\hero_spiderman.model" --output out/

# Extract by Asset ID (hex)
python3 smps4tool.py extract --archive-dir /path/to/game \
    --id 0x800035F1EBDCBCEC --output out/

# Search and extract multiple files
python3 smps4tool.py extract --archive-dir /path/to/game \
    --search "npc_vulture" --output out/

# Flat output (no subdirectories)
python3 smps4tool.py extract --archive-dir /path/to/game \
    --search "npc_vulture" --output out/ --flat
```

### `csv` — Export full asset list
```bash
python3 smps4tool.py csv --output assets.csv
# 657,831 rows: Asset Path, Asset ID, Archive, Offset, Size
```

### `hash` — Compute hash for a path string
```bash
python3 smps4tool.py hash "textures\glass\jn_shattered_glass\jn_shattered_glass_c.texture"
# 0x800035F1EBDCBCEC  (decimal: 9223431350015278316)
```

### `dag` — Search DAG names or build hash DB
```bash
# Search names
python3 smps4tool.py dag --dag dag --search "scarlet"

# Export all names
python3 smps4tool.py dag --dag dag --output all_names.txt
```

### `create-mod` — Create .smpcmod
```bash
python3 smps4tool.py create-mod \
    --archive-dir /path/to/game \
    --title "My Texture Mod" --author "MyName" \
    --assets "characters\hero\hero_spiderman\textures\hero_spiderman_n.texture" \
    --files my_new_normal.texture
```

### `install-mod` — Install mod
```bash
python3 smps4tool.py install-mod \
    --archive-dir /path/to/game My_Texture_Mod.smpcmod
# Automatically backs up toc as toc.BAK
```

### `uninstall` — Uninstall all mods
```bash
python3 smps4tool.py uninstall
# Restores toc from toc.BAK
```

---

## Python Library Usage

```python
from smps4tool import TOC, ArchiveReader, sm_hash, build_hash_db_from_dag

# Load TOC with hash DB
toc = TOC('toc', hashdb_path='PS4AssetHashes.txt')
toc.load()

# Find an asset
asset = toc.get_by_name(r'characters\hero\hero_spiderman\hero_spiderman.model')
print(f'Archive: {asset.archive_name}')
print(f'Offset:  0x{asset.archive_offset:08X}')
print(f'Size:    {asset.file_size:,} bytes')

# Read asset bytes
reader = ArchiveReader('/path/to/game')
data = reader.read_asset(asset)

# Fuzzy search
for a in toc.search('vulture'):
    print(a.filename)

# Compute hash
h = sm_hash(r'characters\hero\hero_spiderman\hero_spiderman.model')
print(f'0x{h:016X}')
```

---

## PS4 File Structure

```
toc                         ← Master index of all assets
  Magic: 0xAF12AF77
  → zlib decompress → DAT1 format
  → 6 sections:
      ArchiveFiles   [stride 24 bytes]  (PC uses 72 bytes)
      AssetIDs       [8 bytes each]
      SizeEntries    [12 bytes each]
      KeyAssets      [8 bytes each]
      OffsetEntries  [8 bytes each]
      SpansEntries   [8 bytes each]

dag                         ← All asset names (386k strings)
  Magic: 0x891F77AF
  → zlib decompress → strings from offset 102

g00s000, g00s001, ...       ← Large archives (gameplay, textures, models)
p000026, p000027, ...       ← Small archives (localization, configs)
a00s019.us, a00s020.fr, ... ← Audio archives (locale-specific)

Archive format: Raw concat   (PC uses RDPA + custom LZ)
Asset format:   0xBA20AFB5 wrapper + DAT1 content
```

---

## Hash Algorithm

Custom CRC-64 by Insomniac Games — reverse-engineered from SMPS4HashTool.exe (native x64).

- **Case-insensitive** — A-Z automatically lowered
- **Path separator normalised** — `/` and `\` treated identically
- **Output** — bit 63 always set (range `0x8000...` to `0xFFFF...`)
- **No SMPS4HashTool.exe required** — fully implemented in Python

---

## Why are ~66% of assets still hex IDs?

These are anonymous assets with no string path in the game data — procedurally generated geometry, runtime-computed resources, or assets referenced directly by hash without a name string. This is normal for the Insomniac engine; the PC version has the same ratio.

---

## Files in This Repo

| File | Description |
|---|---|
| `smps4tool.py` | Main tool (584 LOC, with bugfix) |
| `PS4AssetHashes.txt` | Pre-built hash DB — 386,344 entries (44 MB) |
| `SMPS4HashTool.exe` | Original native hash tool (reference only) |
| `README.md` | This document |

---

## Credits

- **[jedijosh920](https://www.nexusmods.com/marvelsspidermanremastered/mods/51)** — Original SMPCTool developer (PC)
- **[Phew](https://github.com/Phew/SMPCTool-src)** — Published SMPCTool source code
- **[zerlkung](https://github.com/zerlkung/SMPCTool-PS4)** — SMPCTool-PS4 C# version for PS4
- **Hash algorithm** — Reverse-engineered from SMPS4HashTool.exe (native x64)
- **Python port** — Based on direct binary analysis of PS4 game files

---
---

# ภาษาไทย

## SMPCTool-PS4 Python 🕷️

**Spider-Man PS4 Asset Tool** — Python rewrite ของ [SMPCTool-PS4](https://github.com/zerlkung/SMPCTool-PS4) (C#) สำหรับจัดการไฟล์เกม Marvel's Spider-Man บน PS4

ไฟล์เดียว, pure Python 3, ไม่ต้องติดตั้ง dependency ภายนอก ใช้ได้ทั้งเป็น CLI tool และ Python library

---

### ความแตกต่างจาก Original (C#)

| | Original (C#) | Python Rewrite |
|---|---|---|
| **ภาษา** | C# (.NET Framework 4.7.2 / .NET 8) | Python 3 (pure, no deps) |
| **ไฟล์** | หลายไฟล์ + solution | ไฟล์เดียว 584 บรรทัด |
| **Hash function** | ต้องเรียก SMPS4HashTool.exe | Implement ใน Python (reverse-engineered CRC-64) |
| **Mod system** | ผ่าน GUI/CLI แยก | Built-in: create/install/uninstall .smpcmod |
| **Platform** | Windows only (.NET) | Cross-platform (Python 3) |

### Bugfix จาก v2 Original

**Archive name truncation** — ไฟล์ v2 ดั้งเดิมอ่านชื่อ archive แค่ 8 bytes ทำให้ localized audio archives เช่น `a00s019.us`, `a00s020.fr`, `a00s021.de` ถูกตัดเหลือ `a00s019.`, `a00s020.`, `a00s021.` → ค้นหา/extract ไม่ได้

**แก้ไข**: เปลี่ยน `_parse_archives()` ให้อ่าน null-terminated string แทน fixed 8 bytes

---

### การใช้งานครั้งแรก (สำคัญมาก!)

```bash
# ขั้นที่ 1: สร้าง PS4AssetHashes.txt จากไฟล์ dag (รันแค่ครั้งเดียว)
python3 smps4tool.py build-hashdb --dag dag

# ขั้นที่ 2: ตรวจสอบว่าโหลดได้ปกติ
python3 smps4tool.py info
```

> **หมายเหตุ**: ไฟล์ `PS4AssetHashes.txt` ที่แนบมาใน repo คือ hash DB ที่ build เรียบร้อยแล้ว (386,344 entries) สามารถใช้ได้เลย

---

### คำสั่งทั้งหมด

#### `build-hashdb` — สร้าง hash database (รันครั้งเดียว)
```bash
python3 smps4tool.py build-hashdb --dag dag
```

#### `info` — ดูข้อมูล TOC
```bash
python3 smps4tool.py info
```

#### `list` — ค้นหา asset
```bash
python3 smps4tool.py list --search "vulture"
python3 smps4tool.py list --archive g00s000
python3 smps4tool.py list --archive g00s008 --named-only --limit 20
```

#### `extract` — extract asset ออกมา
```bash
# Extract ทั้ง archive
python3 smps4tool.py extract --archive-dir /path/to/game --archive p000045 --output out/

# Extract ด้วยชื่อ
python3 smps4tool.py extract --archive-dir /path/to/game \
    --name "characters\hero\hero_spiderman\hero_spiderman.model" --output out/

# Extract ด้วย Asset ID (hex)
python3 smps4tool.py extract --archive-dir /path/to/game \
    --id 0x800035F1EBDCBCEC --output out/

# ค้นหาและ extract หลายไฟล์
python3 smps4tool.py extract --archive-dir /path/to/game \
    --search "npc_vulture" --output out/
```

#### `csv` — export รายการ asset ทั้งหมด
```bash
python3 smps4tool.py csv --output assets.csv
```

#### `hash` — คำนวณ hash จากชื่อ
```bash
python3 smps4tool.py hash "textures\glass\jn_shattered_glass\jn_shattered_glass_c.texture"
```

#### `dag` — ค้นหาชื่อ asset จากไฟล์ dag
```bash
python3 smps4tool.py dag --dag dag --search "scarlet"
```

#### `create-mod` — สร้าง .smpcmod
```bash
python3 smps4tool.py create-mod \
    --archive-dir /path/to/game \
    --title "My Texture Mod" --author "MyName" \
    --assets "characters\hero\hero_spiderman\textures\hero_spiderman_n.texture" \
    --files my_new_normal.texture
```

#### `install-mod` — ติดตั้ง mod
```bash
python3 smps4tool.py install-mod \
    --archive-dir /path/to/game My_Texture_Mod.smpcmod
# สำรอง toc เป็น toc.BAK อัตโนมัติ
```

#### `uninstall` — ถอน mod ทั้งหมด
```bash
python3 smps4tool.py uninstall
# คืนค่า toc จาก toc.BAK
```

---

### ใช้เป็น Python Library

```python
from smps4tool import TOC, ArchiveReader, sm_hash, build_hash_db_from_dag

toc = TOC('toc', hashdb_path='PS4AssetHashes.txt')
toc.load()

asset = toc.get_by_name(r'characters\hero\hero_spiderman\hero_spiderman.model')
print(f'Archive: {asset.archive_name}, Size: {asset.file_size:,} bytes')

reader = ArchiveReader('/path/to/game')
data = reader.read_asset(asset)

# ค้นหา
for a in toc.search('vulture'):
    print(a.filename)

# คำนวณ hash
h = sm_hash(r'characters\hero\hero_spiderman\hero_spiderman.model')
print(f'0x{h:016X}')
```

---

### โครงสร้างไฟล์ PS4

```
toc                         ← index ของทุก asset (Magic: 0xAF12AF77)
dag                         ← รายชื่อ asset 386k ชื่อ (Magic: 0x891F77AF)
g00s000, g00s001, ...       ← archive ใหญ่ (gameplay, textures, models)
p000026, p000027, ...       ← archive เล็ก (localization, configs)
a00s019.us, a00s020.fr, ... ← archive audio (แยกตามภาษา)
```

- Archive format: Raw concat (ไม่มี compression, PC ใช้ RDPA+LZ)
- Asset format: `0xBA20AFB5` wrapper + DAT1 content
- Archive stride: 24 bytes (PC ใช้ 72 bytes)

---

### Hash Algorithm

Custom CRC-64 ของ Insomniac Games — reverse-engineered จาก SMPS4HashTool.exe

- **Case-insensitive** — A-Z → a-z อัตโนมัติ
- **Path separator normalised** — `/` และ `\` ถือว่าเหมือนกัน
- **ผลลัพธ์** — bit 63 เซตเสมอ (`0x8000...` ถึง `0xFFFF...`)

### ทำไม 66% ยังเป็น hex ID?

เป็น anonymous assets ที่ไม่มี string path ในเกม เช่น procedurally generated geometry, runtime-computed resources หรือ assets ที่อ้างอิงด้วย hash โดยตรง — ปกติสำหรับ Insomniac engine ทั้ง PC และ PS4

---

### Credits

- **[jedijosh920](https://www.nexusmods.com/marvelsspidermanremastered/mods/51)** — ผู้พัฒนา SMPCTool ต้นฉบับ (PC)
- **[Phew](https://github.com/Phew/SMPCTool-src)** — ผู้เผยแพร่ซอร์สโค้ด
- **[zerlkung](https://github.com/zerlkung/SMPCTool-PS4)** — ผู้พัฒนา SMPCTool-PS4 เวอร์ชัน C#
