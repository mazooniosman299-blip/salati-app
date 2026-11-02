# Reference evidence policy — 2026-11-03

The source-controlled `design-references/APPROVED_REFERENCE_REGISTRY.json` lists each reference, whether it is truly verified, the exact file/digest, provenance and permitted scope.

**Only the original mosque and its existing lossless crops are cryptographically verified in this phase.** The latest Mushaf and player screenshot bytes have not been recovered as authenticated project assets, and the repository illustrations are not automatically a final approved design. Therefore **100% screenshot parity cannot yet be claimed**. Run `node tests/reference-provenance.cjs` in CI; fail if original mosque bytes are substituted, native/widget crop diverges, or metadata is removed.

When an actual image is available, register its original SHA-256, source approval date, element scope, rights and expected viewport, then compare captured real application screenshots against it. Do not silently convert an internet thumbnail to approved source. User intent must be determined from latest explicit request, not `PR #35` or `PR #36` alone.
