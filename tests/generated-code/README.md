# Diagnostic generated-code capture

This optional experiment instruments the source at CBLT's completed-buffer point, immediately after the final RETF is written. It emits the first 64 **nonzero-phase** generated buffers to the emulator's Bochs E9 debug port, saving and restoring the emitter's registers and flags. The ordinary release driver is unchanged.

The captured experiment used a separate diagnostic binary, SHA-256 `a485f917c9a0f5b9f5e099ad5d09e5ecca6955d13f4ab44990b416dc590b9559`. The source-built release remains `3027415d8dc8410bd7bd42ece6e007424df049e9b739642ed3d8eb3967c79ba4`.

[Capture summary](../../evidence/GENERATED-CODE-CAPTURE.json): 64 buffers, phases 1–7, 834 single-bit rotates, maximum observed length 213 bytes, no unsupported encodings observed by the parser. [Rendering comparison](../../evidence/COMPARE-generated-code-capture.json): all eight QA frames match the uninstrumented source driver.

This is an **after-generation, before-execution byte capture**, not an executed instruction trace, an exact first-fault trace or an exhaustive maximum-size proof. It does not replace the source-level 600-byte allocation bound.

## Helpers

`prepare_trace.py EXISTING_BUILD NEW_DIAGNOSTIC_BUILD` copies an existing completed build into a fresh directory, modifies only CBLT.ASM and writes a batch file that recompiles CBLT and relinks. It never edits the original build. It reuses the other source-built objects and locally supplied tools; none are included in this test directory.

Compile that batch through the shared emulator guard, attach the same source-built resources, and run the existing EGAQA application in a disposable Windows 3.0 real-mode fixture with DOSBox-X E9 debug logging enabled. Windows installation files and ready-made guest fixtures are intentionally not included. Do not use the diagnostic driver as the release driver.

Parse the resulting host log with GNU objdump installed:

```sh
python tests/generated-code/parse_trace.py \
  --host-log /path/to/diagnostic/HOST.LOG \
  --input /path/to/diagnostic/INPUT.json \
  --out /path/to/new-capture-directory
```

INPUT.json must contain the diagnostic driver's `sha256`. The parser expects exactly the bounded 64 records and retains decoded bytes/disassembly in the local output directory. The repository includes the summary and helpers, not captured executable buffers or a diagnostic binary.
