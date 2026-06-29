# 3D Model Reconstruction Evaluation Methods

Author: Zitong Li

This repository collects Python methods for evaluating the geometric quality of 3D model reconstruction results.

It is designed for comparing two model files:

- Model A: the baseline or reference model
- Model B: the generated 3D model to be evaluated

The repository currently includes Chamfer Distance and Hausdorff Distance. More reconstruction evaluation metrics can be added later as separate scripts and requirement files.

## Current Methods

| Method | Script | What It Measures | Best For |
|---|---|---|---|
| Chamfer Distance | `chamfer_distance_3d.py` | Average nearest-neighbor geometric difference between two sampled model surfaces. | Overall shape similarity and general reconstruction error. |
| Hausdorff Distance | `hausdorff_distance_3d.py` | Maximum nearest-neighbor geometric error between two sampled model surfaces. | Strict local failure detection, missing parts, extra geometry, outliers, and worst-case deviation. |

## General Workflow

Each method follows the same basic workflow:

1. Load two 3D model files.
2. Sample points from each mesh surface.
3. Optionally normalize the two sampled point clouds.
4. Compute the selected evaluation metric.
5. Report the distance from A to B, from B to A, and the final bidirectional score.

Lower distance values usually mean the generated model is closer to the reference model.

## Chamfer Distance

Chamfer Distance measures the average nearest-neighbor distance between two point clouds sampled from the model surfaces.

If A is the reference model and B is the generated model:

- A to B: how far reference-model surface points are from the generated model. A high value may indicate missing geometry in B.
- B to A: how far generated-model surface points are from the reference model. A high value may indicate extra structures, noisy surfaces, or incorrect protrusions in B.
- Total: the sum of A to B and B to A.

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python chamfer_distance_3d.py reference_model.obj generated_model.obj
```

Optional:

```bash
python chamfer_distance_3d.py reference_model.obj generated_model.obj \
  --num-points 20000 \
  --no-normalize \
  --not-squared
```

Example output:

```text
Chamfer Distance
----------------
A to B: 0.00123456
B to A: 0.00198765
Total:  0.00322221
```

## Hausdorff Distance

Hausdorff Distance measures the worst nearest-neighbor distance between two point clouds sampled from the model surfaces.

It is stricter than Chamfer Distance because it focuses on the largest local error rather than the average error. This makes it useful for identifying missing parts, unexpected extra geometry, severe local deformation, and outlier surfaces.

If A is the reference model and B is the generated model:

- A reference -> B generated: the largest reference-surface error against the generated model. A high value may indicate that B missed part of the reference shape.
- B generated -> A reference: the largest generated-surface error against the reference model. A high value may indicate hallucinated geometry, noise, or extra surfaces in B.
- Bidirectional max: the final Hausdorff Distance, computed as the larger of the two directed distances.

Install dependencies:

```bash
pip install -r requirements_hausdorff.txt
```

Run:

```bash
python hausdorff_distance_3d.py reference_model.obj generated_model.obj
```

Hausdorff Distance is sensitive to isolated noisy points. For a more robust score, use a percentile such as 95 or 99:

```bash
python hausdorff_distance_3d.py reference_model.obj generated_model.obj \
  --num-points 20000 \
  --percentile 95 \
  --seed 42
```

Example output:

```text
Hausdorff Distance
------------------
A reference -> B generated: 0.04200000
B generated -> A reference: 0.03100000
Bidirectional max:          0.04200000
```

## Alignment Notes

The scripts can normalize scale and center both sampled point clouds, but they do not perform strict rotational alignment.

If two models face different directions, the distance result may be misleading.

A more rigorous evaluation workflow is:

```text
load models -> sample surfaces -> remove background/noise -> normalize scale -> ICP alignment -> compute evaluation metric
```

For quick experiments, the current scripts are enough to understand the metric behavior. For formal evaluation, add an alignment step with a library such as Open3D.

## Supported File Types

Supported formats depend on `trimesh`, but common mesh formats include:

- `.obj`
- `.stl`
- `.ply`
- `.glb`
- `.gltf`

## Adding More Metrics

Future evaluation metrics should be added as separate files, for example:

- `normal_consistency_3d.py`
- `f_score_3d.py`
- `iou_3d.py`

Each new method should include:

- a separate Python script
- a separate requirements file when it needs method-specific dependencies
- a short README section explaining what the metric measures and how to run it
