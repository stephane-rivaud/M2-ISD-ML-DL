"""Six English protocol markdown cells pasted at the end of every ISD-1020 notebook.

This file is a jupytext percent script: copy the six ``# %% [markdown]`` cells
into each notebook source. ``PROTOCOL_CELLS`` holds the same markdown for tooling.
"""

PROTOCOL_HEADINGS: tuple[str, ...] = (
    "Problem",
    "Data",
    "Baseline",
    "Model",
    "Ablation",
    "Error analysis → Recommendation",
)

_PROBLEM = """## Problem

Answer in prose (not only code).

1. Which **business decision** should the model inform, and what is the **target**?
2. Which **metric** matches that decision, and why not accuracy alone?
3. How do you separate training and test **without leakage** (split unit, time, stratification)?
"""

_DATA = """## Data

Answer in prose (not only code).

1. What are the variables, their types, and any notable **imbalances** or volumes?
2. Which columns must you **not** use (identifiers, leakages, target sub-flags)?
3. What do you know about **quality** (missing values, outliers, drift) and temporal or business coverage?
"""

_BASELINE = """## Baseline

Answer in prose (not only code).

1. Which **naive baseline** (majority class, mean, seasonal) and what score does it get?
2. Why is this baseline the **honest floor**, and not a "deliberately weak" model?
3. Which score must you **beat** to justify a more complex model?
"""

_MODEL = """## Model

Answer in prose (not only code).

1. Which **model family** do you choose, and why (not "because it is deep")?
2. How do you train it (split, validation, hyperparameters, loss)?
3. Does the model **beat the baseline** on the chosen metric, on an uncontaminated split?
"""

_ABLATION = """## Ablation

Answer in prose (not only code).

1. What happens if you remove a family of variables, a regulariser, or a block of the network?
2. Which choice (features, architecture, horizon, threshold) **actually changes** the score?
3. Does the gain justify the extra **complexity** relative to the baseline?
"""

_ERRORS_RECO = """## Error analysis → Recommendation

Answer in prose (not only code).

1. Where does the model go wrong (**segments**, error types, horizon)?
2. Are these errors **costly** for the business, and what would you change in the data or the model?
3. What concrete **recommendation**: deploy, do not deploy, stay on the baseline, or collect this specific data?
"""

PROTOCOL_CELLS: tuple[str, ...] = (
    _PROBLEM,
    _DATA,
    _BASELINE,
    _MODEL,
    _ABLATION,
    _ERRORS_RECO,
)

# %% [markdown]
# ## Problem
#
# Answer in prose (not only code).
#
# 1. Which **business decision** should the model inform, and what is the **target**?
# 2. Which **metric** matches that decision, and why not accuracy alone?
# 3. How do you separate training and test **without leakage** (split unit, time, stratification)?

# %% [markdown]
# ## Data
#
# Answer in prose (not only code).
#
# 1. What are the variables, their types, and any notable **imbalances** or volumes?
# 2. Which columns must you **not** use (identifiers, leakages, target sub-flags)?
# 3. What do you know about **quality** (missing values, outliers, drift) and temporal or business coverage?

# %% [markdown]
# ## Baseline
#
# Answer in prose (not only code).
#
# 1. Which **naive baseline** (majority class, mean, seasonal) and what score does it get?
# 2. Why is this baseline the **honest floor**, and not a "deliberately weak" model?
# 3. Which score must you **beat** to justify a more complex model?

# %% [markdown]
# ## Model
#
# Answer in prose (not only code).
#
# 1. Which **model family** do you choose, and why (not "because it is deep")?
# 2. How do you train it (split, validation, hyperparameters, loss)?
# 3. Does the model **beat the baseline** on the chosen metric, on an uncontaminated split?

# %% [markdown]
# ## Ablation
#
# Answer in prose (not only code).
#
# 1. What happens if you remove a family of variables, a regulariser, or a block of the network?
# 2. Which choice (features, architecture, horizon, threshold) **actually changes** the score?
# 3. Does the gain justify the extra **complexity** relative to the baseline?

# %% [markdown]
# ## Error analysis → Recommendation
#
# Answer in prose (not only code).
#
# 1. Where does the model go wrong (**segments**, error types, horizon)?
# 2. Are these errors **costly** for the business, and what would you change in the data or the model?
# 3. What concrete **recommendation**: deploy, do not deploy, stay on the baseline, or collect this specific data?
