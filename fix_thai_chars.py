#!/usr/bin/env python3
"""
fix_thai_chars.py — Auto-fix keyboard-mapping errors in Thai localization files.

The translator's IME substituted these chars systematically:
  ฃ (U+0E03) → ่ (U+0E48)  mai ek         56,217 occurrences
  ฅ (U+0E05) → ้ (U+0E49)  mai tho        54,946 occurrences
  ๎ (U+0E4E) → ็ (U+0E47)  mai tai khu     1,544 occurrences
  ๏ (U+0E4F) → ี (U+0E35)  sara ii           940 occurrences
  ๚ (U+0E5A) → ๊ (U+0E4A)  mai tri            56 occurrences
  ๛ (U+0E5B) → ๋ (U+0E4B)  mai chattawa      108 occurrences
  Total: ~113,811 replacements

NOT fixed automatically (ambiguous):
  U+FFFD (22,513) — original byte lost; need source CSV saved as UTF-8
  ๙ Thai-9 (1,425) — also appears as legitimate Thai digit 9
  ๘ Thai-8 (223)   — also appears as legitimate Thai digit 8

Usage:
  python3 fix_thai_chars.py <input_loc_file> <output_loc_file> [--dry-run]
"""
import sys, struct, argparse

try:
    import lz4.block
    HAS_LZ4 = True
except ImportError:
    HAS_LZ4 = False

# ─── Substitution table ──────────────────────────────────────────────────────
# Two forms: translate table for fast string replacement, dict for counting
CHAR_FIX = {
    '\u0E03': '\u0E48',  # ฃ → ่  mai ek
    '\u0E05': '\u0E49',  # ฅ → ้  mai tho
    '\u0E4E': '\u0E47',  # ๎ → ็  mai tai khu
    '\u0E4F': '\u0E35',  # ๏ → ี  sara ii
    '\u0E5A': '\u0E4A',  # ๚ → ๊  mai tri
    '\u0E5B': '\u0E4B',  # ๛ → ๋  mai chattawa
}
CHAR_FIX_TABLE = str.maketrans(CHAR_FIX)

FIX_DESC = {
    '\u0E03': 'ฃ→่  mai ek',
    '\u0E05': 'ฅ→้  mai tho',
    '\u0E4E': '๎→็  mai tai khu',
    '\u0E4F': '๏→ี  sara ii',
    '\u0E5A': '๚→๊  mai tri',
    '\u0E5B': '๛→๋  mai chattawa',
}

# Section hashes
_LOC_KEY_DATA = 0x4D73CEBD
_LOC_KEY_OFF  = 0xA4EA55B2
_LOC_TR_DATA  = 0x70A382B8
_LOC_TR_OFF   = 0xF80DEEB4

# Magic constants
_MAGIC_LZ4     = 0x122BB0AB
_MAGIC_WRAPPER = 0xBA20AFB5


def _decompress(raw: bytes) -> bytes:
    magic = struct.unpack('<I', raw[0:4])[0]
    if magic == _MAGIC_LZ4:
        if not HAS_LZ4:
            print("ERROR: lz4 not installed. Run: pip install lz4"); sys.exit(1)
        rawsize = struct.unpack('<I', raw[4:8])[0]
        return lz4.block.decompress(raw[0x24:], uncompressed_size=rawsize)
    elif magic == _MAGIC_WRAPPER:
        return raw[0x24:]
    raise ValueError(f"Unknown magic 0x{magic:08X}")


def _compress(dec: bytes, magic: int) -> bytes:
    if magic == _MAGIC_WRAPPER:
        header = struct.pack('<I', magic) + struct.pack('<I', len(dec)) + b'\x00' * 28
        return header + dec
    if not HAS_LZ4:
        print("ERROR: lz4 not installed. Run: pip install lz4"); sys.exit(1)
    compressed = lz4.block.compress(dec, store_size=False)
    header = struct.pack('<I', magic) + struct.pack('<I', len(dec)) + b'\x00' * 28
    return header + compressed


def _parse_sections(dec: bytes) -> dict:
    nsec = struct.unpack('<I', dec[12:16])[0]
    secs = {}; pos = 16
    for _ in range(nsec):
        h, off, sz = struct.unpack('<III', dec[pos:pos+12])
        secs[h] = (off, sz); pos += 12
    return secs


def fix_loc_file(in_path: str, out_path: str, dry_run: bool = False) -> dict:
    """
    Read a localization file, fix Thai keyboard-mapping errors, write result.
    Returns stats dict.
    """
    with open(in_path, 'rb') as f:
        raw = f.read()

    magic = struct.unpack('<I', raw[0:4])[0]
    dec   = _decompress(raw)
    secs  = _parse_sections(dec)

    if not all(k in secs for k in [_LOC_KEY_DATA, _LOC_KEY_OFF, _LOC_TR_DATA, _LOC_TR_OFF]):
        raise ValueError("Missing required DAT1 sections — not a localization file?")

    kd_off        = secs[_LOC_KEY_DATA][0]
    ko_off, ko_sz = secs[_LOC_KEY_OFF]
    td_off, td_sz = secs[_LOC_TR_DATA]
    to_off        = secs[_LOC_TR_OFF][0]
    count         = ko_sz // 4

    # ─── Rebuild translation data with fixed strings ─────────────────────────
    new_tr_data    = bytearray()
    new_tr_offsets = []
    char_stats     = {ch: 0 for ch in CHAR_FIX}
    strings_fixed  = 0

    for i in range(count):
        ko = struct.unpack('<i', dec[ko_off+i*4:ko_off+i*4+4])[0]
        to = struct.unpack('<i', dec[to_off+i*4:to_off+i*4+4])[0]

        if to == 0:
            kpos = kd_off + ko
            key  = dec[kpos:dec.index(b'\x00', kpos)].decode('utf-8', errors='replace')
            if key != 'INVALID':
                new_tr_offsets.append(0)
                continue
            # INVALID with to==0: write empty null
            new_tr_offsets.append(len(new_tr_data))
            new_tr_data.extend(b'\x00')
            continue

        tpos  = td_off + to
        tend  = dec.index(b'\x00', tpos)
        val   = dec[tpos:tend].decode('utf-8', errors='replace')

        # Count and apply substitutions
        fixed = val.translate(CHAR_FIX_TABLE)
        if fixed != val:
            strings_fixed += 1
            for ch in CHAR_FIX:
                n = val.count(ch)
                if n:
                    char_stats[ch] += n

        new_tr_offsets.append(len(new_tr_data))
        new_tr_data.extend(fixed.encode('utf-8') + b'\x00')

    if dry_run:
        return {
            'strings_fixed': strings_fixed,
            'char_stats': char_stats,
            'total_chars': sum(char_stats.values()),
            'dry_run': True,
        }

    # ─── Patch dec buffer ────────────────────────────────────────────────────
    buf = bytearray(dec)

    # Write new translation offsets
    for i in range(count):
        struct.pack_into('<i', buf, to_off + i*4, new_tr_offsets[i])

    # Replace TR_DATA section — it's the last section by offset, safe to truncate
    new_td   = bytes(new_tr_data)
    all_secs = sorted(secs.items(), key=lambda x: x[1][0])

    if all_secs[-1][0] == _LOC_TR_DATA:
        new_dec_buf = bytearray(buf[:td_off]) + bytearray(new_td)
        # Update TR_DATA size in DAT1 section header
        nsec = struct.unpack('<I', new_dec_buf[12:16])[0]
        pos  = 16
        for _ in range(nsec):
            h = struct.unpack('<I', new_dec_buf[pos:pos+4])[0]
            if h == _LOC_TR_DATA:
                struct.pack_into('<I', new_dec_buf, pos+8, len(new_td))
            pos += 12
        new_dec = bytes(new_dec_buf)
    else:
        # Fallback: patch in place
        new_dec_buf = bytearray(buf)
        new_dec_buf[td_off:td_off+len(new_td)] = new_td
        new_dec = bytes(new_dec_buf)

    out_data = _compress(new_dec, magic)
    with open(out_path, 'wb') as f:
        f.write(out_data)

    return {
        'strings_fixed': strings_fixed,
        'char_stats': char_stats,
        'total_chars': sum(char_stats.values()),
        'in_size':  len(raw),
        'out_size': len(out_data),
        'dry_run':  False,
    }


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('input',  help='Input localization file (extracted from archive)')
    parser.add_argument('output', help='Output fixed localization file')
    parser.add_argument('--dry-run', action='store_true',
                        help='Count replacements without writing output file')
    args = parser.parse_args()

    print(f"Reading: {args.input}")
    result = fix_loc_file(args.input, args.output, dry_run=args.dry_run)

    print(f"\n{'DRY RUN — ' if result['dry_run'] else ''}Results:")
    print(f"  Strings fixed : {result['strings_fixed']:,}")
    print(f"  Total chars   : {result['total_chars']:,}")
    print(f"  Breakdown:")
    for ch, desc in FIX_DESC.items():
        n = result['char_stats'].get(ch, 0)
        if n:
            print(f"    {desc}: {n:,}")

    if not result['dry_run']:
        print(f"\n  Input  : {result['in_size']:,} bytes")
        print(f"  Output : {result['out_size']:,} bytes")
        print(f"  Saved  : {args.output}")

    print(f"\n⚠️  Remaining issues requiring manual fix:")
    print(f"  U+FFFD ~22,513 chars — re-save source CSV as UTF-8 then re-import")
    print(f"  ๙/๘ Thai digits 9/8 may appear as wrong tone marks — verify manually")


if __name__ == '__main__':
    main()
