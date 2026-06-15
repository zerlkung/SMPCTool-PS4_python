#!/usr/bin/env python3
# sm2.py — Marvel's Spider-Man 2 (PS5/PC)
# I29 TOC format: direct DAT1, 66-byte archives, 16-byte SizeEntries, TTF fonts
"""
SM2 Tool - Spider-Man 2 PS5/PC Asset Tool

SM2 uses I29 format (same as Ratchet & Clank: Rift Apart):
- TOC: magic 0x34E89035, raw DAT1 (no compression)
- Archives: UTF-16LE names, variable-length entries
- SizeEntries: 16 bytes = (file_size, archive_index, archive_offset, flags)
- Localization: direct DAT1 (no LZ4 header), 9 sections, 92,760 strings
- Font: TTF/OTF (not GFX)

Setup:  pip install lz4  (for loc-export/loc-import)
Hash DB: uses hashes.txt from Overstrike ModdingTool
         https://github.com/Tkachov/Overstrike
"""

import struct, zlib, os, sys, csv, re
from dataclasses import dataclass
from typing import Optional

# ─── Hash Function (same as SM1/MM) ────────────────────────────────────────────
_SM_TABLE = (
    0x0000000000000000,0xb32e4cbe03a75f6f,0xf4843657a840a05b,0x47aa7ae9abe7ff34,
    0x7bd0c384ff8f5e33,0xc8fe8f3afc28015c,0x8f54f5d357cffe68,0x3c7ab96d5468a107,
    0xf7a18709ff1ebc66,0x448fcbb7fcb9e309,0x0325b15e575e1c3d,0xb00bfde054f94352,
    0x8c71448d0091e255,0x3f5f08330336bd3a,0x78f572daa8d1420e,0xcbdb3e64ab761d61,
    0x7d9ba13851336649,0xceb5ed8652943926,0x891f976ff973c612,0x3a31dbd1fad4997d,
    0x064b62bcaebc387a,0xb5652e02ad1b6715,0xf2cf54eb06fc9821,0x41e11855055bc74e,
    0x8a3a2631ae2dda2f,0x39146a8fad8a8540,0x7ebe1066066d7a74,0xcd905cd805ca251b,
    0xf1eae5b551a2841c,0x42c4a90b5205db73,0x056ed3e2f9e22447,0xb6409f5cfa457b28,
    0xfb374270a266cc92,0x48190ecea1c193fd,0x0fb374270a266cc9,0xbc9d3899098133a6,
    0x80e781f45de992a1,0x33c9cd4a5e4ecdce,0x7463b7a3f5a932fa,0xc74dfb1df60e6d95,
    0x0c96c5795d7870f4,0xbfb889c75edf2f9b,0xf812f32ef538d0af,0x4b3cbf90f69f8fc0,
    0x774606fda2f72ec7,0xc4684a43a15071a8,0x83c230aa0ab78e9c,0x30ec7c140910d1f3,
    0x86ace348f355aadb,0x3582aff6f0f2f5b4,0x7228d51f5b150a80,0xc10699a158b255ef,
    0xfd7c20cc0cdaf4e8,0x4e526c720f7dab87,0x09f8169ba49a54b3,0xbad65a25a73d0bdc,
    0x710d64410c4b16bd,0xc22328ff0fec49d2,0x85895216a40bb6e6,0x36a71ea8a7ace989,
    0x0adda7c5f3c4488e,0xb9f3eb7bf06317e1,0xfe5991925b84e8d5,0x4d77dd2c5823b7ba,
    0x64b62bcaebc387a1,0xd7986774e864d8ce,0x90321d9d438327fa,0x231c512340247895,
    0x1f66e84e144cd992,0xac48a4f017eb86fd,0xebe2de19bc0c79c9,0x58cc92a7bfab26a6,
    0x9317acc314dd3bc7,0x2039e07d177a64a8,0x67939a94bc9d9b9c,0xd4bdd62abf3ac4f3,
    0xe8c76f47eb5265f4,0x5be923f9e8f53a9b,0x1c4359104312c5af,0xaf6d15ae40b59ac0,
    0x192d8af2baf0e1e8,0xaa03c64cb957be87,0xeda9bca512b041b3,0x5e87f01b11171edc,
    0x62fd4976457fbfdb,0xd1d305c846d8e0b4,0x96797f21ed3f1f80,0x2557339fee9840ef,
    0xee8c0dfb45ee5d8e,0x5da24145464902e1,0x1a083bacedaefdd5,0xa9267712ee09a2ba,
    0x955cce7fba6103bd,0x267282c1b9c65cd2,0x61d8f8281221a3e6,0xd2f6b4961186fc89,
    0x9f8169ba49a54b33,0x2caf25044a02145c,0x6b055fede1e5eb68,0xd82b1353e242b407,
    0xe451aa3eb62a1500,0x577fe680b58d4a6f,0x10d59c691e6ab55b,0xa3fbd0d71dcdea34,
    0x6820eeb3b6bbf755,0xdb0ea20db51ca83a,0x9ca4d8e41efb570e,0x2f8a945a1d5c0861,
    0x13f02d374934a966,0xa0de61894a93f609,0xe7741b60e174093d,0x545a57dee2d35652,
    0xe21ac88218962d7a,0x5134843c1b317215,0x169efed5b0d68d21,0xa5b0b26bb371d24e,
    0x99ca0b06e7197349,0x2ae447b8e4be2c26,0x6d4e3d514f59d312,0xde6071ef4cfe8c7d,
    0x15bb4f8be788911c,0xa6950335e42fce73,0xe13f79dc4fc83147,0x521135624c6f6e28,
    0x6e6b8c0f1807cf2f,0xdd45c0b11ba09040,0x9aefba58b0476f74,0x29c1f6e6b3e0301b,
    0xc96c5795d7870f42,0x7a421b2bd420502d,0x3de861c27fc7af19,0x8ec62d7c7c60f076,
    0xb2bc941128085171,0x0192d8af2baf0e1e,0x4638a2468048f12a,0xf516eef883efae45,
    0x3ecdd09c2899b324,0x8de39c222b3eec4b,0xca49e6cb80d9137f,0x7967aa75837e4c10,
    0x451d1318d716ed17,0xf6335fa6d4b1b278,0xb199254f7f564d4c,0x02b769f17cf11223,
    0xb4f7f6ad86b4690b,0x07d9ba1385133664,0x4073c0fa2ef4c950,0xf35d8c442d53963f,
    0xcf273529793b3738,0x7c0979977a9c6857,0x3ba3037ed17b9763,0x888d4fc0d2dcc80c,
    0x435671a479aad56d,0xf0783d1a7a0d8a02,0xb7d247f3d1ea7536,0x04fc0b4dd24d2a59,
    0x3886b22086258b5e,0x8ba8fe9e8582d431,0xcc0284772e652b05,0x7f2cc8c92dc2746a,
    0x325b15e575e1c3d0,0x8175595b76469cbf,0xc6df23b2dda1638b,0x75f16f0cde063ce4,
    0x498bd6618a6e9de3,0xfaa59adf89c9c28c,0xbd0fe036222e3db8,0x0e21ac88218962d7,
    0xc5fa92ec8aff7fb6,0x76d4de52895820d9,0x317ea4bb22bfdfed,0x8250e80521188082,
    0xbe2a516875702185,0x0d041dd676d77eea,0x4aae673fdd3081de,0xf9802b81de97deb1,
    0x4fc0b4dd24d2a599,0xfceef8632775faf6,0xbb44828a8c9205c2,0x086ace348f355aad,
    0x34107759db5dfbaa,0x873e3be7d8faa4c5,0xc094410e731d5bf1,0x73ba0db070ba049e,
    0xb86133d4dbcc19ff,0x0b4f7f6ad86b4690,0x4ce50583738cb9a4,0xffcb493d702be6cb,
    0xc3b1f050244347cc,0x709fbcee27e418a3,0x3735c6078c03e797,0x841b8ab98fa4b8f8,
    0xadda7c5f3c4488e3,0x1ef430e13fe3d78c,0x595e4a08940428b8,0xea7006b697a377d7,
    0xd60abfdbc3cbd6d0,0x6524f365c06c89bf,0x228e898c6b8b768b,0x91a0c532682c29e4,
    0x5a7bfb56c35a3485,0xe955b7e8c0fd6bea,0xaeffcd016b1a94de,0x1dd181bf68bdcbb1,
    0x21ab38d23cd56ab6,0x9285746c3f7235d9,0xd52f0e859495caed,0x6601423b97329582,
    0xd041dd676d77eeaa,0x636f91d96ed0b1c5,0x24c5eb30c5374ef1,0x97eba78ec690119e,
    0xab911ee392f8b099,0x18bf525d915feff6,0x5f1528b43ab810c2,0xec3b640a391f4fad,
    0x27e05a6e926952cc,0x94ce16d091ce0da3,0xd3646c393a29f297,0x604a2087398eadf8,
    0x5c3099ea6de60cff,0xef1ed5546e415390,0xa8b4afbdc5a6aca4,0x1b9ae303c601f3cb,
    0x56ed3e2f9e224471,0xe5c372919d851b1e,0xa26908783662e42a,0x114744c635c5bb45,
    0x2d3dfdab61ad1a42,0x9e13b115620a452d,0xd9b9cbfcc9edba19,0x6a978742ca4ae576,
    0xa14cb926613cf817,0x1262f598629ba778,0x55c88f71c97c584c,0xe6e6c3cfcadb0723,
    0xda9c7aa29eb3a624,0x69b2361c9d14f94b,0x2e184cf536f3067f,0x9d36004b35545910,
    0x2b769f17cf112238,0x9858d3a9ccb67d57,0xdff2a94067518263,0x6cdce5fe64f6dd0c,
    0x50a65c93309e7c0b,0xe388102d33392364,0xa4226ac498dedc50,0x170c267a9b79833f,
    0xdcd7181e300f9e5e,0x6ff954a033a8c131,0x28532e49984f3e05,0x9b7d62f79be8616a,
    0xa707db9acf80c06d,0x14299724cc279f02,0x5383edcd67c06036,0xe0ada17364673f59,
)

def sm_hash(path: str) -> int:
    SEP = 0x2f; h = 0xc96c5795d7870f42; i = 0
    raw = path.encode('ascii', errors='replace')
    while i < len(raw):
        c = raw[i]
        if c == 0x5c or c == SEP:
            while i < len(raw) and (raw[i] == 0x5c or raw[i] == SEP): i += 1
            c = SEP
        else:
            i += 1
            if 0x41 <= c <= 0x5A: c += 0x20
        h = _SM_TABLE[(h & 0xFF) ^ c] ^ (h >> 8)
    return (h >> 2) | 0x8000000000000000


# ─── Constants ────────────────────────────────────────────────────────────────
TOC_MAGIC  = 0x34E89035   # I29 format (SM2, Rift Apart)
DAT1_MAGIC = 0x44415431

# Loc section IDs (same as PS5)
_LOC_KEY_DATA = 0x4D73CEBD
_LOC_KEY_OFF  = 0xA4EA55B2
_LOC_TR_DATA  = 0x70A382B8
_LOC_TR_OFF   = 0xF80DEEB4

# Known asset hashes
HASH_FONT = 0x8143F7F3648B4470   # Azbuka Pro Medium Italic (TTF)
HASH_LOC  = 0xBE55D94F171BF8DE   # localization_all.localization


# ─── Data Classes ─────────────────────────────────────────────────────────────
@dataclass
class Section:
    hash: int; offset: int; size: int

@dataclass
class ArchiveFile:
    index: int; filename: str

@dataclass
class AssetEntry:
    asset_id: int; filename: str
    archive_index: int; archive_name: str
    archive_offset: int; file_size: int
    flags: int = 0xFFFFFFFF


# ─── TOC ──────────────────────────────────────────────────────────────────────
class TOC:
    def __init__(self, toc_path: str, hashdb_path: Optional[str] = None):
        self.toc_path = toc_path
        self.raw_data = b''; self.dec_data = b''
        self.sections: list[Section] = []
        self.archive_files: list[ArchiveFile] = []
        self.assets: list[AssetEntry] = []
        self.hash_db: dict[int,str] = {}
        if hashdb_path and os.path.exists(hashdb_path):
            self._load_hashdb(hashdb_path)

    def _load_hashdb(self, path: str) -> None:
        """Load hashes.txt from Overstrike ModdingTool.
        Format: hash,name,game_id (game_id=32 for SM2)
        """
        with open(path, 'r', errors='replace') as f:
            for line in f:
                line = line.strip()
                if ',' not in line: continue
                parts = line.split(',')
                if len(parts) >= 2:
                    try:
                        h = int(parts[0], 16) & 0xFFFFFFFFFFFFFFFF
                        if parts[1]:  # has name
                            self.hash_db[h] = parts[1]
                    except ValueError:
                        pass

    def name_for(self, aid: int) -> str:
        return self.hash_db.get(aid, f'0x{aid:016X}')

    def load(self) -> None:
        print(f'Loading TOC: {self.toc_path}')
        with open(self.toc_path, 'rb') as f:
            self.raw_data = f.read()

        if struct.unpack('<I', self.raw_data[:4])[0] != TOC_MAGIC:
            raise ValueError(f'Bad TOC magic: 0x{struct.unpack("<I", self.raw_data[:4])[0]:08X}')

        dec_size = struct.unpack('<I', self.raw_data[4:8])[0]
        # I29: raw DAT1, no compression
        self.dec_data = self.raw_data[8:8+dec_size]
        if len(self.dec_data) != dec_size:
            raise ValueError(f'Short TOC data: {len(self.dec_data)}/{dec_size}')

        print(f'Loaded ({dec_size:,} bytes)')
        self._parse()
        named = sum(1 for a in self.assets if not a.filename.startswith('0x'))
        print(f'Ready: {len(self.archive_files)} archives, '
              f'{len(self.assets):,} assets, '
              f'{named:,} named ({100*named//max(len(self.assets),1)}%)')

    def _parse(self) -> None:
        d = self.dec_data
        if struct.unpack('<I', d[0:4])[0] != DAT1_MAGIC:
            raise ValueError('Not DAT1')

        n = struct.unpack('<I', d[12:16])[0]
        pos = 16
        for _ in range(n):
            h, o, s = struct.unpack('<III', d[pos:pos+12])
            self.sections.append(Section(h, o, s))
            pos += 12

        # Section layout (I29):
        # [0]=0x36A6C8CC AssetHeaders, [1]=0x398ABFF0 ArchivesMap,
        # [2]=0x506D7B8A AssetIDs, [3]=0x62297090 (4 bytes),
        # [4]=0x654BDED9 unknown, [5]=0x65BCF461 SizeEntries(16B),
        # [6]=0xC9FB9DDA unknown, [7]=0xEDE8ADA9 Spans
        self._parse_archives(self.sections[1])  # ArchivesMap
        self._parse_assets(self.sections[2], self.sections[5])  # AssetIDs + SizeEntries
        self._build()

    def _parse_archives(self, sec) -> None:
        """Parse ArchivesMap section — 66-byte fixed entries with ASCII names."""
        d = self.dec_data
        ARCH_ENTRY_SIZE = 66  # I29: 66 bytes per archive entry
        offset = sec.offset
        n = sec.size // ARCH_ENTRY_SIZE
        for i in range(n):
            e = d[offset + i*ARCH_ENTRY_SIZE:offset + (i+1)*ARCH_ENTRY_SIZE]
            nm = e.split(b'\x00')[0].decode('ascii', errors='replace')
            self.archive_files.append(ArchiveFile(i, nm))

    def _parse_assets(self, sec_ids, sec_sizes) -> None:
        """Parse assets from AssetIDs + SizeEntries sections.
        SizeEntries I29: (uint32 file_size, uint32 archive_index,
                          uint32 archive_offset, uint32 flags)
        """
        d = self.dec_data
        id_off = sec_ids.offset
        sz_off = sec_sizes.offset
        n = sec_ids.size // 8

        for i in range(n):
            aid = struct.unpack('<Q', d[id_off + i*8:id_off + i*8 + 8])[0]
            fsize, arch_idx, arch_off, flags = struct.unpack(
                '<IIII', d[sz_off + i*16:sz_off + i*16 + 16])

            arch_name = (self.archive_files[arch_idx].filename
                         if arch_idx < len(self.archive_files)
                         else f'archive_{arch_idx}')

            self.assets.append(AssetEntry(
                asset_id=aid, filename=self.name_for(aid),
                archive_index=arch_idx, archive_name=arch_name,
                archive_offset=arch_off, file_size=fsize,
                flags=flags))

    def _build(self) -> None:
        """Post-parse: update in-memory state (no section index fixup needed for I29)."""
        pass

    def get_by_id(self, aid: int) -> Optional[AssetEntry]:
        for a in self.assets:
            if a.asset_id == aid: return a
        return None

    def search(self, q: str) -> list[AssetEntry]:
        ql = q.lower()
        return [a for a in self.assets if ql in a.filename.lower()]

    def by_archive(self, name: str) -> list[AssetEntry]:
        nl = name.lower()
        return [a for a in self.assets if a.archive_name.lower() == nl]

    def patch_size_entry(self, asset_index: int, file_size: int,
                          archive_index: int, archive_offset: int,
                          flags: int = 0xFFFFFFFF) -> None:
        """Update SizeEntry for a specific asset index.
        SizeEntries section is [5] = 0x65BCF461.
        """
        sec_sizes = self.sections[5]
        sz_off = sec_sizes.offset + asset_index * 16
        buf = bytearray(self.dec_data)
        struct.pack_into('<IIII', buf, sz_off, file_size, archive_index, archive_offset, flags)
        self.dec_data = bytes(buf)

    def save(self, path: Optional[str] = None) -> None:
        out = path or self.toc_path
        with open(out, 'wb') as f:
            f.write(struct.pack('<I', TOC_MAGIC))
            f.write(struct.pack('<I', len(self.dec_data)))
            f.write(self.dec_data)
        print(f'TOC saved: {out} ({os.path.getsize(out):,} bytes)')


# ─── Archive Reader ───────────────────────────────────────────────────────────
class ArchiveReader:
    def __init__(self, archive_dir: str):
        self.archive_dir = archive_dir

    def read_asset(self, asset: AssetEntry) -> bytes:
        base = os.path.basename(asset.archive_name)
        path = os.path.join(self.archive_dir, 'd', base)
        if not os.path.exists(path):
            path = os.path.join(self.archive_dir, base)
        if not os.path.exists(path):
            raise FileNotFoundError(f'Not found: {path}')
        with open(path, 'rb') as f:
            f.seek(asset.archive_offset)
            data = f.read(asset.file_size)
        if len(data) != asset.file_size:
            raise IOError(f'Short read: {len(data)}/{asset.file_size}')
        return data


# ─── Localization ─────────────────────────────────────────────────────────────
def _loc_parse_sections(dec: bytes) -> dict:
    nsec = struct.unpack('<I', dec[12:16])[0]
    sections = {}
    pos = 16
    for _ in range(nsec):
        h, off, sz = struct.unpack('<III', dec[pos:pos+12])
        sections[h] = (off, sz)
        pos += 12
    return sections

def loc_export(loc_path: str, csv_path: str) -> int:
    """Export SM2 localization (raw DAT1) to CSV."""
    with open(loc_path, 'rb') as f:
        dec = f.read()

    if struct.unpack('<I', dec[:4])[0] != DAT1_MAGIC:
        raise ValueError(f'Not DAT1: 0x{struct.unpack("<I", dec[:4])[0]:08X}')

    sec = _loc_parse_sections(dec)
    kd_off, _ = sec[_LOC_KEY_DATA]
    ko_off, ko_sz = sec[_LOC_KEY_OFF]
    td_off, _ = sec[_LOC_TR_DATA]
    to_off, _ = sec[_LOC_TR_OFF]
    count = ko_sz // 4

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['key', 'source', 'translation'])
        for i in range(count):
            ko = struct.unpack('<i', dec[ko_off+i*4:ko_off+i*4+4])[0]
            to = struct.unpack('<i', dec[to_off+i*4:to_off+i*4+4])[0]
            # Read key
            kpos = kd_off + ko
            kend = dec.index(b'\x00', kpos)
            key = dec[kpos:kend].decode('utf-8', errors='replace')
            # Read value
            val = ''
            if to != 0 or key == 'INVALID':
                tpos = td_off + to
                tend = dec.index(b'\x00', tpos)
                val = dec[tpos:tend].decode('utf-8', errors='replace')
            w.writerow([key, val, ''])

    print(f'Exported {count:,} strings to {csv_path}')
    return count

def loc_import(loc_path: str, csv_path: str, out_path: str) -> int:
    """Import translated CSV back into SM2 localization (raw DAT1)."""
    # Read translations
    translations = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if len(row) >= 3 and row[2].strip():
                translations[row[0]] = row[2]
    print(f'Loaded {len(translations):,} translations from {csv_path}')

    # Read original
    with open(loc_path, 'rb') as f:
        dec = f.read()

    sec = _loc_parse_sections(dec)
    kd_off, _ = sec[_LOC_KEY_DATA]
    ko_off, ko_sz = sec[_LOC_KEY_OFF]
    td_off, td_sz = sec[_LOC_TR_DATA]
    to_off, _ = sec[_LOC_TR_OFF]
    count = ko_sz // 4

    def _read_str(buf, pos):
        end = buf.index(b'\x00', pos)
        return buf[pos:end].decode('utf-8', errors='replace')

    # Build new translation data
    new_tr_data = bytearray()
    new_tr_offsets = []
    imported = 0

    for i in range(count):
        ko = struct.unpack('<i', dec[ko_off+i*4:ko_off+i*4+4])[0]
        to = struct.unpack('<i', dec[to_off+i*4:to_off+i*4+4])[0]
        key = _read_str(dec, kd_off + ko)

        if key in translations:
            value = translations[key]
            imported += 1
        else:
            value = _read_str(dec, td_off + to) if (to != 0 or key == 'INVALID') else ''

        if key != 'INVALID' and value == '':
            new_tr_offsets.append(0)
        else:
            new_tr_offsets.append(len(new_tr_data))
            new_tr_data.extend(value.encode('utf-8') + b'\x00')

    # Rebuild DAT1: patch offsets + replace TR_DATA
    buf = bytearray(dec)
    for i in range(count):
        struct.pack_into('<i', buf, to_off + i*4, new_tr_offsets[i])

    new_td = bytes(new_tr_data)

    # Find tail sections after TR_DATA
    all_secs = sorted(sec.items(), key=lambda x: x[1][0])
    tr_idx = next(i for i, (h, _) in enumerate(all_secs) if h == _LOC_TR_DATA)
    tail_secs = all_secs[tr_idx + 1:]

    if not tail_secs:
        new_dec = bytes(buf[:td_off]) + new_td
    else:
        tail_start = tail_secs[0][1][0]
        tail_data = dec[tail_start:]
        new_dec = bytes(buf[:td_off]) + new_td + tail_data

    # Update section sizes in DAT1 header
    td_size_delta = len(new_td) - td_sz
    nsec = struct.unpack('<I', new_dec[12:16])[0]
    new_buf = bytearray(new_dec)
    pos = 16
    for _ in range(nsec):
        h = struct.unpack('<I', new_buf[pos:pos+4])[0]
        if h == _LOC_TR_DATA:
            struct.pack_into('<I', new_buf, pos+8, len(new_td))
        elif tail_secs and h in [th for th, _ in tail_secs]:
            _, (off, sz) = sec[h]
            struct.pack_into('<I', new_buf, pos+4, off + td_size_delta)
        pos += 12
    new_dec = bytes(new_buf)

    with open(out_path, 'wb') as f:
        f.write(new_dec)

    print(f'Imported {imported:,} translations, saved to {out_path}')
    print(f'  Original: {len(dec):,} bytes -> New: {len(new_dec):,} bytes')
    return imported


# ─── CLI ──────────────────────────────────────────────────────────────────────
def _auto_toc(args) -> TOC:
    hashdb = getattr(args, 'hashdb', None)
    if not hashdb or not os.path.exists(hashdb):
        for c in ['hashes.txt',
                  os.path.join(os.path.dirname(__file__), 'modding tools', 'hashes.txt'),
                  'AssetHashes.txt']:
            if os.path.exists(c): hashdb = c; break
    return TOC(args.toc, hashdb)

def cmd_info(args):
    toc = _auto_toc(args)
    toc.load()
    named = sum(1 for a in toc.assets if not a.filename.startswith('0x'))
    total = len(toc.assets)
    print(f'\n=== TOC Summary ===')
    print(f'  Archives    : {len(toc.archive_files)}')
    print(f'  Total assets: {total:,}')
    print(f'  Named assets: {named:,} ({100*named//max(total,1)}%)')
    print(f'  Hash DB     : {len(toc.hash_db):,} entries')

    # Show a few archives
    for a in toc.archive_files:
        n = sum(1 for x in toc.assets if x.archive_index == a.index)
        if n > 1000 and 'localization' in a.filename.lower():
            print(f'  [{a.index:3d}] {a.filename:<40s} {n:>10,}')
        if 'userinterface' in a.filename.lower():
            print(f'  [{a.index:3d}] {a.filename:<40s} {n:>10,}')

def cmd_list(args):
    toc = _auto_toc(args)
    toc.load()
    assets = toc.assets
    if getattr(args, 'archive', None):
        assets = [a for a in assets if args.archive in a.archive_name]
    if getattr(args, 'search', None):
        assets = toc.search(args.search)
    limit = getattr(args, 'limit', 50)
    for a in assets[:limit]:
        print(f'  [{toc.assets.index(a):>7}] {a.filename:<80s} {a.archive_name:<20s} '
              f'{a.file_size:>10,} B')
    if len(assets) > limit:
        print(f'  ... {len(assets)-limit:,} more')
    print(f'\n  Total: {len(assets):,}')

def cmd_extract(args):
    toc = _auto_toc(args)
    toc.load()
    reader = ArchiveReader(args.archive_dir)
    os.makedirs(args.output, exist_ok=True)

    if getattr(args, 'id', None):
        assets = [a for a in [toc.get_by_id(int(args.id, 16))] if a]
        if not assets:
            # Search all matching
            hid = int(args.id, 16)
            assets = [a for a in toc.assets if a.asset_id == hid]
    elif getattr(args, 'archive', None):
        assets = toc.by_archive(args.archive)
    elif getattr(args, 'search', None):
        assets = toc.search(args.search)
    else:
        print('Need --id/--archive/--search'); return

    if not assets:
        print('No assets found.'); return

    ok = err = 0
    for a in assets:
        try:
            data = reader.read_asset(a)
            fname = a.filename.replace('\\', '_').replace('/', '_')
            out_path = os.path.join(args.output, fname)
            with open(out_path, 'wb') as f:
                f.write(data)
            print(f'  [OK] {fname}  ({len(data):,} B)')
            ok += 1
        except Exception as e:
            print(f'  [FAIL] {a.filename}: {e}')
            err += 1
    print(f'\n  Extracted: {ok}  Errors: {err}')

def cmd_loc_export(args):
    loc_export(args.input, args.output)

def cmd_loc_import(args):
    loc_import(args.input, args.csv, args.output)

def cmd_patch(args):
    """Inject assets into existing archive for SM2.

    Reads the TOC, finds assets by hash, appends new data to the target
    archive, and updates SizeEntries with new offsets/sizes.
    """
    toc = _auto_toc(args)
    toc.load()
    archive_dir = args.archive_dir
    out_toc = getattr(args, 'output_toc', None) or 'toc.new'
    backup = not getattr(args, 'no_backup', False)

    if backup:
        bak = toc.toc_path + '.BAK'
        if not os.path.exists(bak):
            import shutil
            shutil.copy2(toc.toc_path, bak)
            print(f'  Backup: {bak}')

    # Parse --files
    pairs = []
    for entry in args.files:
        if '=' in entry:
            asset_ref, file_path = entry.split('=', 1)
        else:
            file_path = entry
            asset_ref = os.path.basename(entry)

        if not os.path.exists(file_path):
            print(f'  ERROR: file not found: {file_path}'); return

        # Resolve by hex ID
        hid = int(asset_ref, 16) if asset_ref.startswith(('0x', '0X')) else None
        if hid:
            idx = getattr(args, 'asset_index', 0)
            matches = [(i, a) for i, a in enumerate(toc.assets) if a.asset_id == hid]
            if idx < len(matches):
                asset_idx, asset = matches[idx]
                pairs.append((asset_idx, asset, file_path))
            elif matches:
                asset_idx, asset = matches[0]
                pairs.append((asset_idx, asset, file_path))
            else:
                print(f'  ERROR: asset not found: {asset_ref}'); return
        else:
            print(f'  ERROR: use hex ID (0x...) for SM2'); return

    if not pairs:
        print('No files to patch.'); return

    # Target archive (default: userinterface for font, localization for loc)
    # Use existing archive index from the first matching asset
    _, first_asset, _ = pairs[0]
    target_idx = first_asset.archive_index
    target_name = toc.archive_files[target_idx].filename if target_idx < len(toc.archive_files) else f'archive_{target_idx}'

    print(f'\n=== Patch: {len(pairs)} asset(s) -> [{target_idx}] {target_name} ===')

    file_offsets = {}
    for asset_idx, asset, file_path in pairs:
        if file_path in file_offsets:
            new_off, data_len = file_offsets[file_path]
            toc.patch_size_entry(asset_idx, data_len, target_idx, new_off)
            print(f'  [OK] {asset.filename} <- {os.path.basename(file_path)} ({data_len:,} B) [shared]')
        else:
            # Append to archive
            base_name = os.path.basename(target_name)
            arch_path = os.path.join(archive_dir, 'd', base_name)
            if not os.path.exists(arch_path):
                arch_path = os.path.join(archive_dir, base_name)
            if not os.path.exists(arch_path):
                print(f'  ERROR: archive not found: {arch_path}'); return

            data = open(file_path, 'rb').read()
            with open(arch_path, 'ab') as out:
                new_off = out.tell()
                out.write(data)

            file_offsets[file_path] = (new_off, len(data))
            toc.patch_size_entry(asset_idx, len(data), target_idx, new_off)
            print(f'  [OK] {asset.filename} <- {os.path.basename(file_path)} ({len(data):,} B)')

    toc.save(out_toc)
    print(f'  Done. Replace your toc with {out_toc}')


def main():
    import argparse
    p = argparse.ArgumentParser(prog='sm2', description='Spider-Man 2 PS5/PC Asset Tool')
    p.add_argument('--toc',    default='toc')
    p.add_argument('--hashdb', default='hashes.txt')
    sub = p.add_subparsers(dest='cmd')

    sub.add_parser('info', help='TOC summary')

    s = sub.add_parser('list', help='List assets')
    s.add_argument('--archive'); s.add_argument('--search')
    s.add_argument('--limit', type=int, default=50)

    s = sub.add_parser('extract', help='Extract assets')
    s.add_argument('--archive-dir', required=True)
    s.add_argument('--output', default='extracted')
    s.add_argument('--archive'); s.add_argument('--id'); s.add_argument('--search')

    s = sub.add_parser('loc-export', help='Export localization -> CSV')
    s.add_argument('input'); s.add_argument('output')

    s = sub.add_parser('loc-import', help='Import translated CSV -> localization')
    s.add_argument('input'); s.add_argument('csv'); s.add_argument('output')

    s = sub.add_parser('patch', help='Inject assets into existing archive')
    s.add_argument('--archive-dir', required=True, help='Game archive directory')
    s.add_argument('--files', nargs='+', required=True,
                   help='asset=file pairs (e.g. "0x8143F7F3648B4470=font.ttf")')
    s.add_argument('--output-toc', default='toc.new', help='Output TOC path')
    s.add_argument('--no-backup', action='store_true', help='Skip TOC backup')
    s.add_argument('--asset-index', type=int, default=0,
                   help='When multiple assets match, use the Nth one')

    args = p.parse_args()
    cmds = {
        'info': cmd_info, 'list': cmd_list, 'extract': cmd_extract,
        'loc-export': cmd_loc_export, 'loc-import': cmd_loc_import,
        'patch': cmd_patch,
    }
    if args.cmd not in cmds:
        p.print_help(); return
    cmds[args.cmd](args)


if __name__ == '__main__':
    main()
