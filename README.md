# ISD-1020 — Machine Learning / Deep Learning

Master Informatique — **Informatique pour la Science des Données (ISD)**,
apprenticeship pathway · Université Paris-Saclay, Faculté des Sciences d'Orsay.
Room **PUIO B210** (building 640, Orsay).

This is the student copy of the course pack. It grows on each Monday: only
material for the weeks already taught is here.

## The four Mondays

| Day | Date | Hours | Theme |
|---|---|---|---|
| D0 | Monday 14 September 2026 | 13:30–17:00 | Kick-off and first contact (telecom churn) |
| D1 | Monday 21 September 2026 | 09:00–12:30 · 13:30–17:00 | Prediction on tabular data; from the linear model to the MLP |
| D2 | Monday 28 September 2026 | 09:00–12:30 · 13:30–17:00 | Time series: forecasting and anomaly detection |
| D3 | Monday 5 October 2026 | 09:00–12:30 · 13:30–17:00 | Supervised practical (morning) and oral defences (afternoon) |

Groups of 3. You may still change group until 28 September; the group of that
day is the one assessed on 5 October. The exact mark weighting is being
settled and will be given before 28 September.

## The six-step protocol

Every notebook and the oral defence use the same six steps:

1. **Problem**
2. **Data**
3. **Baseline**
4. **Model**
5. **Ablation**
6. **Error analysis leading to a recommendation**

The sixth step is one step: you observe where the model fails, then you derive
a recommendation. Six steps, six notebook cells, six slides at the oral exam.

## Open the notebook in Colab

Work in the **autonomous** notebook. Before any edit: **File → Save a copy in
Drive**. Work only on your copy.

1. Click the Colab badge for this week (or open the `.ipynb` on GitHub and
   use **Open in Colab**).
2. Save the copy in Drive.
3. Run the first code cell. You should see one line of the form
   `sklearn 1.x.x | torch 2.x.x`.
4. Run the setup cell under “Course helpers”. On Colab it downloads `common/`
   and `data/` from this repository. In a local clone of this repository it
   does nothing.
5. Run the data cell. Day 0 loads the Telco churn table shipped in
   `data/telco.parquet`.

If you are not on Colab, clone this repository and open the same notebook in
Jupyter. The dataset loaders still look for the course copy first.

**14 September — first contact (telecom churn)**
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/stephane-rivaud/M2-ISD-ML-DL/blob/main/sessions/d0-2026-09-14/notebooks/d0_first_contact_autonomous.ipynb)
· [slides](sessions/d0-2026-09-14/dist/slides.pdf)
· [setup check](sessions/d0-2026-09-14/setup-check.md)
**21 September — tabular data and a first MLP**
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/stephane-rivaud/M2-ISD-ML-DL/blob/main/sessions/d1-2026-09-21/am/notebooks/d1_am_tabular_sklearn_autonomous.ipynb)
morning ·
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/stephane-rivaud/M2-ISD-ML-DL/blob/main/sessions/d1-2026-09-21/pm/notebooks/d1_pm_first_mlp_pytorch_autonomous.ipynb)
afternoon
· [morning slides](sessions/d1-2026-09-21/am/dist/slides.pdf)
· [afternoon slides](sessions/d1-2026-09-21/pm/dist/slides.pdf)

## LLM use

Using an LLM is allowed everywhere in this module: lectures, labs,
mini-project, oral exam. There is nothing to declare. Any code you hand
in counts as your own: I will assume you wrote it, and that you can
explain every line of it.

At the oral exam, a line you cannot explain costs you marks; the tool that
produced it does not. Details: [`evaluation/llm-policy.md`](evaluation/llm-policy.md).
