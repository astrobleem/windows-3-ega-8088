# Source-derived instruction semantics

This suite extracts the **built source driver's own instruction fragments** using its linker MAP labels and tests them in bounded DOS programs. It does not use stock-driver offsets or apply a binary patch.

The qualified driver SHA-256 is:

`3027415d8dc8410bd7bd42ece6e007424df049e9b739642ed3d8eb3967c79ba4`

[RESULTS.json](RESULTS.json) records exact driver, MAP, generated assembly and test-COM hashes, guest results, and mutation controls. The original binary-patch experiments are not inputs to this suite.

## Verified coverage

Three positive suites passed **290,816 cases plus eight exact-emitter checks**:

- **base: 268,288 cases.** Both direct repeated SHR sequences cover every 16-bit input with two complementary incoming flag patterns. Generated rotations cover every byte at all eight phases, with both flag patterns. All eight source DDA memory-PUSH/JMP sequences cover 256 flag patterns each, checking registers, flags, stack depth, and the return IP actually visible to the callee.
- **rep: 20,480 cases.** All ten exact inline copy loops cover counts 0, 1, 2, 3, 7, 255, 256, 257 and all 256 combinations of CF/PF/AF/ZF/SF/IF/DF/OF. Distinct CS, DS and ES source patterns detect wrong segment overrides. Every destination byte and surrounding guard bytes are checked.
- **emitter: 2,048 cases.** All eight phases and all 256 mode bytes cover the optional eight-byte suffix. Checks output, lengths, registers, stack, defined flags, all unused buffer bytes, and 16-byte leading/trailing guards. Rotation output is exactly repeated `D0 C0` or `D0 C8`, never the later-CPU `C0` immediate-count opcode.

Three test-only mutants were rejected at the expected stage:

- A SHR changed to SHL fails on input 1.
- An ES source override changed to DS fails on count 1.
- An emitter choosing ROR in place of ROL fails at phase 1.

The mutants modify generated test COMs only, never the driver.

## Requirements

- Python 3.10 or newer.
- GNU binutils: `as`, `ld` with `elf_i386` support, and `objdump`.
- An installed DOSBox-X for execution. The supplied runner uses POSIX `fcntl`, process groups and `ps` and therefore needs a POSIX host.
- An existing, nonempty shared emulator lease file, coordinated with other emulator owners. The runner never creates or replaces it, refuses another live emulator, and limits each run to 120 seconds by default. A watchdog only stops the process group it launched.
- A built `EGA88.DRV` and its matching `SRC/EGA88.MAP` from this project's build.

There are no historical compiler executables, Windows installation files, driver binaries, or prebuilt test binaries in this test directory. The test compiler generates its COMs locally.

## Build the tests

From the repository root, substitute your actual build/output paths:

```sh
python tests/semantics/build_source_semantics.py \
  --candidate /path/to/driver-build/EGA88.DRV \
  --map /path/to/driver-build/SRC/EGA88.MAP \
  --out /path/to/semantics-build

python tests/semantics/build_source_negative.py \
  --build /path/to/semantics-build
```

The builder and the three files in `templates/` are the complete source dependencies. The templates contain the test harness and independent oracles. Every subject fragment is inserted from the supplied driver. GNU assembler `.arch i8086` restricts the harness instructions. The builder checks the extracted fragment encodings and MAP-derived DDA return targets before compiling.

Each suite directory retains `SEMANTIC.S`, `SEMANTIC.O`, `SEMANTIC.COM`, `SEMANTIC.DIS` and `BUILD.json`. `EXTRACTION.json` records label anchors, locations and exact bytes. These local build records may contain your local input paths; the published `RESULTS.json` intentionally contains none.

## Run the tests

Use a fresh output directory for every run. Coordinate emulator use before starting:

```sh
python tests/semantics/run_semantics.py \
  --dosbox /path/to/dosbox-x \
  --lease /path/to/existing-shared-emulator.lock \
  --build /path/to/semantics-build/base \
  --out /path/to/new-base-results
```

Repeat with `rep` and `emitter` in place of `base`, using fresh output directories.

For mutation controls, use the corresponding build directory and expected failure stage:

- `negative_shift`: `--expect-failure-stage 1`
- `negative_prefix`: `--expect-failure-stage 5`
- `negative_rotate`: `--expect-failure-stage 6`

A negative control's `PASS.json` means the checker correctly rejected the mutant, not that the mutant passed the instruction tests. Every run retains the guest result, configuration, host log, input metadata, and process/lease outcome.

## Oracle and relocation details

SHR expected values use unsigned division and a host-generated parity table. Rotate expectations use exhaustive Python bit arithmetic. Copy expectations use source-pattern arithmetic and affected address ranges, not another string-copy routine.

Static repeated shifts and inline copy loops receive a test-only RET for isolated execution. The exact-emitter base check disables its optional suffix and copies the fragment without address relocation. The full emitter test relocates only the MOV SI source address to the copied eight-byte template. DDA tests relocate the CS-memory operand and stored return address into their test COM while preserving the instruction opcodes and testing the original target relationship.

## Limits

These runs use DOSBox-X's experimental `8086_prefetch` model, **not a true or cycle-accurate 8088**. They do not test physical interrupt restart behavior or every graphics input. Copy counts are bounded; these cases do not cover overlapping buffers, 16-bit address wrap or arbitrary interrupt schedules.

SHR AF and multi-bit OF are undefined and are excluded. Rotate OF is checked for no-op and single-bit rotations, and excluded for multi-bit rotations. The generator requires DF=0 and intentionally changes working registers and arithmetic flags. The full emitter test checks those defined results; it does not claim the emitter preserves all registers. The optional graphics suffix is copied and inspected, not executed as a complete graphics operation.

## Independent check of captured generated buffers

[GENERATED_TRACE_REVIEW.json](GENERATED_TRACE_REVIEW.json) independently verifies 64 diagnostic pre-execution snapshots: 5,275 instructions, 834 count-one rotates in 371 phase-correct groups, and 304 internal, instruction-aligned branches. Every buffer ends in a reachable far return with consistent and balanced data-stack depth. Captured lengths are 74–213 bytes versus a 600-byte reservation. All normalized log bytes match the captured binary files.

The checker decodes a documented 8086 subset independently of the supplied objdump output and fails closed on unknown forms. Its small [self-test](TRACE_DECODER_SELFTEST.json) rejects immediate-count rotates, operand-size overrides, undocumented shifts and truncation. It is not a universal x86 decoder; new captures containing other legitimate instructions may require reviewed decoder extensions.

```sh
python tests/semantics/verify_generated_trace.py \
  --log /path/to/diagnostic/HOST.LOG \
  --buffers /path/to/captured-buffers \
  --output /path/to/new-trace-review.json
```

This observation is limited to the first 64 nonzero-phase generated buffers. It is not an execution trace or exhaustive maximum-size proof, and the diagnostic capture contains no guard-byte evidence. The released driver is unchanged by the separate diagnostic build.
