# CAD Standardization Analysis Report

## Overview
- **Total Files Processed:** 17

### Categories Identified
- **Abutment_Reinforcement:** 2 files
- **GAD:** 6 files
- **Deck Slab:** 2 files
- **Pier_Reinforcement:** 4 files
- **Unknown:** 1 files
- **Bearing:** 2 files

## Component Patterns

### Abutment_Reinforcement
#### Most Common Layers
- `0` (2 occurrences)
- `TEXT` (2 occurrences)
- `DEFPOINTS` (2 occurrences)
- `DIM` (2 occurrences)
- `STRUCTURE` (2 occurrences)
- `Ttile_Sheet` (2 occurrences)
- `WALL` (2 occurrences)
- `ASHADE` (1 occurrences)
- `PLAN` (1 occurrences)
- `TITLE` (1 occurrences)

#### Most Common Blocks
- `_ArchTick` (2 occurrences)
- `VDDIM_DEFAULT` (2 occurrences)
- `VDDIM_NONE` (2 occurrences)
- `_OBLIQUE` (1 occurrences)
- `AVE_RENDER` (1 occurrences)
- `AVE_GLOBAL` (1 occurrences)
- `50` (1 occurrences)
- `ANONYM_X3` (1 occurrences)
- `TIT` (1 occurrences)
- `ORG` (1 occurrences)

### GAD
#### Most Common Layers
- `0` (6 occurrences)
- `DEFPOINTS` (5 occurrences)
- `DIM` (5 occurrences)
- `TEXT` (5 occurrences)
- `HATCH` (5 occurrences)
- `STRUCTURE` (4 occurrences)
- `P` (4 occurrences)
- `ASHADE` (4 occurrences)
- `TT2` (4 occurrences)
- `BORDER` (4 occurrences)

#### Most Common Blocks
- `VDDIM_DEFAULT` (6 occurrences)
- `VDDIM_NONE` (6 occurrences)
- `AVE_RENDER` (5 occurrences)
- `AVE_GLOBAL` (5 occurrences)
- `1` (4 occurrences)
- `R` (1 occurrences)
- `XXX` (1 occurrences)
- `VDCLIP_6_1_04d46eaa-1526-4b02-8f36-cec2df0442b5` (1 occurrences)
- `ANONYM_X53` (1 occurrences)
- `ANONYM_X60` (1 occurrences)

### Deck Slab
#### Most Common Layers
- `0` (2 occurrences)
- `DEFPOINTS` (2 occurrences)
- `DIM` (2 occurrences)
- `HATCH` (2 occurrences)
- `TEXT` (2 occurrences)
- `Ttile_Sheet` (2 occurrences)
- `WALL` (2 occurrences)
- `REINFORCEMENT` (2 occurrences)
- `1CON` (1 occurrences)
- `6CON` (1 occurrences)

#### Most Common Blocks
- `VDDIM_DEFAULT` (2 occurrences)
- `VDDIM_NONE` (2 occurrences)
- `_Oblique` (1 occurrences)
- `ANONYM_X0` (1 occurrences)
- `ANONYM_X1` (1 occurrences)
- `ANONYM_X2` (1 occurrences)
- `ANONYM_X3` (1 occurrences)
- `ANONYM_X4` (1 occurrences)
- `ANONYM_X5` (1 occurrences)
- `ANONYM_X6` (1 occurrences)

### Pier_Reinforcement
#### Most Common Layers
- `0` (4 occurrences)
- `Defpoints` (4 occurrences)
- `st-txt` (3 occurrences)
- `st-dim` (3 occurrences)
- `st-rf` (3 occurrences)
- `G-25CO` (3 occurrences)
- `FV_G_1001-A2_T$0$G-25CO` (3 occurrences)
- `FV_G_1001-A2_T$0$GSRDC-LOGO` (3 occurrences)
- `FV_G_1001-A2_T$0$GSRDC LOGO` (3 occurrences)
- `FV_G_1001-A2_T$0$TIT` (3 occurrences)

#### Most Common Blocks
- `_Origin` (3 occurrences)
- `1` (3 occurrences)
- `FV_G_1001-A2_T` (3 occurrences)
- `FV_G_1001-A2_T$0$A$C71345202` (3 occurrences)
- `FV_G_1001-A2_T$0$L & T logo` (3 occurrences)
- `VDDIM_DEFAULT` (3 occurrences)
- `VDDIM_NONE` (3 occurrences)
- `_Oblique` (2 occurrences)
- `ST-DOT-40` (2 occurrences)
- `793EE` (2 occurrences)

### Unknown
#### Most Common Layers
- `Beam` (1 occurrences)
- `Plate` (1 occurrences)
- `Solid` (1 occurrences)
- `BeamNo` (1 occurrences)
- `PlateNo` (1 occurrences)
- `SolidNo` (1 occurrences)
- `NodeNo` (1 occurrences)
- `PropertyName` (1 occurrences)
- `0` (1 occurrences)
- `Defpoints` (1 occurrences)

### Bearing
#### Most Common Layers
- `0` (2 occurrences)
- `TEXT` (2 occurrences)
- `DIMENSION` (2 occurrences)
- `DEFPOINTS` (2 occurrences)
- `DIM` (2 occurrences)
- `Ttile_Sheet` (2 occurrences)
- `CENTER` (2 occurrences)
- `HATCH` (2 occurrences)
- `STR` (2 occurrences)
- `REINF.` (2 occurrences)

#### Most Common Blocks
- `_OBLIQUE` (2 occurrences)
- `G1` (2 occurrences)
- `R12` (2 occurrences)
- `VDDIM_DEFAULT` (2 occurrences)
- `VDDIM_NONE` (2 occurrences)

## Recommendations for Standardization
1. **Layer Standardization:** Adopt the most common layers found across components as the unified standard.
2. **Block Parameterization:** Convert the frequently occurring static blocks into dynamic blocks with parametric properties.
3. **Template Assembly:** Use the identified layer structures to generate strict drawing templates for each component type.
