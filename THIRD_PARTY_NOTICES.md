# LATSES — THIRD-PARTY SOFTWARE COMPLIANCE & NOTICES

**Project:** LATSES  
**File:** `THIRD_PARTY_NOTICES.md`  
**Review date:** 2026-08-28  
**Status:** Compliance baseline; release-specific artifact verification required

> **Important:** This document is a compliance control and attribution document, not legal advice. “Legal” cannot be guaranteed by a notice file alone. Before a release bundles third-party binaries, the exact versions, binaries, dependencies, licenses, source correspondence and trademark use must be verified.

## 1. Architecture and separation

LATSES owns its Canonical Building Model, Engineering Core, GUI/application code, engineering logic and adapters. OpenFOAM, ParaView and Blender are treated as independent third-party programs.

```text
LATSES
│
├── CANONICAL BUILDING MODEL
├── ENGINEERING CORE
├── VIEW / EXPORT ADAPTERS
│      ├── 2D
│      ├── 3D
│      ├── CFD
│      └── Illustrations
│
└── EXTERNAL BACKENDS
       ├── OpenFOAM → CFD
       ├── ParaView  → scientific visualization
       └── Blender   → rendering / animation
```

The preferred boundary is a neutral-data/file and external-process boundary. LATSES must not claim ownership of upstream software.

## 2. OPENFOAM

**Role:** external CFD solver.

OpenFOAM distributed by the OpenFOAM Foundation is licensed under the GNU GPLv3. The Foundation states that distribution of compiled GPL software requires the source code to be made available.

### Redistribution controls

When LATSES bundles OpenFOAM, the release must:

- record the exact OpenFOAM version/subversion;
- retain upstream copyright and license notices;
- provide the applicable GPLv3 license text;
- provide Corresponding Source for the exact distributed binary in a GPL-compliant manner;
- record the source revision/tag corresponding to the binary;
- retain build information needed to identify/reproduce the shipped build where applicable;
- document all modifications and patches;
- identify and review third-party components distributed with the selected OpenFOAM package;
- record binary SHA-256 and source provenance.

OpenFOAM provides exact source tags for patched releases, which should be used to establish source/binary correspondence.

The OpenFOAM Foundation has publicly described enforcement cases involving removal of copyright/license notices, modified binaries without corresponding source and undisclosed modifications. LATSES therefore treats these as release-blocking compliance items.

### Trademark

`OPENFOAM®` is a registered trademark of OpenCFD Ltd licensed to the OpenFOAM Foundation. LATSES may use the name truthfully to identify the external software, but must not imply endorsement, sponsorship, certification or affiliation.

### OpenFOAM gate

```text
[ ] Exact version/subversion recorded
[ ] Official source/binary provenance recorded
[ ] SHA-256 recorded
[ ] GPLv3 text included
[ ] Copyright notices retained
[ ] Corresponding Source available
[ ] Source corresponds to shipped binary
[ ] Modifications/patches documented
[ ] Third-party dependencies reviewed
[ ] Trademark wording reviewed
[ ] Installer contents verified
```

## 3. PARAVIEW

**Role:** external scientific visualization backend.

ParaView uses the BSD 3-Clause license. Its official license requires copyright notice, license conditions and disclaimer to be reproduced for binary redistribution. It also states that additional licenses apply to parts of ParaView and its dependencies, and that SPDX files are included in binary distributions from ParaView 5.12.0 onward.

### Redistribution controls

When LATSES bundles ParaView, the release must:

- record the exact ParaView version;
- retain the Kitware copyright notice;
- include the BSD 3-Clause license and disclaimer;
- retain the third-party license/notice material supplied with the exact binary distribution;
- retain SPDX files when supplied by the distribution;
- record binary SHA-256 and official provenance;
- ensure no endorsement claim is made using Kitware or contributor names.

### ParaView gate

```text
[ ] Exact version recorded
[ ] Official provenance recorded
[ ] SHA-256 recorded
[ ] BSD 3-Clause text retained
[ ] Copyright notice retained
[ ] Disclaimer retained
[ ] Third-party licenses retained
[ ] SPDX material retained where supplied
[ ] Endorsement restriction reviewed
[ ] Installer contents verified
```

## 4. BLENDER

**Role:** external 3D rendering, animation and illustration backend.

Blender states that distribution of Blender binaries uses GNU GPL Version 3 or later. Blender also contains separately licensed components, so the license material accompanying the exact distribution must be retained.

### External-process model

The preferred LATSES integration is:

```text
LATSES BuildingModel
      ↓
neutral export
      ↓
Blender executable as independent process
      ↓
render / animation / illustration
```

Blender's official FAQ says proprietary software can remain proprietary where it operates outside Blender, uses no Blender source code or API calls, produces data for Blender, and executes Blender to operate on that data. The actual LATSES implementation must remain within that described model if LATSES relies on it.

### GPL redistribution controls

If LATSES redistributes Blender binaries, it must:

- provide the applicable GPL information;
- retain Blender copyright and credit notices;
- provide source or a GPL-compliant source-access mechanism for the exact distributed binary;
- document modifications, if any;
- preserve the license material and third-party notices supplied with the exact Blender distribution;
- avoid adding restrictions inconsistent with GPL rights.

Blender's FAQ specifically states that redistribution of official releases can provide information forwarding recipients to the official sources, while modified Blender versions require the corresponding source to be provided under GPL conditions.

### Blender Python API / add-ons

If LATSES ever distributes Python scripts that use Blender's `bpy` API, this is a separate compliance case. Blender states that published scripts using its Python API must be shared under a GPL-compliant license.

Therefore the default LATSES design should prefer external file/process integration and must not silently bundle proprietary `bpy`-dependent add-ons.

### Trademark and logo

The Blender name is a registered trademark of the Blender Foundation. Truthful textual references to unmodified Blender are permitted, but Blender's policy prohibits use that implies affiliation, sponsorship or endorsement and restricts commercial branding uses.

The Blender logo is property of the Blender Foundation. Third-party use is limited by its published guidelines; commercial product use may require permission. LATSES should therefore use a textual attribution rather than the Blender logo unless the exact proposed use has been cleared.

### Blender gate

```text
[ ] Exact version recorded
[ ] Official provenance recorded
[ ] SHA-256 recorded
[ ] GPLv3-or-later information retained
[ ] License/credits material retained
[ ] Source-access mechanism recorded
[ ] Source corresponds to shipped binary
[ ] Modifications documented
[ ] bpy/add-on status reviewed
[ ] Trademark wording reviewed
[ ] Logo use avoided or separately cleared
[ ] Installer contents verified
```

## 5. Common LATSES attribution

The LATSES About/Third-Party Software page may state:

> **LATSES uses OpenFOAM, ParaView and Blender as independent third-party software components for CFD simulation, scientific visualization, 3D rendering and engineering illustration. These projects are not developed, maintained, certified, sponsored or endorsed by LATSES. Their respective licenses, copyright notices, trademark policies and third-party notices apply.**

This short statement does not replace the complete license and notice materials required by the applicable licenses.

## 6. Installer package requirements

If third-party binaries are bundled, the installer should expose at least:

```text
LATSES/
├── LATCES.exe
├── THIRD_PARTY_NOTICES.md
├── LICENSES/
└── third_party/
    ├── openfoam/
    ├── paraview/
    └── blender/
```

Exact paths may differ. What matters is that recipients can access the required notices, license texts and applicable source-access information.

## 7. Release manifest

Every release that bundles a third-party binary must record:

```yaml
third_party:
  - name: OpenFOAM
    version: "<EXACT_VERSION>"
    license: "GPL-3.0"
    source: "<OFFICIAL_SOURCE>"
    sha256: "<SHA256>"
    source_correspondence: "<SOURCE_ACCESS>"
    modified: false

  - name: ParaView
    version: "<EXACT_VERSION>"
    license: "BSD-3-Clause"
    source: "<OFFICIAL_SOURCE>"
    sha256: "<SHA256>"
    modified: false

  - name: Blender
    version: "<EXACT_VERSION>"
    license: "GPL-3.0-or-later"
    source: "<OFFICIAL_SOURCE>"
    sha256: "<SHA256>"
    source_correspondence: "<SOURCE_ACCESS>"
    modified: false
```

The exact SPDX identifier must be confirmed from the license supplied with the exact release.

## 8. Final release gate

A LATSES installer containing these components is **NOT compliance-GREEN** until:

```text
exact version
    ↓
official provenance
    ↓
SHA-256
    ↓
license text / notices
    ↓
third-party dependency notices
    ↓
GPL source/corresponding-source procedure
    ↓
trademark/logo review
    ↓
installer inspection
    ↓
offline installation test
    ↓
COMPLIANCE GREEN
```

## 9. Important legal boundary

No separate partnership agreement is assumed merely because LATSES uses these projects under their published licenses. However, a license does not automatically answer every question about a particular combined distribution. Exact binaries, modifications, dependencies, trademarks and distribution method must be reviewed.

This document therefore deliberately does **not** claim that LATSES is “legally approved” by OpenFOAM, Kitware/ParaView or Blender Foundation. Those organizations have not granted LATSES a special endorsement or approval through this document.

For a commercial release, LATSES should obtain qualified open-source counsel's review of the final installer and source-access mechanism, especially for GPL-covered bundled binaries.

## 10. Official source material

- OpenFOAM — Free Software Licence: https://openfoam.org/licence/
- OpenFOAM — Enforcing the GPL: https://openfoam.org/licence/enforcing-gpl/
- OpenFOAM — Website Terms / trademark information: https://openfoam.org/website-terms-of-use/
- OpenFOAM — current source/release information: https://openfoam.org/download/source/
- ParaView — License: https://www.paraview.org/license/
- Blender — License: https://www.blender.org/about/license/
- Blender — FAQ: https://www.blender.org/support/faq/
- Blender — Trademark Policy: https://www.blender.org/about/trademark-policy/
- Blender — Logo: https://www.blender.org/about/logo/

---

**LATSES compliance state:** `BASELINE — RELEASE-SPECIFIC VERIFICATION REQUIRED`
