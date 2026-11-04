# Source provenance

## Microsoft Windows 3.0 DDK

The base driver sources come from the archived Windows 3.0 DDK release media, whose files are dated June 1, 1990. The archive is preserved in the [WaREZ HouZE wbiz0095 collection](https://discmaster.textfiles.com/browse/29993/wbiz0090-0099/wbiz0095.tar/wbiz0095/WDDK3001.ZIP), backed by [Internet Archive's IBM/WGAM/WBIZ collection](https://archive.org/details/ibm-wgam-wbiz-collection). The historical discovery is described in the update to [OS/2 Museum's Windows 3.x VDDVGA article](https://www.os2museum.com/wp/windows-3-x-vddvga/).

The original archives used were:

- [WDDK3001.ZIP](https://discmaster.textfiles.com/file/29993/wbiz0090-0099/wbiz0095.tar/wbiz0095/WDDK3001.ZIP), SHA-256 `d547fac34ba551324e535253f6a1f647f20575f3570d737e0c1f85a72f8d0b03`. Contains `DISPLAY/4PLANE`, including `COLOR/EGA/EGAHIRES` and its original makefile, module-definition file, linker response, and resources.
- [WDDK3006.ZIP](https://discmaster.textfiles.com/file/29993/wbiz0090-0099/wbiz0095.tar/wbiz0095/WDDK3006.ZIP), SHA-256 `293ade55710e7d137e5a3f3062d740d27a38f567300e69469417c7ddbbbb52f6`. Supplies `INCLUDE/GDIDEFS.INC`, `INCLUDE/WINDEFS.INC`, and `LIB/C51/SWINLIBC.LIB`.
- [WDDK3008.ZIP](https://discmaster.textfiles.com/file/29993/wbiz0090-0099/wbiz0095.tar/wbiz0095/WDDK3008.ZIP), SHA-256 `d3e1ba72da1affd00d5e20d23813417936feedd0fa9f4db28e9860f63ef76ef1`. Supplies `TOOLS/LINK4.EXE` for the historical build toolchain.

Many files inside these ZIP archives retain Microsoft's SZDD compression. File hashes for expanded source and dependencies therefore differ from hashes of the stored compressed files.

The full 236-file `DISPLAY/4PLANE` source tree was compared with the [May 1, 1990 final-prerelease DDK mirror](https://github.com/neozeed/Windows_3.0_ddk_prerel_19900501/tree/f825ad33af828320de88685b8e0067b9753935a9), commit `f825ad33af828320de88685b8e0067b9753935a9`. Of these, 203 files were byte-identical. The other 33 differed only in comments. No instruction, data declaration, or build-command differences were found. This comparison does not claim that a rebuilt executable is byte-identical to Microsoft's shipped EGA.DRV.

## Microsoft Windows 3.0 SDK

The matching macros and Windows header come from the [Windows 3.0 SDK 3.5-inch 720K disk set](https://winworldpc.com/download/c1967b17-6c3b-11ec-bb7d-0200008a0da4).

- Archive: [Microsoft Windows 3.0 SDK (1990) (3.5-720k).7z](https://dl.winworldpc.com/Microsoft%20Windows%203.0%20SDK%20(1990)%20(3.5-720k).7z)
- Size: 3,637,286 bytes
- SHA-256: `1c45b60aa6e1e5f8fd75daff2ec7dddd8a0df11137cead3d4f297a8b2efb061b`
- Source image: `Include Files, Sample Source Code 1 (050-151-035).img`
- Original path: `INC/CMACROS.INC`, dated June 1, 1990; expanded size 17,114 bytes; SHA-256 `7804481d5684f336d9f6dca092827ead721d4bd014621fc026f07bac2a5dad2d`
- Original path: `INC/WINDOWS.H`, dated June 1, 1990; expanded size 108,580 bytes; SHA-256 `e198f5bf0b07543e871a33b4359b7b6ba1cb0fa3ce95fc5c0291f96447cc853b`

The SDK's `Development Tools 1 (050-151-029).img` supplies `RESTOOLS/RC.EXE`, `RCPP.EXE`, and `RCPP.ERR`. `Development Tools 2 - Debug Tools 1 (050-151-030).img` supplies `DBGTOOLS/MAPSYM.EXE`. FAT12 images were parsed read-only and SZDD files expanded before use.

The [Microsoft Windows 3.0 DDK Installation and Update Guide](https://www.pcjs.org/documents/books/mspl13/win/w3ddkins/) documents the division of build dependencies: CMACROS.INC from the SDK, and GDIDEFS.INC, WINDEFS.INC, SWINLIBC.LIB, and LINK4.EXE from the DDK.

CMACROS.INC's displayed version number alone does not establish identity. A later 3.1-lineage copy also prints version 5.20 but contains materially different protected-mode and register-support macros. This project uses the Windows 3.0 SDK file identified above.

## Prior art

[Tony814/VGAon8088](https://github.com/Tony814/VGAon8088) documents binary patches for the Windows 3.0 VGA driver. It informed the investigation of immediate-shift instructions and the original 8088's interrupted multi-prefix string-operation behavior. The present project's driver changes are made to source and assembled, rather than distributed as a patch to a stock driver binary.
