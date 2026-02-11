"""Shared fixtures and path setup for all tests."""

import os
import sys

import numpy as np
import pytest

# Add source directories to sys.path so tests can import modules
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASENET_DIR = os.path.join(PROJECT_ROOT, "LatestPhasenetLocalTest", "phasenet")
GAMMA_DIR = os.path.join(PROJECT_ROOT, "GaMMaTest")

for path in [PHASENET_DIR, GAMMA_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)


@pytest.fixture
def project_root():
    return PROJECT_ROOT


@pytest.fixture
def phasenet_dir():
    return PHASENET_DIR


@pytest.fixture
def gamma_dir():
    return GAMMA_DIR


@pytest.fixture
def sample_waveform_3c():
    """A synthetic 3-component seismic waveform (nt=3000, nsta=1, nch=3)."""
    np.random.seed(42)
    nt, nsta, nch = 3000, 1, 3
    data = np.random.randn(nt, nsta, nch).astype(np.float32)
    # Add a synthetic P-wave arrival at sample 500
    for ch in range(nch):
        data[500:520, 0, ch] += 5.0 * np.sin(np.linspace(0, 4 * np.pi, 20))
    # Add a synthetic S-wave arrival at sample 1200
    for ch in range(nch):
        data[1200:1240, 0, ch] += 8.0 * np.sin(np.linspace(0, 6 * np.pi, 40))
    return data


@pytest.fixture
def sample_predictions():
    """Synthetic model predictions with clear P and S peaks.

    Shape: (Nb=1, Nt=3000, Ns=1, Nc=3) where channels are [noise, P, S].
    """
    np.random.seed(42)
    Nb, Nt, Ns, Nc = 1, 3000, 1, 3
    preds = np.zeros((Nb, Nt, Ns, Nc), dtype=np.float32)
    # Noise channel is generally high
    preds[:, :, :, 0] = 0.9

    # P-wave peak at index 500
    p_signal = np.exp(-0.5 * ((np.arange(Nt) - 500) / 5) ** 2)
    preds[0, :, 0, 1] = p_signal
    preds[0, :, 0, 0] -= p_signal

    # S-wave peak at index 1200
    s_signal = np.exp(-0.5 * ((np.arange(Nt) - 1200) / 5) ** 2)
    preds[0, :, 0, 2] = s_signal
    preds[0, :, 0, 0] -= s_signal

    # Clamp noise channel
    preds[:, :, :, 0] = np.clip(preds[:, :, :, 0], 0, 1)
    return preds
