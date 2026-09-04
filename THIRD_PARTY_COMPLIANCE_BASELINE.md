# LATSES — Third-Party Compliance Baseline

## Version baseline reviewed 2026-08-28

- **OpenFOAM:** 14, patched subversion `20260724`; Windows integration is WSL/Linux, following the OpenFOAM Foundation's Windows guidance. The exact binary/source artifact and corresponding-source evidence remain release-gate items.
- **ParaView:** 6.1.1, Windows x64 MSI: `ParaView-6.1.1-Windows-Python3.12-msvc2017-AMD64.msi`; SHA-256 `9CDC653D839EBDD14903DD11A473018D722185EEF091569454170C5BAB876D6D`.
- **Blender:** 5.2.1 LTS, Windows x64 MSI: `blender-5.2.1-windows-x64.msi`; SHA-256 `bebb90fc5bf7e3ec7ab4eb34f4c5a5b54e28e582a722152a47fd4ee66ec3c6fa`.

## Release-gate requirements

### OpenFOAM / GPLv3

Before redistributing an OpenFOAM binary/package, retain GPLv3 notices, copyright information and the exact source correspondence. For patched v14, the Foundation identifies source tag `20260724` for the `20260724` package. The corresponding source for the actual shipped artifact must be retained or made available in a GPL-compliant manner. Record exact binary SHA-256, source provenance, modifications and third-party dependencies. Do not imply OpenFOAM/OpenCFD/Foundation endorsement.

### ParaView / BSD 3-Clause

For binary redistribution, retain the applicable copyright notice, BSD 3-Clause conditions and disclaimer. Preserve the third-party license/notice material and SPDX information supplied with the exact ParaView distribution. Do not use Kitware/contributor names to imply endorsement.

### Blender / GPLv3-or-later

For binary redistribution, retain the applicable GPL and Blender license/credits material and provide a GPL-compliant source-access mechanism corresponding to the shipped binary. Modified Blender requires explicit source/modification handling. Keep LATSES outside Blender's source/API boundary where relying on the independent-process model. Any distributed `bpy`-based add-on is a separate compliance case. Do not imply Blender Foundation endorsement or use Blender branding as LATSES product identity.

## Windows installer policy

The first Windows LATSES installer should bundle ParaView 6.1.1 and Blender 5.2.1 only after their exact license/third-party notice packages are captured from the actual distributions. OpenFOAM should be integrated through the supported WSL/Linux route unless a separately verified Windows deployment is established.

## Current status

`VERSION-PINNED BASELINE — RELEASE-SPECIFIC VERIFICATION REQUIRED`

Still required for compliance GREEN:

1. Capture exact OpenFOAM source/corresponding-source evidence for the WSL deployment.
2. Capture ParaView 6.1.1 third-party license/SPDX material from the exact binary package.
3. Capture Blender 5.2.1 license/credits/source-access material from the exact release.
4. Put all required notices into the LATSES installer and verify offline.
5. Record final artifact SHA-256 values in the release manifest.

## Official references

- OpenFOAM: https://openfoam.org/download/ ; https://openfoam.org/news/v14-patch/ ; https://openfoam.org/licence/
- ParaView: https://www.paraview.org/download/ ; https://www.paraview.org/license/
- Blender: https://www.blender.org/download/ ; https://www.blender.org/about/license/ ; https://www.blender.org/support/faq/ ; https://www.blender.org/about/trademark-policy/

**This document is a compliance control, not legal advice or an upstream approval.**
