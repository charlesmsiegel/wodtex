# Implementation ledger

The approved design and eight-task plan in this directory govern this work.
The handoff branch starts at `4f71fc5c0d289edcb845bcb096ae8f0c8b2da7ce`.

Pre-flight interfaces: Task 1 measured geometry/fonts feed Task 2 composition;
Task 2 ordered segment/shipout records feed Task 3 long flow and Task 4 art;
Task 2 semantics feed Tasks 5 and 6 navigation/conversion; Tasks 5/6 build
reports feed Task 7 verification; passing outputs feed Task 8 packaging.

Baseline: 13 tests ran; 7 failed and 3 errored. Missing prepared LuaLaTeX
format and an importer requiring absent external profile/audit files block it.

Ruling: recover the exact branch through GitHub Git objects because ordinary
git authentication is unavailable. Preserve the original commit and history;
publish fast-forward commits through the GitHub plugin. Cost if wrong: no
loss of existing history; an unsuccessful ref update leaves the branch intact.

Ruling: regenerate asset/profile metadata directly from the supplied IDML and
font/art input tree rather than requiring another untracked project's JSON.
The original IDML remains authoritative. Cost if wrong: decoration measurements
need correction during visual calibration; original inputs remain unchanged.

Runtime/profile checkpoint: official pinned dependencies and supplied original
font/art files recovered; eight runtime/profile tests pass. Actual LuaLaTeX
font smoke compiled twice, rendered, and visually inspected. Tiny EPUB runtime
smoke still requires a missing transitive TeX4ht dependency. Task 1 is therefore
not claimed complete yet. No licensed inputs are committed.
