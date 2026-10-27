# Provenance and retrospective Git history

**The early Git history was retrospectively reconstructed in October 2026 from recovered source artifacts and development records. Historically dated commits are archival representations, not Git commits originally created on those dates.**

The original project had no Git history. Reconstruction preserves recoverable code stages while keeping later organization and release preparation current-dated. No missing source stage is invented. The original evidence remains private and unchanged.

## Evidence and method

- **E01:** native Claude source-creation input, Lark interpreter. Original stream interval `2026-06-01T01:51:58.964494Z`–`2026-06-01T01:52:50.772340Z`. Recorded tests failed parsing.
- **E02:** native Claude literal shell-heredoc input, recursive-descent rewrite. Interval `2026-06-01T01:53:13.846065Z`–`2026-06-01T01:54:18.645734Z`. Exact bytes match a subsequently saved standalone file and a Gemini Takeout attachment. The source-size/mtime fields in a bytecode header provide additional timing corroboration; semantic equivalence of that bytecode was not established.
- **E03:** complete expanded interpreter saved on June 13. Recorded file last-write `2026-06-13T05:48:09.7080931Z` is a conservative snapshot bound. A recovered Gemini code block matches apart from an extra terminal newline. The downloaded file's exact bytes are imported; the timestamp is not authenticated source-generation completion.
- **E04:** complete browser HTML, verified against the forensic manifest. Last-write `2026-06-13T06:26:01.3559436Z` is corroborated to the second by the recorded final Antigravity patch. It is not dated at the earlier file creation time.
- **E05:** original documentation and four examples, each verified by SHA-256. Last included source last-write `2026-06-13T06:34:31.0597954Z` bounds the group; saved documentation-generation actions corroborate it. The calculator also has an independently saved, hash-matching editor-history version. Other examples rely on recorded filesystem metadata rather than independently complete early revisions.

The original native Claude records preserve the explicit design proposal at `2026-06-01T01:50:30.305434Z` and naming at `2026-06-01T01:51:46.207303Z` (May 31 evening EDT). A later pasted transcript alone would not authenticate that date. The native export, matching source inputs and Takeout attachment offer stronger corroboration, but local metadata is not signed proof of authorship, priority or immutability.

Both Git author and committer dates use the selected historical second, retaining EDT offset. Subsecond precision is **truncated, not represented by Git**, and retained below and in evidence/snapshots.json. Stream-completion dates describe recorded inputs, not proof of the precise sandbox write time. The configured human/project Git identity is used, not an impersonated AI identity.

No code or modern provenance documents appear before their supported source snapshot. Five normalized HTML states derived by reversing recorded diffs remain in the private evidence package and are not promoted to independent historical originals. A truncated earlier diff limits that reconstruction.

## Commit-to-evidence mapping

| Archival commit | Author and committer timestamp | Source snapshot and SHA-256 | Evidence and limitations |
| --- | --- | --- | --- |
| `42437b95b3b54a1b483fea1fa1907872e197a978` | `2026-05-31T21:52:50-04:00` | `mozhi.py`: `2ef5c23c870aba52952e6891bd2a80db39dc6f9f70e8ca7dfd2b8cc997b5a2eb` | E01: Completion of recorded create_file input stream; known parser failures; does not date original conception. |
| `447bb1973a3d6776ef6e534026c545d333174233` | `2026-05-31T21:54:18-04:00` | `mozhi.py`: `97fe0e7c8cb0d9e2c567c3edcb021cd957ada2933b38c9460f1c853b780d87b9` | E02: Completion of literal shell-heredoc input stream; native source equals two later saved copies; known loop bug. |
| `4cd3b0ec149e39875412676e810fc37720d37473` | `2026-06-13T01:48:09-04:00` | `mozhi.py`: `86a9595cbf1c03646100dd39bde717f0a42f9919416c67be179d3538479175c5` | E03: Conservative bound from complete downloaded snapshot last-write; corroborated by Gemini response source differing only in extra terminal newline. Not a feature-discussion timestamp or authenticated generation time. |
| `5f67d601c6f6664479afa03fd9db4abba0fd60cb` | `2026-06-13T02:26:01-04:00` | `mozhionline.html`: `c3a6edc1251d0632410dea5f213c37c2ebe6ca9302af0ce2eb7f67a3f2f48e00` | E04: Verified current bytes and filesystem last-write corroborated by saved final Antigravity diff. Not earlier creation time. |
| `25e16453d0723b0302de6d7d64b989806ba979e5` | `2026-06-13T02:34:31-04:00` | README, configuration, eight documentation pages and four examples; individual SHA-256 values below | E05: grouped snapshot; current saved content, supported per-file times and documentation actions. |

### Original source precision and file digests

The machine-readable [snapshot index](evidence/snapshots.json) contains full UTC timestamps, file sizes, paths, SHA-256 digests, and commit/tree IDs. It is a modern evidence index, not a historical artifact.

| E05 historical path | Original last-write UTC | SHA-256 |
| --- | --- | --- |
| `calculator.mozhi` | `2026-06-13T06:19:05.9332023Z` | `7ccf87031344feff73eab09400d683b89bd853bfd5cc30ef44ad6fdc680a7997` |
| `demo.mozhi` | `2026-06-13T06:09:51.2074464Z` | `120e8583cf93b0244d5548551b8d9395991436b93e86b2be38ad34e8d964ff0b` |
| `docs/advanced/arrays.md` | `2026-06-13T06:34:24.7782088Z` | `abb9d2bba7a362e5646f392b29894db87ae19a4e56a4bf17b4400a31ccf57b2e` |
| `docs/advanced/oop.md` | `2026-06-13T06:34:28.2050439Z` | `39454b650ceaa2988a4840b86ec11990b699afa0d21c60f005c6fec45fcc1484` |
| `docs/basics/io.md` | `2026-06-13T06:34:16.9309248Z` | `58a3870a442b9ffa68207ec9d35978c51e9cb11822ddc63fed3beb23a9dd1a83` |
| `docs/basics/variables.md` | `2026-06-13T06:34:14.5512017Z` | `c641aa226f8bd5a4e7cddbc20af5f54a56c78da7ec3b5d8a64a580856ea0f2be` |
| `docs/control-flow/conditionals.md` | `2026-06-13T06:34:19.5769842Z` | `0557fe3d2b0715c376e4d0ccde1c93c7876a06b8885d5ad015407d4052bf4164` |
| `docs/control-flow/loops.md` | `2026-06-13T06:34:21.9798026Z` | `e9b30a0862aae466da187a392635a53d1cdc80cd0d4be7db0cae56df33e58c7a` |
| `docs/examples/calculator.md` | `2026-06-13T06:34:31.0597954Z` | `cddd72cae67b0ca0af6c28464a7b30597791fbf4c9b45f06f79d233abafc9b5d` |
| `docs/index.md` | `2026-06-13T06:34:12.1938722Z` | `9c992821ab288ae5fd769a8a9879c3292ee3163651a71a474805daa3aef8acb5` |
| `gossip.mozhi` | `2026-06-13T06:14:59.6839565Z` | `7b63ffbdbb14b3a5925dddaa03b833087e153406871c2fd4906d41daa80392e1` |
| `library.mozhi` | `2026-06-13T06:09:17.1042686Z` | `de5ebd3aa6bc788eb94e478dec4af1ba04a428a7b0399d3929f5108eef068198` |
| `mkdocs.yml` | `2026-06-13T06:34:09.7607076Z` | `a27545446ef7edc9bba31bfa57d10a0c3f8488545874ecb1ff549e0e65b01516` |
| `README.md` | `2026-06-13T06:34:07.3783610Z` | `54f0d1efa5d52955e7542c0dad6c69fc208ce0d2cee6e7190d90e69b055deb5a` |

## Modern path mapping

| Historical Git path | Current path |
| --- | --- |
| `mozhi.py` | `src/mozhi.py` (expanded snapshot unchanged) |
| `mozhionline.html` | `playground/index.html` (browser source unchanged) |
| Four root `.mozhi` examples | `examples/` (unchanged) |
| Original README and Markdown docs | Original versions in archival commits; current README replaced and docs corrected in October |
| Generated MkDocs site | Omitted from Git; retained privately in the forensic archive |

Modern commits use actual October creation times. They add the layout, README, license, language notes, contributor guidance, validation and this provenance index. Their IDs are ordinary Git history; no self-referential current-commit hash is embedded here. Archival commit/tree IDs are frozen and verified independently. Later verification reports are kept outside the public tree.

## Privacy and publication

Public references E01–E05 identify evidence categories without private conversation IDs, personal absolute paths, full transcripts, account data, databases or Takeout archives. No private raw evidence is included. Historical sample first names in documentation are illustrative code, not an exported contact list. Externally loaded frontend libraries are referenced by the original HTML, not vendored into this repository.

First public publication is planned for October 2026 and has not yet occurred at preparation. The GitHub repository creation date will reflect actual publication; older archival commit timestamps are not proof that a GitHub repository existed then. No historical release tags or public priority claims are made. The author explicitly chose MIT for this release.
