#!/usr/bin/env python3
"""
SMPS4Tool - Spider-Man PS4 Asset Tool
Python port of SMPCTool adapted for PS4 file format.

Setup:      pip install lz4  (required for loc-export/loc-import)
First run:  python3 smps4tool.py build-hashdb --dag dag
Then:       python3 smps4tool.py info
            python3 smps4tool.py list --search spider-man
            python3 smps4tool.py extract --archive-dir /game --archive g00s000
            python3 smps4tool.py loc-export localization.en-US output.csv
"""

import struct, zlib, os, sys, csv, re
from dataclasses import dataclass
from typing import Optional

# ─── Native Hash Function ─────────────────────────────────────────────────────
# Reverse-engineered from SMPS4HashTool.exe (native x64 Windows binary).
# CRC-64 variant with custom lookup table extracted from binary offset 0x2840.

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
    """Insomniac Games asset hash. Case-insensitive, path-separator normalised."""
    SEP = 0x2f
    h   = 0xc96c5795d7870f42
    i   = 0
    raw = path.encode('ascii', errors='replace')
    while i < len(raw):
        c = raw[i]
        if c == 0x5c or c == SEP:
            while i < len(raw) and (raw[i] == 0x5c or raw[i] == SEP):
                i += 1
            c = SEP
        else:
            i += 1
            if 0x41 <= c <= 0x5A:
                c += 0x20
        h = _SM_TABLE[(h & 0xFF) ^ c] ^ (h >> 8)
    return (h >> 2) | 0x8000000000000000


# ─── Constants ────────────────────────────────────────────────────────────────
TOC_MAGIC  = 0xAF12AF77
DAG_MAGIC  = 0x891F77AF
DAT1_MAGIC = 0x44415431
ARCH_STRIDE = 24   # PS4: 24 bytes (PC: 72 bytes)

# Language detection for localization files.
# Uses 'TEST_ALL_LANG' key as primary discriminator, falls back to
# 'ABANDON_CONFIRM_HEADER' translation for identification.
_LANG_DETECT_KEYS = ('TEST_ALL_LANG', 'ABANDON_CONFIRM_HEADER')

# TEST_ALL_LANG value → language code
_TEST_LANG_MAP = {
    'Test all languages': 'en-US',
    'english(uk)':        'en-GB',
    'japanese':           'ja',
    'french(fr)':         'fr',
    'french(ca)':         'fr-CA',
    'spanish(sp)':        'es',
    'spanish(mex)':       'es-LA',
    'german':             'de',
    'italian':            'it',
    'dutch':              'nl',
    'port(port)':         'pt',
    'port(br)':           'pt-BR',
    'russian':            'ru',
    'polish':             'pl',
    'danish':             'da',
    'norwegian':          'no',
    'swedish':            'sv',
    'finnish':            'fi',
    'czech':              'cs',
    'greek':              'el',
    'turkish':            'tr',
    'hungarian':          'hu',
    'romanian':           'ro',
    'chinese traditional':'zh-Hant',
    'chinese simplified': 'zh-Hans',
    'arabic':             'ar',
    'thai':               'th',
    'vietnamese':         'vi',
    'indonesian':         'id',
    'hindi':              'hi',
}

# Fallback: ABANDON_CONFIRM_HEADER translation → language code
_HEADER_LANG_MAP = {
    'ARE YOU SURE?':        'en',
    '¿SEGURO?':             'es',
    'BIST DU SICHER?':      'de',
    'CONFIRMER ?':          'fr',
    'SEI SICURO?':          'it', 'CONFERMI?': 'it',
    'WEET JE HET ZEKER?':   'nl',
    'TEM CERTEZA?':         'pt', 'TENS A CERTEZA?': 'pt',
    'ВЫ УВЕРЕНЫ?':          'ru',
    'NA PEWNO?':            'pl',
    'ER DU SIKKER?':        'da',
    'ÄR DU SÄKER?':         'sv',
    'IHANKO VARMASTI?':     'fi',
    'JSTE SI JISTÍ?':       'cs',
    'ΤΟ ΘΕΛΕΙΣ ΣΙΓΟΥΡΑ;':   'el', 'ΕΊΣΤΕ ΣΊΓΟΥΡΟΙ;': 'el',
    'BIZTOS VAGY BENNE?':   'hu',
    'よろしいですか？':         'ja',
    '확실합니까?':              'ko', '정말 괜찮습니까?': 'ko',
    '你確定嗎？':              'zh-Hant',
    '你确定吗？':              'zh-Hans',
}

# Korean TEST_ALL_LANG is in Korean script, detect separately
_TEST_LANG_KO = '모든 언어 시험'

# All known language codes used in suffixes
_ALL_LANG_CODES = [
    'ja','en','en-US','en-GB','fr','fr-CA','es','es-LA','de','it','nl','pt','pt-BR',
    'ru','ko','zh-Hant','zh-Hans','fi','sv','da','no','pl','cs','el','tr','ar',
    'ro','hu','vi','id','hi','th','und',
]

def _detect_loc_language(data: bytes) -> str:
    """Detect language from raw localization asset bytes (LZ4+DAT1).

    Uses TEST_ALL_LANG key (e.g. 'japanese', 'french(fr)') as primary signal.
    Falls back to ABANDON_CONFIRM_HEADER translation if TEST_ALL_LANG missing.
    """
    try:
        import lz4.block
        rawsize = struct.unpack('<I', data[4:8])[0]
        dec = lz4.block.decompress(data[0x24:], uncompressed_size=rawsize)

        nsec = struct.unpack('<I', dec[12:16])[0]
        sections = {}
        pos = 16
        for _ in range(nsec):
            h, off, sz = struct.unpack('<III', dec[pos:pos+12])
            sections[h] = (off, sz)
            pos += 12

        kd_off, _ = sections.get(0x4D73CEBD, (0,0))
        ko_off, ko_sz = sections.get(0xA4EA55B2, (0,0))
        td_off, _ = sections.get(0x70A382B8, (0,0))
        to_off, _ = sections.get(0xF80DEEB4, (0,0))
        if ko_sz == 0: return 'und'

        count = ko_sz // 4
        found = {}
        for i in range(count):
            ko = struct.unpack('<i', dec[ko_off+i*4:ko_off+i*4+4])[0]
            to = struct.unpack('<i', dec[to_off+i*4:to_off+i*4+4])[0]
            kpos = kd_off + ko
            kend = dec.index(b'\x00', kpos)
            key = dec[kpos:kend].decode('utf-8','replace')
            if key in _LANG_DETECT_KEYS and to != 0:
                tpos = td_off + to
                tend = dec.index(b'\x00', tpos)
                found[key] = dec[tpos:tend].decode('utf-8','replace')
            if len(found) >= 2:
                break

        # Primary: TEST_ALL_LANG
        test_val = found.get('TEST_ALL_LANG', '').strip().lower()
        if test_val:
            if test_val == _TEST_LANG_KO.lower() or '언어' in test_val:
                return 'ko'
            for phrase, lang in _TEST_LANG_MAP.items():
                if phrase.lower() == test_val:
                    return lang

        # Fallback: ABANDON_CONFIRM_HEADER
        header_val = found.get('ABANDON_CONFIRM_HEADER', '').strip()
        if header_val:
            lang = _HEADER_LANG_MAP.get(header_val)
            if lang:
                return lang

        # Check if file has any translations at all
        non_empty = sum(1 for i in range(min(count, 100))
                        if struct.unpack('<i', dec[to_off+i*4:to_off+i*4+4])[0] != 0)
        if non_empty == 0:
            return 'und'

    except Exception:
        pass
    return 'und'

# Cache: asset_id+offset → detected lang
_lang_cache: dict[tuple, str] = {}

def _lang_suffix_for(asset, all_assets, reader=None):
    """Return a language suffix like '.en' for localization duplicates.

    Detects actual language from file content (LZ4+DAT1) instead of
    relying on archive position. Requires an ArchiveReader to read data.

    Returns '' for non-duplicate filenames.
    Falls back to '.lang{N}' if reader is unavailable or detection fails.
    """
    if asset.filename.startswith('0x'):
        return ''
    dupes = [a for a in all_assets
             if a.filename == asset.filename and a.archive_name == asset.archive_name]
    if len(dupes) <= 1:
        return ''
    idx = dupes.index(asset)

    if reader is not None:
        cache_key = (asset.asset_id, asset.archive_offset)
        if cache_key not in _lang_cache:
            try:
                data = reader.read_asset(asset)
                _lang_cache[cache_key] = _detect_loc_language(data)
            except Exception:
                _lang_cache[cache_key] = f'lang{idx}'
        lang = _lang_cache[cache_key]
        # Handle duplicate detected codes (e.g. multiple 'en' for en-US/en-GB)
        # by appending index if collision
        used = []
        for j, d in enumerate(dupes):
            if j == idx:
                break
            dk = (d.asset_id, d.archive_offset)
            if dk in _lang_cache and _lang_cache[dk] == lang:
                used.append(j)
        if used:
            lang = f'{lang}_{len(used)+1}'
        return f'.{lang}'
    else:
        return f'.lang{idx}'

def _strip_lang_suffix(filename):
    """Remove a language suffix added by extract, e.g.
    'localization_all.localization.en' → 'localization_all.localization'
    """
    for lang in _ALL_LANG_CODES:
        if filename.endswith(f'.{lang}'):
            return filename[:-(len(lang)+1)]
    # Handle collision suffixes like .en_2 and fallback .lang##
    m = re.match(r'^(.+)\.(?:[a-z]{2}(?:-[A-Za-z]+)?_\d+|lang\d+)$', filename)
    if m:
        return m.group(1)
    return filename


# ─── Data classes ─────────────────────────────────────────────────────────────
@dataclass
class Section:
    hash: int; offset: int; size: int

@dataclass
class ArchiveFile:
    index: int; filename: str; unk1: int; unk2: int; unk3: int; unk4: int

@dataclass
class AssetEntry:
    asset_id: int; filename: str
    archive_index: int; archive_name: str
    archive_offset: int; file_size: int
    ai_toc: int = 0; ao_toc: int = 0; sz_toc: int = 0


# ─── TOC ──────────────────────────────────────────────────────────────────────
class TOC:
    def __init__(self, toc_path: str, hashdb_path: Optional[str] = None):
        self.toc_path = toc_path
        self.raw_data = b''; self.dec_data = b''; self.dec_size = 0
        self.sections: list[Section] = []
        self.archive_files: list[ArchiveFile] = []
        self.asset_ids: list[int] = []
        self.size_entries: list[tuple] = []
        self.key_assets: list[int] = []
        self.offset_entries: list[tuple] = []
        self.spans_entries: list[tuple] = []
        self.assets: list[AssetEntry] = []
        self.hash_db: dict[int,str] = {}
        if hashdb_path and os.path.exists(hashdb_path):
            self._load_hashdb(hashdb_path)

    def _load_hashdb(self, path: str) -> None:
        with open(path,'r',errors='replace') as f:
            for line in f:
                line = line.strip()
                if ',' not in line: continue
                idx = line.rfind(',')
                try: self.hash_db[int(line[idx+1:]) & 0xFFFFFFFFFFFFFFFF] = line[:idx]
                except ValueError: pass

    def load_hashdb_from_dag(self, dag_path: str, save_path: Optional[str] = None) -> None:
        print(f'Building hash DB from DAG...')
        db = build_hash_db_from_dag(dag_path, output_path=save_path, verbose=True)
        self.hash_db.update(db)
        # Refresh asset names
        n = sum(1 for a in self.assets
                if a.filename.startswith('0x') and a.asset_id in db
                for _ in [setattr(a,'filename',db[a.asset_id])])
        print(f'Hash DB: {len(self.hash_db):,} entries')

    def name_for(self, aid: int) -> str:
        return self.hash_db.get(aid, f'0x{aid:016X}')

    def load(self) -> None:
        print(f'Loading TOC: {self.toc_path}')
        with open(self.toc_path,'rb') as f: self.raw_data = f.read()
        if struct.unpack('>I', self.raw_data[:4])[0] != TOC_MAGIC:
            raise ValueError('Bad TOC magic')
        self.dec_size = struct.unpack('<I', self.raw_data[4:8])[0]
        print(f'Decompressing ({self.dec_size:,} bytes)...')
        self.dec_data = zlib.decompressobj().decompress(self.raw_data[8:])
        self._parse()
        named = sum(1 for a in self.assets if not a.filename.startswith('0x'))
        print(f'Ready: {len(self.archive_files)} archives, '
              f'{len(self.assets):,} assets, '
              f'{named:,} named ({100*named//len(self.assets)}%)')

    def _parse(self) -> None:
        d = self.dec_data
        if struct.unpack('<I',d[0:4])[0] != DAT1_MAGIC: raise ValueError('Not DAT1')
        n = struct.unpack('<I',d[12:16])[0]; pos = 16
        for _ in range(n):
            h,o,s = struct.unpack('<III',d[pos:pos+12])
            self.sections.append(Section(h,o,s)); pos += 12
        self._parse_archives(self.sections[0])
        self._parse_ids(self.sections[1])
        self._parse_sizes(self.sections[2])
        self._parse_keys(self.sections[3])
        self._parse_offsets(self.sections[4])
        self._parse_spans(self.sections[5])
        self._build()

    def _parse_archives(self, sec):
        d,o = self.dec_data, sec.offset
        for i in range(sec.size // ARCH_STRIDE):
            e = d[o+i*ARCH_STRIDE:o+(i+1)*ARCH_STRIDE]
            u1,u2 = struct.unpack('<II',e[0:8])
            # Name is null-terminated starting at byte 8, can extend past byte 16
            nm = e[8:].split(b'\x00')[0].decode('ascii','replace')
            # Remaining unk fields only if name fits in 8 bytes
            tail = e[8+len(nm)+1:] if 8+len(nm)+1 < ARCH_STRIDE else b''
            if len(tail) >= 8:
                u3,u4 = struct.unpack('<II',tail[:8])
            elif len(tail) >= 4:
                u3 = struct.unpack('<I',tail[:4])[0]; u4 = 0
            else:
                u3 = u4 = 0
            self.archive_files.append(ArchiveFile(i,nm,u1,u2,u3,u4))

    def _parse_ids(self, sec):
        d,o = self.dec_data, sec.offset
        for i in range(sec.size//8):
            self.asset_ids.append(struct.unpack('<Q',d[o+i*8:o+i*8+8])[0])

    def _parse_sizes(self, sec):
        d,o = self.dec_data, sec.offset
        for i in range(sec.size//12):
            b = o+i*12; self.size_entries.append(struct.unpack('<III',d[b:b+12]))

    def _parse_keys(self, sec):
        d,o = self.dec_data, sec.offset
        for i in range(sec.size//8):
            self.key_assets.append(struct.unpack('<Q',d[o+i*8:o+i*8+8])[0])

    def _parse_offsets(self, sec):
        d,o = self.dec_data, sec.offset
        for i in range(sec.size//8):
            b = o+i*8; self.offset_entries.append(struct.unpack('<II',d[b:b+8]))

    def _parse_spans(self, sec):
        d,o = self.dec_data, sec.offset
        for i in range(sec.size//8):
            b = o+i*8; self.spans_entries.append(struct.unpack('<II',d[b:b+8]))

    def _build(self) -> None:
        oe_base = self.sections[4].offset; se_base = self.sections[2].offset
        for i,(aid,se) in enumerate(zip(self.asset_ids, self.size_entries)):
            _,fsize,fctr = se
            arch_idx,arch_off = self.offset_entries[fctr]
            nm = self.archive_files[arch_idx].filename if arch_idx < len(self.archive_files) else f'archive_{arch_idx}'
            oe_off = oe_base + fctr*8
            self.assets.append(AssetEntry(
                asset_id=aid, filename=self.name_for(aid),
                archive_index=arch_idx, archive_name=nm,
                archive_offset=arch_off, file_size=fsize,
                ai_toc=oe_off, ao_toc=oe_off+4, sz_toc=se_base+i*12+4))

    def refresh_names(self) -> int:
        n = 0
        for a in self.assets:
            if a.filename.startswith('0x'):
                nm = self.hash_db.get(a.asset_id)
                if nm: a.filename = nm; n += 1
        return n

    def get_by_id(self, aid: int) -> Optional[AssetEntry]:
        for a in self.assets:
            if a.asset_id == aid: return a
        return None

    def get_by_name(self, name: str) -> Optional[AssetEntry]:
        nl = name.lower()
        for a in self.assets:
            if a.filename.lower() == nl: return a
        return None

    def search(self, q: str) -> list[AssetEntry]:
        ql = q.lower(); return [a for a in self.assets if ql in a.filename.lower()]

    def by_archive(self, name: str) -> list[AssetEntry]:
        return [a for a in self.assets if a.archive_name == name]

    def export_csv(self, path: str, reader=None) -> None:
        with open(path,'w',newline='',encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Asset Path','Asset ID','Archive','Offset','Size'])
            for a in self.assets:
                lang = _lang_suffix_for(a, self.assets, reader=reader)
                w.writerow([a.filename + lang, f'0x{a.asset_id:016X}',
                             a.archive_name,f'0x{a.archive_offset:08X}',a.file_size])
        print(f'CSV: {path} ({len(self.assets):,} rows)')

    def patch_redirect(self, asset: AssetEntry, new_idx: int, new_off: int, new_sz: int) -> None:
        buf = bytearray(self.dec_data)
        struct.pack_into('<I',buf,asset.ai_toc,new_idx)
        struct.pack_into('<I',buf,asset.ao_toc,new_off)
        struct.pack_into('<I',buf,asset.sz_toc,new_sz)
        self.dec_data = bytes(buf)

    def save(self, path: Optional[str] = None) -> None:
        out = path or self.toc_path
        with open(out,'wb') as f:
            f.write(struct.pack('>I',TOC_MAGIC))
            f.write(struct.pack('<I',len(self.dec_data)))
            f.write(zlib.compress(self.dec_data, level=9))
        print(f'TOC saved: {out} ({os.path.getsize(out):,} bytes)')


# ─── DAG hash builder ─────────────────────────────────────────────────────────
def build_hash_db_from_dag(dag_path: str, output_path: Optional[str] = None,
                            verbose: bool = True) -> dict[int,str]:
    with open(dag_path,'rb') as f: raw = f.read()
    if struct.unpack('<I',raw[:4])[0] != DAG_MAGIC: raise ValueError('Bad DAG magic')
    if verbose: print('Decompressing DAG...')
    dec = zlib.decompressobj().decompress(raw[12:])
    names: list[str] = []; pos = 102
    while pos < len(dec):
        start = pos
        while pos < len(dec) and dec[pos] != 0: pos += 1
        s = dec[start:pos].decode('ascii','replace')
        if s: names.append(s)
        pos += 1
        if pos < len(dec) and dec[pos] == 0: break
    if verbose: print(f'Hashing {len(names):,} names...')
    db = {sm_hash(n): n for n in names}
    if output_path:
        with open(output_path,'w',encoding='utf-8') as f:
            for h,n in db.items(): f.write(f'{n},{h}\n')
        if verbose:
            print(f'Saved: {output_path} ({len(db):,} entries, '
                  f'{os.path.getsize(output_path)//1024//1024} MB)')
    return db


# ─── Archive Reader ───────────────────────────────────────────────────────────
class ArchiveReader:
    def __init__(self, archive_dir: str): self.archive_dir = archive_dir
    def read_asset(self, asset: AssetEntry) -> bytes:
        path = os.path.join(self.archive_dir, asset.archive_name)
        if not os.path.exists(path): raise FileNotFoundError(f'Not found: {path}')
        with open(path,'rb') as f:
            f.seek(asset.archive_offset); data = f.read(asset.file_size)
        if len(data) != asset.file_size: raise IOError(f'Short read: {len(data)}/{asset.file_size}')
        return data


# ─── Mod Manager ─────────────────────────────────────────────────────────────


# ─── Localization ─────────────────────────────────────────────────────────────
# Section IDs from team-waldo/InsomniacArchive LocalizationFile.cs
_LOC_KEY_DATA   = 0x4D73CEBD
_LOC_KEY_OFF    = 0xA4EA55B2
_LOC_TR_DATA    = 0x70A382B8
_LOC_TR_OFF     = 0xF80DEEB4

def _loc_decompress(path: str) -> bytes:
    """Decompress an Insomniac asset file (LZ4 with 0x24-byte header)."""
    try:
        import lz4.block
    except ImportError:
        print('ERROR: lz4 not installed. Run: pip install lz4'); sys.exit(1)
    with open(path,'rb') as f: raw = f.read()
    magic = struct.unpack('<I', raw[0:4])[0]
    rawsize = struct.unpack('<I', raw[4:8])[0]
    compressed = raw[0x24:]
    if len(compressed) == rawsize:
        return compressed  # not compressed
    return lz4.block.decompress(compressed, uncompressed_size=rawsize)

def _loc_compress(dec: bytes, magic: int) -> bytes:
    """Compress data back into Insomniac asset format."""
    try:
        import lz4.block
    except ImportError:
        print('ERROR: lz4 not installed. Run: pip install lz4'); sys.exit(1)
    compressed = lz4.block.compress(dec, store_size=False)
    header = struct.pack('<I', magic) + struct.pack('<I', len(dec)) + b'\x00' * 28
    return header + compressed

def _loc_parse_sections(dec: bytes) -> dict:
    """Parse DAT1 sections, return {hash: (offset, size)}."""
    nsec = struct.unpack('<I', dec[12:16])[0]
    sections = {}
    pos = 16
    for _ in range(nsec):
        h, off, sz = struct.unpack('<III', dec[pos:pos+12])
        sections[h] = (off, sz)
        pos += 12
    return sections

def _loc_get_string(dec: bytes, base: int, off: int) -> str:
    pos = base + off
    end = dec.index(b'\x00', pos)
    return dec[pos:end].decode('utf-8', errors='replace')

def loc_export(loc_path: str, csv_path: str) -> int:
    """Export localization asset → CSV (key, source, translation)."""
    dec = _loc_decompress(loc_path)
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
            key = _loc_get_string(dec, kd_off, ko)
            val = _loc_get_string(dec, td_off, to) if to != 0 or key == 'INVALID' else ''
            w.writerow([key, val, ''])

    print(f'Exported {count:,} strings to {csv_path}')
    return count

def loc_import(loc_path: str, csv_path: str, out_path: str) -> int:
    """Import translated CSV back into localization asset."""
    # Read translations from CSV
    translations = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if len(row) >= 3 and row[2].strip():
                translations[row[0]] = row[2]
    print(f'Loaded {len(translations):,} translations from {csv_path}')

    # Decompress original
    with open(loc_path, 'rb') as f: raw = f.read()
    magic = struct.unpack('<I', raw[0:4])[0]
    dec = _loc_decompress(loc_path)
    sec = _loc_parse_sections(dec)

    kd_off, _ = sec[_LOC_KEY_DATA]
    ko_off, ko_sz = sec[_LOC_KEY_OFF]
    td_off, td_sz = sec[_LOC_TR_DATA]
    to_off, _ = sec[_LOC_TR_OFF]
    count = ko_sz // 4

    # Build new translation data
    new_tr_data = bytearray()
    new_tr_offsets = []
    imported = 0

    for i in range(count):
        ko = struct.unpack('<i', dec[ko_off+i*4:ko_off+i*4+4])[0]
        to = struct.unpack('<i', dec[to_off+i*4:to_off+i*4+4])[0]
        key = _loc_get_string(dec, kd_off, ko)

        if key in translations:
            value = translations[key]
            imported += 1
        else:
            value = _loc_get_string(dec, td_off, to) if to != 0 or key == 'INVALID' else ''

        if key != 'INVALID' and value == '':
            new_tr_offsets.append(0)
        else:
            new_tr_offsets.append(len(new_tr_data))
            new_tr_data.extend(value.encode('utf-8') + b'\x00')

    # Patch decompressed data: replace translation data + offsets
    buf = bytearray(dec)

    # Replace translation offsets section
    for i in range(count):
        struct.pack_into('<i', buf, to_off + i*4, new_tr_offsets[i])

    # Replace translation data section — need to update section size in header
    old_td_end = td_off + td_sz
    new_td = bytes(new_tr_data)

    # Rebuild: everything before tr_data + new tr_data + everything after old tr_data
    # Since tr_data is the LAST section (highest offset), we can just truncate and append
    # But sections aren't guaranteed to be in order, so we do it carefully
    # Find which section is at the end of the file
    all_secs = sorted(sec.items(), key=lambda x: x[1][0])
    
    # TranslationData (0x70A382B8) is last section by offset — just replace in place
    if all_secs[-1][0] == _LOC_TR_DATA:
        new_dec = bytes(buf[:td_off]) + new_td
        # Update section size in DAT1 header
        nsec = struct.unpack('<I', new_dec[12:16])[0]
        pos = 16
        new_dec_buf = bytearray(new_dec)
        for _ in range(nsec):
            h = struct.unpack('<I', new_dec_buf[pos:pos+4])[0]
            if h == _LOC_TR_DATA:
                struct.pack_into('<I', new_dec_buf, pos+8, len(new_td))
            pos += 12
        new_dec = bytes(new_dec_buf)
    else:
        # Fallback: just patch in place (may leave garbage but size stays same)
        new_dec_buf = bytearray(buf)
        new_dec_buf[td_off:td_off+len(new_td)] = new_td
        new_dec = bytes(new_dec_buf)

    # Compress and save
    out_data = _loc_compress(new_dec, magic)
    with open(out_path, 'wb') as f:
        f.write(out_data)

    print(f'Imported {imported:,} translations, saved to {out_path}')
    print(f'  Original: {len(raw):,} bytes → New: {len(out_data):,} bytes')
    return imported


# ─── CLI ──────────────────────────────────────────────────────────────────────

def repack_archive(toc: TOC, archive_name: str, archive_dir: str,
                   output_archive: str, output_toc: str,
                   skip_hex: bool = False, verbose: bool = True) -> dict:
    """Repack an archive: read all assets → write new archive → update TOC.

    Returns dict with stats. The new archive is a raw concatenation of asset
    data (same format as the original PS4 archives). The TOC is patched so
    every affected asset points to the new archive with correct offsets/sizes.
    """
    reader = ArchiveReader(archive_dir)
    assets = toc.by_archive(archive_name)
    if not assets:
        raise ValueError(f'No assets found in archive: {archive_name}')

    # Optional: filter out hex-only assets
    if skip_hex:
        original_count = len(assets)
        assets = [a for a in assets if not a.filename.startswith('0x')]
        skipped = original_count - len(assets)
        if verbose:
            print(f'  Skipping {skipped:,} hex-ID assets, repacking {len(assets):,} named assets')

    # Determine archive index for the repacked archive.
    # Find the original archive index so we can reuse it.
    orig_idx = assets[0].archive_index if assets else -1

    # Read all asset data and write new archive
    if verbose:
        print(f'  Reading {len(assets):,} assets from {archive_name}...')

    os.makedirs(os.path.dirname(output_archive) or '.', exist_ok=True)
    ok = err = 0
    with open(output_archive, 'wb') as out:
        for a in assets:
            try:
                data = reader.read_asset(a)
                new_off = out.tell()
                out.write(data)
                # Patch TOC: update offset and size for this asset
                toc.patch_redirect(a, orig_idx, new_off, len(data))
                ok += 1
            except Exception as e:
                if verbose:
                    print(f'  ✗ {a.filename}: {e}')
                err += 1

    archive_size = os.path.getsize(output_archive)
    if verbose:
        print(f'  Archive: {output_archive} ({archive_size:,} bytes)')
        print(f'  Assets:  {ok:,} repacked, {err:,} errors')

    # Save updated TOC
    toc.save(output_toc)

    stats = {
        'archive': output_archive, 'archive_size': archive_size,
        'toc': output_toc, 'assets_total': len(assets),
        'assets_ok': ok, 'assets_err': err,
        'skipped_hex': skipped if skip_hex else 0,
    }
    return stats


def cmd_repack(args):
    toc = _auto_toc(args)
    archive_name = args.archive
    out_archive = getattr(args, 'output_archive', None) or archive_name
    out_toc = getattr(args, 'output_toc', None) or 'toc.new'
    skip_hex = getattr(args, 'skip_hex', False)

    print(f'\n=== Repack: {archive_name} ===')
    stats = repack_archive(
        toc, archive_name, args.archive_dir,
        out_archive, out_toc,
        skip_hex=skip_hex, verbose=True
    )
    print(f'\n  Done. New TOC: {stats["toc"]}')
    if skip_hex and stats['skipped_hex']:
        print(f'  Note: {stats["skipped_hex"]:,} hex-ID assets were excluded.')
        print(f'  The new archive only contains named assets.')


def cmd_repack_dir(args):
    """Repack from an extracted directory.

    Reads files from a directory (as produced by 'extract'), rebuilds the archive,
    and generates a new TOC.  For localization files that were extracted with a
    language suffix (e.g. localization_all.localization.en-US), the suffix is
    stripped and the file is matched back to the correct asset entry by position.
    Files not found in the directory are read from the original archive as-is.
    """
    toc = _auto_toc(args)
    archive_name = args.archive
    extract_dir = args.dir
    out_archive = getattr(args, 'output_archive', None) or archive_name
    out_toc = getattr(args, 'output_toc', None) or 'toc.new'
    is_flat = getattr(args, 'flat', False)

    reader = ArchiveReader(args.archive_dir)
    assets = toc.by_archive(archive_name)
    if not assets:
        print(f'No assets in archive: {archive_name}'); return

    orig_idx = assets[0].archive_index

    # Build a map: for each asset, find the corresponding file in extract_dir.
    # Handle language suffixes: extract produces e.g.
    #   localization_all.localization.en-US  (flat)
    #   localization/localization_all.localization.en-US  (tree)
    # We need to match these back to the correct asset entry.

    # Scan extracted files
    extracted_files = {}
    for root, _dirs, files in os.walk(extract_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            extracted_files[fname] = fpath
            # Also store the relative path version
            rel = os.path.relpath(fpath, extract_dir)
            extracted_files[rel] = fpath

    print(f'\n=== Repack from directory: {extract_dir} ===')
    print(f'  Archive: {archive_name} ({len(assets):,} assets)')
    print(f'  Found {len(extracted_files)//2:,} files in directory')

    os.makedirs(os.path.dirname(out_archive) or '.', exist_ok=True)
    ok = replaced = from_orig = err = 0

    with open(out_archive, 'wb') as out:
        for a in assets:
            try:
                lang = _lang_suffix_for(a, assets, reader=reader)
                data = None

                # Try to find a replacement file in the extract directory
                candidates = []
                if is_flat or '\\' not in a.filename:
                    safe = a.filename.replace('\\','_').replace('/','_')
                    candidates.append(safe + lang)       # with lang suffix
                    candidates.append(safe)              # without
                else:
                    rel = a.filename.replace('\\', os.sep)
                    candidates.append(rel + lang)
                    candidates.append(rel)
                    # Also flat versions
                    safe = a.filename.replace('\\','_').replace('/','_')
                    candidates.append(safe + lang)
                    candidates.append(safe)

                for c in candidates:
                    if c in extracted_files:
                        data = open(extracted_files[c], 'rb').read()
                        replaced += 1
                        break

                # Fallback: read from original archive
                if data is None:
                    data = reader.read_asset(a)
                    from_orig += 1

                new_off = out.tell()
                out.write(data)
                toc.patch_redirect(a, orig_idx, new_off, len(data))
                ok += 1
            except Exception as e:
                print(f'  ✗ {a.filename}: {e}')
                err += 1

    archive_size = os.path.getsize(out_archive)
    toc.save(out_toc)

    print(f'  Repacked: {ok:,} assets ({replaced:,} from dir, {from_orig:,} from original)')
    print(f'  Errors: {err}')
    print(f'  Archive: {out_archive} ({archive_size:,} bytes)')
    print(f'  TOC: {out_toc}')


def _auto_toc(args) -> TOC:
    hashdb = getattr(args,'hashdb',None)
    if not hashdb or not os.path.exists(hashdb):
        for c in ['PS4AssetHashes.txt',
                  os.path.join(os.path.dirname(__file__),'PS4AssetHashes.txt'),
                  'AssetHashes.txt']:
            if os.path.exists(c): hashdb = c; break
    toc = TOC(args.toc, hashdb)
    toc.load()
    return toc

def cmd_build_hashdb(args):
    out = getattr(args,'output','PS4AssetHashes.txt')
    build_hash_db_from_dag(args.dag, output_path=out, verbose=True)

def cmd_info(args):
    toc = _auto_toc(args)
    named = sum(1 for a in toc.assets if not a.filename.startswith('0x'))
    total = len(toc.assets)
    print(f'\n=== TOC Summary ===')
    print(f'  Archives    : {len(toc.archive_files)}')
    print(f'  Total assets: {total:,}')
    print(f'  Named assets: {named:,} ({100*named//total}%)')
    print(f'  Hash DB     : {len(toc.hash_db):,} entries')
    print(f'\n  {"#":<5} {"Archive":<18} {"Assets":>8}')
    print(f'  {"─"*5} {"─"*18} {"─"*8}')
    for arc in toc.archive_files:
        n = sum(1 for a in toc.assets if a.archive_index == arc.index)
        if n: print(f'  [{arc.index:3d}] {arc.filename:<18} {n:8,}')

def cmd_list(args):
    toc = _auto_toc(args)
    assets = toc.assets
    if getattr(args,'archive',None): assets = [a for a in assets if a.archive_name==args.archive]
    if getattr(args,'search',None):  assets = toc.search(args.search) if not getattr(args,'archive',None) else [a for a in assets if args.search.lower() in a.filename.lower()]
    if getattr(args,'named_only',False): assets = [a for a in assets if not a.filename.startswith('0x')]
    limit = getattr(args,'limit',50)
    print(f'\n  {"Asset Path":<80} {"Archive":<14} {"Offset":>12} {"Size":>10}')
    print(f'  {"─"*80} {"─"*14} {"─"*12} {"─"*10}')
    for a in assets[:limit]:
        print(f'  {a.filename:<80} {a.archive_name:<14} 0x{a.archive_offset:08X} {a.file_size:10,}')
    if len(assets)>limit: print(f'\n  ... {len(assets)-limit:,} more')
    print(f'\n  Total: {len(assets):,}')

def cmd_extract(args):
    toc = _auto_toc(args)
    reader = ArchiveReader(args.archive_dir)
    os.makedirs(args.output, exist_ok=True)
    if   getattr(args,'id',None):      assets = [a for a in [toc.get_by_id(int(args.id,16))] if a]
    elif getattr(args,'name',None):    a = toc.get_by_name(args.name); assets = [a] if a else toc.search(args.name)
    elif getattr(args,'archive',None): assets = toc.by_archive(args.archive)
    elif getattr(args,'search',None):  assets = toc.search(args.search)
    else: print('Need --name/--id/--archive/--search'); return
    if not assets: print('No assets found.'); return
    skip_hex = getattr(args,'skip_hex',False)
    ok = err = skipped = 0
    for a in assets:
        if skip_hex and a.filename.startswith('0x'):
            skipped += 1; continue
        try:
            data = reader.read_asset(a)
            lang = _lang_suffix_for(a, assets, reader=reader)
            if getattr(args,'flat',False) or '\\' not in a.filename:
                safe = a.filename.replace('\\','_').replace('/','_') + lang
                out_path = os.path.join(args.output, safe)
            else:
                rel = a.filename.replace('\\', os.sep) + lang
                out_path = os.path.join(args.output, rel)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path,'wb') as f: f.write(data)
            disp = a.filename + lang
            print(f'  ✓ {disp}  ({len(data):,} B)')
            ok += 1
        except Exception as e:
            print(f'  ✗ {a.filename}: {e}'); err += 1
    print(f'\n  Extracted: {ok}  Errors: {err}' +
          (f'  Skipped (hex): {skipped}' if skipped else ''))

def cmd_csv(args):
    toc = _auto_toc(args)
    reader = ArchiveReader(args.archive_dir) if getattr(args,'archive_dir',None) else None
    toc.export_csv(getattr(args,'output','assets.csv'), reader=reader)

def cmd_hash(args):
    h = sm_hash(args.path)
    print(f'0x{h:016X}  (decimal: {h})')

def cmd_dag(args):
    dag_path = getattr(args,'dag','dag')
    if getattr(args,'search',None):
        with open(dag_path,'rb') as f: raw = f.read()
        dec = zlib.decompressobj().decompress(raw[12:])
        pos = 102; names = []
        while pos < len(dec):
            start = pos
            while pos < len(dec) and dec[pos] != 0: pos += 1
            s = dec[start:pos].decode('ascii','replace')
            if s: names.append(s)
            pos += 1
            if pos < len(dec) and dec[pos] == 0: break
        q = args.search.lower(); matches = [n for n in names if q in n.lower()]
        print(f'{len(matches):,} results for "{args.search}":')
        for n in matches[:50]: print(f'  {n}')
        if len(matches)>50: print(f'  ... {len(matches)-50} more')
    else:
        out = getattr(args,'output','PS4AssetHashes.txt')
        build_hash_db_from_dag(dag_path, output_path=out, verbose=True)


def cmd_loc_export(args):
    loc_export(args.input, args.output)

def cmd_loc_import(args):
    loc_import(args.input, args.csv, args.output)

def cmd_patch(args):
    """Create a small mod archive with only modified files + patch TOC to point to it.

    Instead of repacking the entire archive, this:
    1. Creates a new small archive containing ONLY the replacement files
    2. Patches the TOC so those specific assets point to the new archive
    3. All other assets remain pointing to original archives (untouched)

    Usage:
      --files "asset_name_or_id=replacement_file" pairs
      The new archive is placed in archive-dir so the game can find it.
    """
    toc = _auto_toc(args)
    archive_dir = args.archive_dir
    mod_name = args.mod_name
    out_toc = getattr(args, 'output_toc', None) or 'toc.new'
    backup = not getattr(args, 'no_backup', False)

    # Backup original TOC
    if backup:
        bak = toc.toc_path + '.BAK'
        if not os.path.exists(bak):
            import shutil
            shutil.copy2(toc.toc_path, bak)
            print(f'  Backup: {bak}')

    # Parse --files pairs: "asset=file" or "0xHASH=file"
    pairs = []
    for entry in args.files:
        if '=' not in entry:
            print(f'  ERROR: invalid format "{entry}", expected "asset_name=file_path"'); return
        asset_ref, file_path = entry.split('=', 1)
        if not os.path.exists(file_path):
            print(f'  ERROR: file not found: {file_path}'); return

        # Find asset by name, hash, or ID
        asset = None
        if asset_ref.startswith(('0x','0X')):
            asset = toc.get_by_id(int(asset_ref, 16))
        if not asset:
            asset = toc.get_by_name(asset_ref)
        if not asset:
            results = toc.search(asset_ref)
            if len(results) == 1:
                asset = results[0]
            elif len(results) > 1:
                print(f'  ERROR: "{asset_ref}" matches {len(results)} assets, be more specific'); return
        if not asset:
            print(f'  ERROR: asset not found: {asset_ref}'); return
        pairs.append((asset, file_path))

    if not pairs:
        print('No files to patch.'); return

    # Use the next available archive index (beyond existing archives)
    new_idx = max(a.index for a in toc.archive_files) + 1

    # Write mod archive
    mod_path = os.path.join(archive_dir, mod_name)
    os.makedirs(os.path.dirname(mod_path) if os.path.dirname(mod_path) else '.', exist_ok=True)

    print(f'\n=== Patch: {len(pairs)} asset(s) → {mod_name} ===')

    with open(mod_path, 'wb') as out:
        for asset, file_path in pairs:
            data = open(file_path, 'rb').read()
            new_off = out.tell()
            out.write(data)
            toc.patch_redirect(asset, new_idx, new_off, len(data))
            print(f'  ✓ {asset.filename} ← {file_path} ({len(data):,} B)')

    mod_size = os.path.getsize(mod_path)
    print(f'  Archive: {mod_path} ({mod_size:,} bytes)')

    # Save patched TOC
    toc.save(out_toc)
    print(f'  Done. Replace your toc with {out_toc}')
    print(f'  Game will load patched assets from {mod_name}')

def main():
    import argparse
    p = argparse.ArgumentParser(prog='smps4tool', description='Spider-Man PS4 Asset Tool')
    p.add_argument('--toc',    default='toc')
    p.add_argument('--hashdb', default='PS4AssetHashes.txt')
    sub = p.add_subparsers(dest='cmd')

    s = sub.add_parser('build-hashdb', help='Build PS4AssetHashes.txt from dag  ← run this first!')
    s.add_argument('--dag',    default='dag')
    s.add_argument('--output', default='PS4AssetHashes.txt')

    sub.add_parser('info', help='TOC summary')

    s = sub.add_parser('list', help='List assets')
    s.add_argument('--archive'); s.add_argument('--search')
    s.add_argument('--named-only', action='store_true')
    s.add_argument('--limit', type=int, default=50)

    s = sub.add_parser('extract', help='Extract assets')
    s.add_argument('--archive-dir', required=True)
    s.add_argument('--output', default='extracted')
    s.add_argument('--archive'); s.add_argument('--name')
    s.add_argument('--id'); s.add_argument('--search')
    s.add_argument('--flat', action='store_true', help='No subdirs in output')
    s.add_argument('--skip-hex', action='store_true', help='Skip assets with hex ID (no name)')

    s = sub.add_parser('repack', help='Repack archive → new archive + new TOC')
    s.add_argument('--archive-dir', required=True)
    s.add_argument('--archive', required=True)
    s.add_argument('--output-archive', default=None, help='Output archive path (default: same name)')
    s.add_argument('--output-toc', default='toc.new', help='Output TOC path (default: toc.new)')
    s.add_argument('--skip-hex', action='store_true', help='Exclude hex-ID assets from repack')

    s = sub.add_parser('repack-dir', help='Repack from extracted dir (supports lang suffixes)')
    s.add_argument('--archive-dir', required=True, help='Original archive directory')
    s.add_argument('--archive', required=True, help='Archive name to repack')
    s.add_argument('--dir', required=True, help='Directory with extracted/modified files')
    s.add_argument('--output-archive', default=None, help='Output archive path')
    s.add_argument('--output-toc', default='toc.new', help='Output TOC path')
    s.add_argument('--flat', action='store_true', help='Files in dir are flat (no subdirs)')

    s = sub.add_parser('csv', help='Export asset list to CSV')
    s.add_argument('--output', default='assets.csv')
    s.add_argument('--archive-dir', default=None, help='Archive dir for language detection on localization files')

    s = sub.add_parser('hash', help='Compute hash for a path string')
    s.add_argument('path')

    s = sub.add_parser('dag', help='Search DAG names or build hash DB')
    s.add_argument('--dag', default='dag')
    s.add_argument('--search'); s.add_argument('--output', default='PS4AssetHashes.txt')

    s = sub.add_parser('loc-export', help='Export localization asset → CSV')
    s.add_argument('input', help='Localization file path (extracted .localization asset)')
    s.add_argument('output', help='Output CSV path')

    s = sub.add_parser('loc-import', help='Import translated CSV → localization asset')
    s.add_argument('input', help='Original localization file path')
    s.add_argument('csv', help='Translated CSV file path')
    s.add_argument('output', help='Output localization file path')

    s = sub.add_parser('patch', help='Patch specific assets → small mod archive + new TOC')
    s.add_argument('--archive-dir', required=True, help='Game archive directory')
    s.add_argument('--mod-name', required=True, help='Name for the mod archive file')
    s.add_argument('--files', nargs='+', required=True,
                   help='asset=file pairs (e.g. "0xBE55D94F171BF8DE=modified.localization")')
    s.add_argument('--output-toc', default='toc.new', help='Output TOC path')
    s.add_argument('--no-backup', action='store_true', help='Skip TOC backup')

    args = p.parse_args()
    cmds = {
        'build-hashdb': cmd_build_hashdb, 'info': cmd_info,
        'list': cmd_list, 'extract': cmd_extract, 'csv': cmd_csv,
        'hash': cmd_hash, 'dag': cmd_dag,
        'repack': cmd_repack, 'repack-dir': cmd_repack_dir,
        'loc-export': cmd_loc_export, 'loc-import': cmd_loc_import,
        'patch': cmd_patch,
    }
    if args.cmd not in cmds: p.print_help(); return
    cmds[args.cmd](args)

if __name__ == '__main__':
    main()
