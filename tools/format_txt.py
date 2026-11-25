#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把 common 下 txt 的缩进统一成 tab（4 空格 = 1 tab）。

用法：
  python tools/format_txt.py --check   只报告，不写盘
  python tools/format_txt.py           真的改

只动行首的空格缩进，行内内容和换行符不变。缩进不是 4 的倍数的行跳过并报出来。
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def convert(text):
    out = []
    odd = []
    changed = 0
    for i, line in enumerate(text.splitlines(), 1):
        m = re.match(r"^( +)(\S)", line)
        if not m:
            out.append(line)
            continue
        count = len(m.group(1))
        if count % 4:
            odd.append((i, count))
            out.append(line)
            continue
        out.append("\t" * (count // 4) + line[count:])
        changed += 1
    return "\n".join(out), changed, odd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    total_files = 0
    total_lines = 0
    for path in sorted(ROOT.glob("common/**/*.txt")):
        raw = path.read_bytes()
        bom = raw[:3] == b"\xef\xbb\xbf"
        text = raw.decode("utf-8-sig")
        new_text, changed, odd = convert(text)
        if not changed and not odd:
            continue
        total_files += 1
        total_lines += changed
        print("%s  改 %d 行%s" % (path.relative_to(ROOT), changed,
                                 "" if not odd else "，%d 行缩进不是 4 的倍数（跳过）" % len(odd)))
        for line_no, count in odd[:3]:
            print("    第 %d 行缩进 %d 个空格" % (line_no, count))
        if args.check or not changed:
            continue
        out = new_text.replace("\r\n", "\n")
        data = out.encode("utf-8")
        if bom:
            data = b"\xef\xbb\xbf" + data
        with path.open("wb") as f:
            f.write(data.replace(b"\n", b"\r\n"))

    print("---")
    print("%s：%d 个文件，%d 行" % ("待改" if args.check else "已改", total_files, total_lines))
    sys.exit(0)


if __name__ == "__main__":
    main()
