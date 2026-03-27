"""Unit tests for util.py (EMA, LMA, metrics, clean_queue)."""

import numpy as np
import pytest

from util import EMA, LMA, metrics, clean_queue, clean_queue_thread


class TestEMA:
    """Tests for the Exponential Moving Average class."""

    @pytest.mark.unit
    def test_first_value(self):
        """First call should return the input value itself."""
        ema = EMA(alpha=0.9)
        result = ema(5.0)
        assert result == 5.0

    @pytest.mark.unit
    def test_smoothing(self):
        """EMA should smooth values towards the running average."""
        ema = EMA(alpha=0.9)
        ema(10.0)
        result = ema(20.0)
        # result = 0.9 * 10 + 0.1 * 20 = 11.0
        assert np.isclose(result, 11.0)

    @pytest.mark.unit
    def test_high_alpha_slow_change(self):
        """High alpha means slow response to new values."""
        ema = EMA(alpha=0.99)
        ema(0.0)
        for _ in range(100):
            val = ema(1.0)
        # After 100 iterations, should be close to but not quite 1.0
        assert val < 1.0
        assert val > 0.5

    @pytest.mark.unit
    def test_zero_alpha_instant_change(self):
        """Alpha=0 means the EMA always equals the latest value."""
        ema = EMA(alpha=0.0)
        ema(10.0)
        result = ema(20.0)
        assert result == 20.0

    @pytest.mark.unit
    def test_value_property(self):
        ema = EMA(alpha=0.5)
        ema(10.0)
        assert ema.value == 10.0


class TestLMA:
    """Tests for the Linear Moving Average class."""

    @pytest.mark.unit
    def test_first_value(self):
        lma = LMA()
        result = lma(5.0)
        assert result == 5.0

    @pytest.mark.unit
    def test_running_mean(self):
        """LMA should compute the running mean."""
        lma = LMA()
        lma(2.0)
        result = lma(4.0)
        # Mean of [2, 4] = 3
        assert np.isclose(result, 3.0)

    @pytest.mark.unit
    def test_multiple_values(self):
        lma = LMA()
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        for v in values:
            result = lma(v)
        assert np.isclose(result, 3.0)  # mean of 1..5

    @pytest.mark.unit
    def test_value_property(self):
        lma = LMA()
        lma(10.0)
        assert lma.value == 10.0


class TestMetrics:
    """Tests for the metrics function."""

    @pytest.mark.unit
    def test_perfect_score(self):
        precision, recall, f1 = metrics(10, 10, 10)
        assert precision == 1.0
        assert recall == 1.0
        assert f1 == 1.0

    @pytest.mark.unit
    def test_low_precision(self):
        precision, recall, f1 = metrics(2, 10, 2)
        assert precision == 0.2
        assert recall == 1.0

    @pytest.mark.unit
    def test_low_recall(self):
        precision, recall, f1 = metrics(2, 2, 10)
        assert precision == 1.0
        assert recall == 0.2

    @pytest.mark.unit
    def test_f1_harmonic_mean(self):
        p, r, f1 = metrics(3, 5, 8)
        expected_f1 = 2 * (3 / 5) * (3 / 8) / ((3 / 5) + (3 / 8))
        assert np.isclose(f1, expected_f1)


class TestCleanQueue:
    """Tests for the clean_queue and clean_queue_thread functions."""

    @pytest.mark.unit
    def test_removes_zeros(self):
        picks = [[0, 1, 0, 2, 0], [3, 0, 4]]
        result = clean_queue(picks)
        assert result == [[1, 2], [3, 4]]

    @pytest.mark.unit
    def test_all_zeros(self):
        picks = [[0, 0, 0]]
        result = clean_queue(picks)
        assert result == [[]]

    @pytest.mark.unit
    def test_no_zeros(self):
        picks = [[1, 2, 3]]
        result = clean_queue(picks)
        assert result == [[1, 2, 3]]

    @pytest.mark.unit
    def test_empty_list(self):
        picks = [[]]
        result = clean_queue(picks)
        assert result == [[]]

    @pytest.mark.unit
    def test_clean_queue_thread(self):
        result = clean_queue_thread([0, 5, 0, 10, 0])
        assert result == [5, 10]

    @pytest.mark.unit
    def test_clean_queue_thread_empty(self):
        result = clean_queue_thread([0, 0, 0])
        assert result == []
