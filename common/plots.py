"""Matplotlib helpers for ISD-1020 notebooks. English axis labels and docstrings.

No seaborn. Figures are not shown at import time. A non-interactive backend is
selected only when no display is available, so Colab and Jupyter still render inline.
"""

from __future__ import annotations

import os

import matplotlib
import numpy as np
from sklearn.metrics import confusion_matrix, precision_recall_curve

try:
    from IPython import get_ipython
except ImportError:
    get_ipython = None


def _configure_backend() -> None:
    """Use Agg when headless; leave notebook/Colab backends untouched."""
    if os.environ.get("MPLBACKEND"):
        return
    if os.environ.get("COLAB_RELEASE_TAG"):
        return
    if get_ipython is not None:
        ip = get_ipython()
        if ip is not None and getattr(ip, "kernel", None) is not None:
            return
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        return
    matplotlib.use("Agg")


_configure_backend()

from matplotlib import pyplot as plt
from matplotlib.axes import Axes


def _axes(ax: Axes | None) -> Axes:
    if ax is None:
        _, ax = plt.subplots()
    return ax


def plot_confusion(y_true, y_pred, labels=None, ax: Axes | None = None) -> Axes:
    """Plot a confusion matrix (true rows, predicted columns).

    Parameters
    ----------
    y_true, y_pred
        Ground-truth and predicted labels.
    labels
        Optional label order. Defaults to the sorted union of both arrays.
    ax
        Existing axes, or a new figure if omitted.

    Returns
    -------
    matplotlib.axes.Axes
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    if labels is None:
        labels = np.unique(np.concatenate([y_true, y_pred]))
    ax = _axes(ax)
    image = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    ax.figure.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    ticks = np.arange(len(labels))
    ax.set_xticks(ticks, labels)
    ax.set_yticks(ticks, labels)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Confusion matrix")
    vmax = cm.max() if cm.size else 0
    thresh = vmax / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            color = "white" if vmax and cm[i, j] > thresh else "black"
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color=color)
    ax.set_aspect("equal")
    return ax


def plot_pr_curve(y_true, y_score, ax: Axes | None = None) -> Axes:
    """Plot a binary precision–recall curve from scores (probability of the positive class).

    Parameters
    ----------
    y_true
        Binary labels (0/1).
    y_score
        Scores or probabilities for the positive class.
    ax
        Existing axes, or a new figure if omitted.

    Returns
    -------
    matplotlib.axes.Axes
    """
    precision, recall, _ = precision_recall_curve(y_true, y_score)
    ax = _axes(ax)
    ax.plot(recall, precision, label="Precision–recall")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision–recall curve")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.05)
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)
    return ax


def plot_learning_curves(train_losses, val_losses, ax: Axes | None = None) -> Axes:
    """Plot training and validation loss against epoch (1-based).

    Parameters
    ----------
    train_losses, val_losses
        Sequences of scalar losses. Lengths may differ (e.g. early stopping).
    ax
        Existing axes, or a new figure if omitted.

    Returns
    -------
    matplotlib.axes.Axes
    """
    train_losses = np.asarray(train_losses, dtype=float)
    val_losses = np.asarray(val_losses, dtype=float)
    ax = _axes(ax)
    ax.plot(np.arange(1, len(train_losses) + 1), train_losses, label="Training")
    ax.plot(np.arange(1, len(val_losses) + 1), val_losses, label="Validation")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title("Learning curves")
    ax.legend()
    ax.grid(True, alpha=0.3)
    return ax


def plot_forecast(y_true, y_pred, horizon, ax: Axes | None = None) -> Axes:
    """Plot an observed series against a forecast and shade the last ``horizon`` steps.

    Parameters
    ----------
    y_true, y_pred
        Observed and predicted values, same length.
    horizon
        Forecast horizon in time steps, used to highlight the prediction window.
    ax
        Existing axes, or a new figure if omitted.

    Returns
    -------
    matplotlib.axes.Axes
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if y_true.shape != y_pred.shape:
        msg = "y_true and y_pred must have the same shape"
        raise ValueError(msg)
    n = len(y_true)
    horizon = int(horizon)
    t = np.arange(n)
    ax = _axes(ax)
    ax.plot(t, y_true, label="Observed")
    ax.plot(t, y_pred, label="Predicted")
    if n and horizon > 0:
        start = max(n - horizon, 0)
        ax.axvspan(start, n - 1, alpha=0.15, color="#004E7D", label=f"Horizon = {horizon}")
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.set_title("Forecast")
    ax.legend()
    ax.grid(True, alpha=0.3)
    return ax
