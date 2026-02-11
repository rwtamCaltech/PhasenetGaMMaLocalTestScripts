"""Unit tests for the GaMMa base mixture model module."""

import numpy as np
import pytest

from gamma._base import _check_shape, _check_X


class TestCheckShape:
    """Tests for _check_shape validation function."""

    @pytest.mark.unit
    def test_valid_shape(self):
        """No error for correctly shaped parameter."""
        param = np.array([1.0, 2.0, 3.0])
        _check_shape(param, (3,), "test_param")  # should not raise

    @pytest.mark.unit
    def test_invalid_shape(self):
        """Should raise ValueError for mismatched shape."""
        param = np.array([1.0, 2.0])
        with pytest.raises(ValueError, match="should have the shape"):
            _check_shape(param, (3,), "test_param")

    @pytest.mark.unit
    def test_2d_shape(self):
        param = np.array([[1.0, 2.0], [3.0, 4.0]])
        _check_shape(param, (2, 2), "test_param")  # should not raise

    @pytest.mark.unit
    def test_2d_invalid(self):
        param = np.array([[1.0, 2.0], [3.0, 4.0]])
        with pytest.raises(ValueError):
            _check_shape(param, (3, 2), "test_param")

    @pytest.mark.unit
    def test_scalar(self):
        param = np.array(5.0)
        _check_shape(param, (), "test_param")  # should not raise


class TestCheckX:
    """Tests for _check_X input validation function."""

    @pytest.mark.unit
    def test_valid_input(self):
        X = np.random.randn(100, 3)
        result = _check_X(X, n_components=5)
        assert result.shape == (100, 3)

    @pytest.mark.unit
    def test_too_few_samples(self):
        """Should raise when n_samples < n_components."""
        X = np.random.randn(3, 2)
        with pytest.raises(ValueError, match="n_samples >= n_components"):
            _check_X(X, n_components=5)

    @pytest.mark.unit
    def test_wrong_features(self):
        """Should raise when features don't match expected."""
        X = np.random.randn(100, 3)
        with pytest.raises(ValueError, match="features"):
            _check_X(X, n_features=5)

    @pytest.mark.unit
    def test_converts_dtype(self):
        X = np.random.randn(10, 2).astype(np.int32)
        result = _check_X(X)
        assert result.dtype in [np.float32, np.float64]

    @pytest.mark.unit
    def test_no_constraints(self):
        X = np.random.randn(5, 2)
        result = _check_X(X)
        assert result.shape == (5, 2)
