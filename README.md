# 3D Model Reconstruction Evaluation with Chamfer Distance

Author: Zitong Li

This project provides a simple Python script for evaluating the geometric difference between two 3D models using bidirectional Chamfer distance.

It is designed for comparing outputs such as:

- a traditional photogrammetry / RealityCapture reconstruction model
- an AI-generated 3D model from image-to-3D tools

## What It Does

The script:

1. Loads two 3D mesh files.
2. Samples point clouds from their mesh surfaces.
3. Optionally normalizes the two point clouds to a similar scale.
4. Computes bidirectional Chamfer distance.
5. Reports:
   - A to B distance
   - B to A distance
   - Total Chamfer distance

## Result Interpretation

If model A is the RealityCapture model and model B is the AI-generated model:

| Metric | Meaning |
|---|---|
| A to B | Average nearest-neighbor distance from RealityCapture points to AI model points. A large value may indicate that the AI model is missing real structures. |
| B to A | Average nearest-neighbor distance from AI model points to RealityCapture points. A large value may indicate that the AI model generated extra structures, noisy surfaces, or incorrect protrusions. |
| Total | Overall bidirectional geometric difference between the two models. Lower is generally better. |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python chamfer_distance_3d.py realitycapture_model.obj ai_model.obj
```

Optional arguments:

```bash
python chamfer_distance_3d.py realitycapture_model.obj ai_model.obj \
  --num-points 20000 \
  --no-normalize \
  --not-squared
```

## Important Note About Alignment

This script can normalize scale and center both point clouds, but it does not perform strict rotational alignment.

If two models face different directions, for example one faces left and the other faces right, the Chamfer distance result may be misleading.

A more rigorous workflow is:

```text
load models -> sample surfaces -> remove background/noise -> normalize scale -> ICP alignment -> compute Chamfer distance
```

For a first experiment, this script is enough to understand the idea. For a more formal evaluation, add ICP alignment with a library such as Open3D.

## Supported File Types

Supported formats depend on `trimesh`, but common mesh formats include:

- `.obj`
- `.stl`
- `.ply`
- `.glb`
- `.gltf`

## Example Output

```text
Chamfer Distance
----------------
A to B: 0.00123456
B to A: 0.00198765
Total:  0.00322221
```

