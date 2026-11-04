# Validation and remaining limits

Qualified driver: 57,392 bytes, SHA-256 `3027415d8dc8410bd7bd42ece6e007424df049e9b739642ed3d8eb3967c79ba4`.

## Source and binary checks

- The retail DDK and matching SDK sources rebuild all 39 explicit object modules.
- MASM `.8086` guards and the independent listing audit cover 14,738 emitted instruction rows. Numeric runtime-code templates are not mistaken for ordinary instructions; the generator is reviewed and tested separately.
- OMF segment contributions, alignment and final linker MAP lengths agree exactly. No additional library CODE or DATA is left outside the audited module set.
- Prefix decoding across all listings finds ten replacement MOVS loops, 44 retained ordinary single-prefix REP instructions, and no multi-prefix REP instruction.
- Resources are compiled from source, packed into 74 records and roundtrip-checked. Packing preserves the linked segment payloads and relocations.

## Windows GUI comparison

The same source-built driver ran under Windows 3.0 real mode in DOSBox-X's `8086_prefetch` and 386 models, with EGA selected. Both reported 640×350, 16 colors, `FAILURES=0` and `COMPLETE=1`. A stock Microsoft EGA.DRV control ran under the 386 model. All eight four-plane captures were byte-identical across these runs.

The stages in `tests/EGAQA.C` are:

1. Sixteen-color palette bars.
2. All 64 source/destination bit-phase pairs for memory-to-screen SRCCOPY.
3. Fifteen selected ROP3 operations.
4. All sixteen ROP2 settings for representative lines and rectangles.
5. Four overlapping screen-copy directions.
6. Rectangular clipping and representative off-screen transfers.
7. Representative opaque text in sixteen foreground/background combinations.
8. Screen-to-memory-to-screen transfers across eight phases.

Each capture stores four planes of 28,000 bytes, for 112,000 bytes per frame. `tests/compare_planes.py REFERENCE_DIRECTORY CANDIDATE_DIRECTORY` checks the expected successful log fields, exact capture lengths and every byte. `evidence/COMPARE-*.json` retains the comparison hashes and logs without private fixture paths.

The GUI harness checks every BitBlt return and verifies creation of its compatible memory DC/bitmap. It does not check every other GDI API return or every pen/brush/region allocation. The comparisons are deterministic rendering evidence, not blanket certification of all APIs.

## Startup controls and invalid fixtures

- The source-built driver completes the GUI exerciser on the 8086-prefetch and 386 models.
- The stock EGA driver completes the same exerciser on the 386 model.
- With the validated matching EGA assets, the unmodified stock EGA driver stalls on the 8086-prefetch model before the QA log appears; a 20-second watchdog ends that run. This is not an executed first-fault trace, and no exact failing instruction is claimed from the stall alone.
- A stock CGA driver boots the same Windows real-mode installation on the 8086-prefetch model at 640×200, 2 colors. This provides a separate installation/CPU control.
- Early fixtures still contained SZDD-compressed font/driver files and were invalid installations. Their startup failures are excluded from the comparison evidence. The successful runs use expanded matching assets.

## Actual screenshot

`evidence/EGA88-source-built-working.png` is a screenshot of the actual emulated Windows display, showing the source-built driver running `tests/EGADEMO.C`. The source driver hash and emulator configuration are in `evidence/DEMO-INPUT.json`; the demo's real-mode/dimension output is in `evidence/DEMO.LOG`. The screenshot is not a conversion of a frame dump or an illustration.

## Not established by these tests

- Physical 8088/8086 execution, bus timing, prefetch behavior or injected interrupts during string operations.
- Every EGA board or BIOS, small-memory configuration, or emulator CPU model.
- Every ROP3 value, arbitrary GDI argument, huge bitmap, font format, DIB/RLE conversion, cursor intersection or screen-save scenario.
- Long-running stability, repeated Windows exit/re-entry, task switching and every application.
- Protected-mode Windows support. The port intentionally rejects protected-mode enablement.

The original 8088 lacks the later invalid-opcode exception. An emulator rejection or hang of the stock driver is useful evidence of incompatibility but is not a claim that physical hardware raises the same fault.

## Source-derived instruction semantics and generated-code sampling

The [instruction semantics suite](../tests/semantics/README.md) extracts fragments from the final source-built driver using its MAP labels. It passes 290,816 cases plus eight exact-emitter checks and rejects three deliberate mutants. The suite includes shift values/flags, all eight source DDA memory-push expansions, all ten inline MOVS loops and the full phase emitter including its optional suffix. Its README spells out oracle assumptions, relocation and bounded-input limits.

A [separate diagnostic source variant](../tests/generated-code/README.md) captures 64 generated buffers before their execution. These cover all seven nonzero phases, with 834 count-one rotates, maximum observed size 213 bytes and no unsupported encoding observed. All eight GUI captures match the ordinary source driver. This is a sample of actual generated code, not an execution trace or an exhaustive buffer bound.
