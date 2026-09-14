# ISD-1020 — Running the notebook at home

Use this page after day 0 if you want the notebook working on your own
machine (home or a company laptop). Bring a **charged laptop** and the
**charger** to the next Mondays: 21 September, 28 September and
5 October, room **PUIO B210** (building 640, Orsay). No room machine is
guaranteed.

Stéphane Rivaud, Solal Nathan and Dylan Séchet are involved in the module.

## 1. Google account (for Colab)

A **Google account** is required for Google Colab. No local Python install
is required if Colab works. A personal Gmail is enough if you do not
already have one.

If a company laptop blocks Google, Colab or Drive, pair with a classmate
or install locally (see below).

## 2. Open the notebook in Colab

1. Open the **`d0_first_contact_autonomous`** notebook from this repository
   (or the Colab badge in the README).
2. **Before any edit:** `File → Save a copy in Drive`. Work only on **your**
   copy.

On Colab, the setup cell under “Course helpers” downloads `common/` and
`data/` from this repository. In a local clone of this repository it does
nothing.

## 3. Run the first cell

Run the **first code cell**. The expected output is **one line** with the
scikit-learn and PyTorch versions, of the form:

```text
sklearn 1.x.x | torch 2.x.x
```

(the exact numbers vary; what matters is that both versions print without
error.)

Then run the setup cell and the data cell. Day 0 loads the Telco churn
table shipped in `data/telco.parquet`.

## 4. If it fails

| Situation | What to do |
|---|---|
| No Google account, or Colab refuses the connection | Use a personal Gmail account; otherwise install locally (below) or **pair** with a classmate. |
| Company laptop blocks Google / Colab / Drive | Same fallback: local install, or pair. |
| The first cell crashes (`ModuleNotFoundError`, no version line) | In Colab: `Runtime → Restart session`, rerun the cell. If it persists: `!pip install -q scikit-learn torch pandas matplotlib numpy pyarrow requests` then rerun. Locally: the same packages (see below). |

### Local install

Clone this repository. At the repository root:

```text
pip install -r requirements-colab.txt
```

Then open `sessions/d0-2026-09-14/notebooks/d0_first_contact_autonomous.ipynb`
in Jupyter.

## 5. Groups

**Groups of 3.** You may still **change group until 28 September**; the
group of that day is the one assessed on 5 October.

## 6. LLM

Using an LLM is allowed everywhere in this module: lectures, labs,
mini-project, oral exam. There is nothing to declare. Any code you hand
in counts as your own: I will assume you wrote it, and that you can
explain every line of it. At the oral exam, a line you cannot explain
costs you marks; the tool that produced it does not.

## Contact

Module lead: **Stéphane Rivaud** (MCF, LISN). For any question, write to
the track address: `master-isd@universite-paris-saclay.fr`.
