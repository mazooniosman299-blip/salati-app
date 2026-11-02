# Salati: literal Madar mushaf reference acceptance (2 November 2026)

Status: **NOT APPROVED / DO NOT MERGE OR PUBLISH**. The user requires a literal, not approximate, match to their Madar Software Mushaf Al-Madinah reference image.

## Fixed requirements

- Preserve Salati's **original dark-only interface** and navigation; do not replace the existing app or invent a new homepage.
- Use the *exact* approved page artwork: Uthmani calligraphy, blue page decorations, ayah medallions, line breaks, and page distribution. Identical page geometry is not proven by using an Uthmani font alone.
- The recitation controls belong inside the **lower part of the existing mushaf frame**, after the Quran scrollport in document flow. The player must not float over, obscure, delete, crop, or alter any ayah.
- Keep the existing 604-page indexing, reciters, audio state, bookmarks, vertical scrolling, and Android WebView behavior.

## Provenance and usage rights gate

The repository currently includes MadinahHafsClassic.ttf (KFGQPC licensed as documented in dist/fonts/KFGQPC-HAFS-LICENSE.txt), Quran page metadata from quran-meta, Tanzil Uthmani text, and separately designed Quran ornament SVGs. **These do not prove** that the page images or blue decoration match Madar Software's artwork.

The King Fahd Complex offers printable Madinah Mushaf digital vectors with an explicit free use statement for websites and software:
https://dm.qurancomplex.gov.sa/rights/
These are a potentially usable **alternative source**, not permission to copy proprietary Madar Software UI and not proof of pixel identity to the user's reference.

To pass this gate, obtain the precise source edition and all 604 page assets from an authorized, documented source; compare the same numbered sample pages at the same physical viewport and resolution, including line layout, blue borders, verse ornaments, and lettering. Record asset hashes, source URLs, usage terms and page-to-ayah mapping. If the authorized assets do not match, STOP and do not present an approximation as an identical mushaf.

## Scope of this pending change

The player was moved into #qSheet after #qVerses / #qPageLabel. The page text and Quran data.json were **not modified**. This only fixes an independent layout requirement. A new responsive Chromium check asserts the player is inside #qSheet, outside #qVerses, and below every verse with no covering overlay.

The screenshot comparison against the **specific Madar Software reference** and original licensed page-artwork integration remain **unverified and outstanding**. Keep this PR in draft; no production deployment, signed APK release, or claim of 100% matching is authorized.
