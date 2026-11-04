# Source changes

The port targets the retail Windows 3.0 DDK EGAHIRES driver and matching Windows 3.0 SDK. It is not a byte-identical rebuild of Microsoft's shipped EGA.DRV. The repository flattens the source include hierarchy, recording original paths/hashes in SOURCE-ORIGINS.json.

## CPU compatibility

1. Force `.8086` in linked sources and the shared macros. Set the shift macro CPU selection to 88. Reject alternate protected/386 macro modes.
2. Expand `SHR DX,3` in BITBLT and `SHR BX,2` in CBLT into repeated one-bit shifts. All defined result flags are retained; the original multi-bit overflow flag was undefined.
3. Replace the polyline macro's immediate return-address push with a CS-relative memory push. The literal follows an unconditional indirect jump, is never executed, and retains the exact original return address, stack depth, registers and flags. Eight macro expansions are emitted.
4. Make the runtime BitBlt compiler emit `D0 C0` or `D0 C8` once per phase step, rather than the unsupported `C0` immediate-rotate opcode. CX is zero before phase setup and after the REP STOSW emitter. Generated offsets and copied lengths are computed from DI.
5. Replace ten `REP` plus segment-override MOVS instructions with `JCXZ`, a single overridden MOVS and `LOOP`. This preserves zero-count handling, DF direction, registers and flags without disabling interrupts. The generated copy loop has one segment prefix at most per interrupted instruction. Ordinary single-prefix REP instructions remain.
6. Widen one assembly-time short branch in CBLT after code growth. This does not alter generated-code branch selection.

The original Windows 3.0 real-mode paths already use 8086-safe save/restore code. No PUSHA-frame emulation or unrelated Windows 3.1 backport is introduced.

## Generated buffer bound

The stock source reserves 452 bytes. Phase rotations change one payload length by d in {-1, 1, 3, 5}. The generator normally replicates an inner payload four times when its length is below 32, otherwise twice, subject to the requested byte count.

The often-missed case is a shrink from 32 bytes to 31 bytes. That changes two copies into four: `4×31 − 2×32 = 60` bytes of growth, even though the individual rotate got smaller. Positive growth without increased replication is at most `4×5 = 20`.

A conservative combined allowance is:

- Inner copied payload: 60 bytes.
- Up to two initial fetches and one final fetch: 15 bytes.
- Size-dependent entry code: 6 bytes.
- Inner loop termination: 6 bytes.
- Plane-loop branch widening: 3 bytes.
- Scanline-loop branch widening: 4 bytes.

Total additional bound: 94 bytes, giving 546 bytes from the original 452-byte bound. `MAX_BLT_SIZE = 600` leaves another 54 bytes. Allocation, stack probing and release all use the same symbol. A 500-byte buffer does not follow from this proof and must not be substituted.

## Build and real-mode policy

- Retain the original EGA physical backend, cursor/exclusion support, palette, DIB and screen-save modules.
- Omit the original 386-only protected text modules. Preserve ordinals 400/401 with 8086 far tail jumps to the real-mode equivalents, and explicitly reject protected-mode physical enablement.
- Correct two mismatched external declarations: the definitions of `LineSeg_check_stack` and `rCode_check_stack` are NEAR, so callers declare them NEAR.
- Use the linker's default DOS stub rather than an unavailable WINSTUB.EXE. No Windows driver code depends on that stub.
- Build CONFIG, FONTS and COLORTAB from their original resource assembler sources. The Python resource packer assembles the 74 resource records and validates their roundtrip while preserving linked code and fixups.

The linker reports the expected DISPLAY/output-filename difference and two frame-relative-fixup warnings for the added far text aliases. All target addresses are resolved, and the complete OMF/MAP closure passes. These are warnings, not missing objects or unresolved imports.
