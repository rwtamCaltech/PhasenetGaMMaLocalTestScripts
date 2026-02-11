"""Unit tests for data_reader.py normalization functions and DataConfig."""

import sys
import types
from unittest import mock

import numpy as np
import pytest

# Mock tensorflow and its submodules so data_reader can be imported without TF installed.
# The functions under test (normalize, normalize_long, normalize_batch, DataConfig)
# do not use TensorFlow at all — it's only imported at module level.
_tf_mock = types.ModuleType("tensorflow")
_tf_compat = types.ModuleType("tensorflow.compat")
_tf_compat_v1 = types.ModuleType("tensorflow.compat.v1")
_tf_compat_v1.disable_eager_execution = lambda: None
_tf_compat_v1.logging = types.SimpleNamespace(set_verbosity=lambda *a: None, ERROR=0)
_tf_mock.compat = _tf_compat
_tf_mock.compat.v1 = _tf_compat_v1
_tf_mock.nest = types.SimpleNamespace(flatten=lambda x: x, pack_sequence_as=lambda t, v: v)
_tf_mock.data = types.SimpleNamespace(Dataset=type("Dataset", (), {"range": classmethod(lambda cls, n: None)}))
_tf_mock.numpy_function = lambda *a, **kw: None

for mod_name in ["tensorflow", "tensorflow.compat", "tensorflow.compat.v1"]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = {"tensorflow": _tf_mock, "tensorflow.compat": _tf_compat, "tensorflow.compat.v1": _tf_compat_v1}[mod_name]

# Also mock h5py and obspy if not installed
for mod_name in ["h5py", "obspy"]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = mock.MagicMock()

from data_reader import normalize, normalize_long, normalize_batch, DataConfig


class TestDataConfig:
    """Tests for the DataConfig class."""

    @pytest.mark.unit
    def test_default_values(self):
        config = DataConfig()
        assert config.n_channel == 3
        assert config.n_class == 3
        assert config.sampling_rate == 100
        assert config.dt == 0.01
        assert config.X_shape == [3000, 1, 3]
        assert config.Y_shape == [3000, 1, 3]

    @pytest.mark.unit
    def test_custom_values(self):
        config = DataConfig(n_channel=1, sampling_rate=200)
        assert config.n_channel == 1
        assert config.sampling_rate == 200

    @pytest.mark.unit
    def test_label_shape_default(self):
        config = DataConfig()
        assert config.label_shape == "gaussian"
        assert config.label_width == 30


class TestNormalize:
    """Tests for the normalize function."""

    @pytest.mark.unit
    def test_zero_mean(self):
        """After normalization, data should have approximately zero mean."""
        np.random.seed(42)
        data = np.random.randn(3000, 1, 3).astype(np.float32) + 5.0
        result = normalize(data.copy())
        assert np.allclose(np.mean(result, axis=0), 0, atol=1e-5)

    @pytest.mark.unit
    def test_unit_std(self):
        """After normalization, data should have approximately unit std."""
        np.random.seed(42)
        data = np.random.randn(3000, 1, 3).astype(np.float32) * 10.0
        result = normalize(data.copy())
        assert np.allclose(np.std(result, axis=0), 1, atol=0.05)

    @pytest.mark.unit
    def test_zero_data(self):
        """Zero data should not produce NaN or inf after normalization."""
        data = np.zeros((3000, 1, 3), dtype=np.float32)
        result = normalize(data.copy())
        assert not np.any(np.isnan(result))
        assert not np.any(np.isinf(result))
        assert np.allclose(result, 0)

    @pytest.mark.unit
    def test_preserves_shape(self):
        np.random.seed(42)
        data = np.random.randn(3000, 1, 3).astype(np.float32)
        result = normalize(data.copy())
        assert result.shape == data.shape

    @pytest.mark.unit
    def test_single_channel(self):
        """Should work with single-channel data."""
        np.random.seed(42)
        data = np.random.randn(3000, 1, 1).astype(np.float32)
        result = normalize(data.copy())
        assert result.shape == (3000, 1, 1)
        assert not np.any(np.isnan(result))


class TestNormalizeLong:
    """Tests for the normalize_long function (sliding window normalization)."""

    @pytest.mark.unit
    def test_output_shape(self):
        np.random.seed(42)
        data = np.random.randn(6000, 1, 3).astype(np.float32)
        result = normalize_long(data.copy())
        assert result.shape == data.shape

    @pytest.mark.unit
    def test_no_nan_output(self):
        np.random.seed(42)
        data = np.random.randn(6000, 1, 3).astype(np.float32)
        result = normalize_long(data.copy())
        assert not np.any(np.isnan(result))
        assert not np.any(np.isinf(result))

    @pytest.mark.unit
    def test_preserves_dtype(self):
        data = np.random.randn(3000, 1, 3).astype(np.float32)
        result = normalize_long(data.copy())
        assert result.dtype == np.float32

    @pytest.mark.unit
    def test_zero_data(self):
        """Zero data should not produce NaN or inf."""
        data = np.zeros((3000, 1, 3), dtype=np.float32)
        result = normalize_long(data.copy())
        assert not np.any(np.isnan(result))
        assert not np.any(np.isinf(result))

    @pytest.mark.unit
    def test_custom_window(self):
        np.random.seed(42)
        data = np.random.randn(3000, 1, 3).astype(np.float32)
        result = normalize_long(data.copy(), window=1500)
        assert result.shape == data.shape
        assert not np.any(np.isnan(result))


class TestNormalizeBatch:
    """Tests for the normalize_batch function."""

    @pytest.mark.unit
    def test_output_shape(self):
        np.random.seed(42)
        data = np.random.randn(4, 3000, 1, 3).astype(np.float32)
        result = normalize_batch(data.copy())
        assert result.shape == data.shape

    @pytest.mark.unit
    def test_no_nan_output(self):
        np.random.seed(42)
        data = np.random.randn(4, 3000, 1, 3).astype(np.float32)
        result = normalize_batch(data.copy())
        assert not np.any(np.isnan(result))
        assert not np.any(np.isinf(result))

    @pytest.mark.unit
    def test_zero_batch(self):
        data = np.zeros((2, 3000, 1, 3), dtype=np.float32)
        result = normalize_batch(data.copy())
        assert not np.any(np.isnan(result))
        assert not np.any(np.isinf(result))

    @pytest.mark.unit
    def test_single_station_batch(self):
        np.random.seed(42)
        data = np.random.randn(1, 3000, 1, 3).astype(np.float32)
        result = normalize_batch(data.copy())
        assert result.shape == (1, 3000, 1, 3)
