# Mozhi history

All local dates below use EDT (UTC-04:00). The native records use UTC, so May 31 evening appears as June 1 in the original export. This is a retrospective account; see PROVENANCE.md for the meaning of the Git dates.

| Recorded time | Event |
| --- | --- |
| May 31, 2026, 21:48 | Conversation begins with a question about languages for implementing a language. |
| May 31, 21:50:30.305434 | The author proposes a Tanglish language with trailing `sollu` and `vechukko`, explicitly motivated by Tamil grammatical placement. |
| May 31, 21:51:46.207303 | The author names it Mozhi, chooses hybrid syntax and corrects the loop spelling to `varaikum`. |
| May 31, 21:51:58–21:52:50 | Claude-assisted Lark implementation is generated. Recorded tests encounter parsing failures. |
| May 31, 21:53:13–21:54:18 | Recursive-descent rewrite is generated. Later tests still exhibit a runaway loop. |
| May 31, 21:54:19 | Preserved Python bytecode header records a matching-size source mtime. This corroborates timing but does not independently prove bytecode/source identity. |
| June 13, 01:13–01:18 | Gemini takeover, copied original conversation, and attachment of the earlier interpreter are recorded. |
| June 13, 01:20–01:48 | Strings, arrays, control flow and OOP are discussed and expanded code is saved. Feature discussion times do not establish completed implementations. |
| June 13, 01:58–02:26 | Antigravity records parent-scope, property/method and asynchronous browser-input repairs, then live output and input-clearing fixes. |
| June 13, 02:34–02:38 | Documentation source is generated and MkDocs is built. |
| June 15 | Further Gemini discussion revisits grammatical consistency. These discussions are not imported as a finished source version. |
| October 27, 2026 | Local archaeology recovers structured conversations, source inputs, Takeout attachments, saved files and patches. The archival Git history and modern repository are prepared. |
| October 27, 2026, 02:52:44 EDT | First public GitHub repository created (`2026-10-27T06:52:44Z`). The reconstructed history was published that day; no earlier public Git history is claimed. |

The author's language concept was developed with AI implementation assistance, initially Claude and then Gemini/Google Antigravity. One preserved test result contains 500,000 lines of `1`; this records a bug, not a successful test. Historical code is retained with its failures. The project does not claim priority over other independent languages or allege copying.

The first Lark and recursive-descent sources survive in Git history at the same original filename, `mozhi.py`. Publication initially preserved the June expanded CLI and a later independent embedded browser runtime. Modern layout changes, corrected docs, MIT licensing, tests, and provenance were added with actual October dates.

On October 27, modern runtime repairs fixed scope updates, method closures and properties, program termination, exponentiation, short-circuit evaluation, and diagnostics. Browser execution moved into a worker with Stop, an input-aware execution limit and engine recovery. Both input spellings became aliases. The asynchronous browser engine is generated from the core parser/runtime to keep these repairs consistent. These changes are modern development; the archival commits and original source digests remain unchanged.
