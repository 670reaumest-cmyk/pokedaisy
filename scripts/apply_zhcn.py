#!/usr/bin/env python3
"""PokeDaisy 1.3.3 Simplified Chinese translations. Never modifies ROM cores."""
from pathlib import Path
import csv, json, re, collections
root = Path(__file__).resolve().parents[1]
base = root / "app/src/main/kotlin/com/pokedaisy/app/companion/i18n"
file1 = root / "zhcn/translations-part1.csv"
file2 = root / "zhcn/translations-part2.csv"
rows = []
for file in (file1,file2):
    with file.open(encoding="utf-8-sig",newline="") as stream:
        rows.extend(csv.DictReader(stream))
assert len(rows) == 1345, f"Expected 1345, got {len(rows)}"
groups = {"TrCoreKt":"Core","TrLibraryKt":"Library","TrSettingsKt":"Settings","TrCompanionKt":"Companion","TrCompanionInfoKt":"CompanionInfo"}
assert all(r["模块"] in groups and r["English key"] and r["简体中文"] for r in rows)
def placeholders(s): return sorted(re.findall(r"\{\d+\}",s))
assert all(placeholders(r["English key"])==placeholders(r["简体中文"]) for r in rows), "Placeholder mismatch"
assert len({r["English key"] for r in rows})==len(rows), "Duplicate translation key"
def kotlin(s):
    return '"'+s.replace("\\","\\\\").replace('"','\\"').replace("\n","\\n").replace("\r","\\r").replace("\t","\\t").replace("$","\\$")+'"'
for module,name in groups.items():
    pairs = [f"        {kotlin(r['English key'])} to {kotlin(r['简体中文'])}," for r in rows if r["模块"]==module]
    (base/f"TrZh{name}.kt").write_text(
        "// Unofficial Simplified Chinese interface localization. Does not translate ROM assets.\n"
        "package com.pokedaisy.app.companion.i18n\n\n"
        f"internal val trZh{name}: Map<String, String> by lazy {{\n    mapOf(\n" + "\n".join(pairs) + "\n    )\n}\n",encoding="utf-8")
(base/"TrZhAll.kt").write_text(
    "package com.pokedaisy.app.companion.i18n\n"
    "internal val zhCNTranslations: Map<String, String> by lazy {\n"
    "    trZhCore + trZhLibrary + trZhSettings + trZhCompanion + trZhCompanionInfo\n}\n", encoding="utf-8")
l10n = base / "L10n.kt"
text = l10n.read_text(encoding="utf-8")
edits = [
 ('    PT("PT", null, "pt", "PORTUGUÊS (PT)"),',
  '    PT("PT", null, "pt", "PORTUGUÊS (PT)"),\n    ZH("ZH", null, "zh", "简体中文"),'),
 ('        AppLanguage.PT -> pt','        AppLanguage.PT -> pt\n        AppLanguage.ZH -> null'),
 ('    val lang = L10n.language\n    if (lang != AppLanguage.EN)',
  '    val lang = L10n.language\n    if (lang == AppLanguage.ZH) return zhCNTranslations[en] ?: en.substringBefore(\'|\')\n    if (lang != AppLanguage.EN)')
]
for old,new in edits:
    assert text.count(old)==1, f"Unexpected source shape: {old!r}"
    text=text.replace(old,new,1)
l10n.write_text(text,encoding="utf-8")
print("Applied",len(rows),"Simplified Chinese UI entries without touching ROM core code")
