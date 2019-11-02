# Griffin-Lim implementation by candlewill 
# Audio -> Spectrogram / Spectrogram -> Audio conversion
# https://github.com/candlewill/Griffin_lim

import librosa
import librosa.filters
import numpy as np
from scipy import signal
import soundfile as sf

from utils.hparams import hparams

def load_wav(path, sr):
    return librosa.core.load(path, sr=sr)[0]

def save_wav(wav, path):
    sf.write(path, wav, hparams.sample_rate, subtype='PCM_16')

def spectrogram(y):
    D = _stft(_preemphasis(y))
    S = _amp_to_db(np.abs(D)) - hparams.ref_level_db
    return _normalize(S)


def inv_spectrogram(spectrogram):
    S = _db_to_amp(_denormalize(spectrogram) + hparams.ref_level_db)  # Convert back to linear
    return _inv_preemphasis(_griffin_lim(S ** 1.5))  # Reconstruct phase


def melspectrogram(y):
    D = _stft(_preemphasis(y))
    S = _amp_to_db(_linear_to_mel(np.abs(D)))
    return _normalize(S)


def inv_melspectrogram(melspectrogram):
    S = _mel_to_linear(_db_to_amp(_denormalize(melspectrogram)))  # Convert back to linear
    return _inv_preemphasis(_griffin_lim(S ** 1.5))  # Reconstruct phase


# Based on https://github.com/librosa/librosa/issues/434
def _griffin_lim(S):
    angles = np.exp(2j * np.pi * np.random.rand(*S.shape))
    S_complex = np.abs(S).astype(np.complex)
    for i in range(hparams.griffin_lim_iters):
        if i > 0:
            angles = np.exp(1j * np.angle(_stft(y)))
        y = _istft(S_complex * angles)
    return y


def _stft(y):
    n_fft = (hparams.num_freq - 1) * 2
    hop_length = int(hparams.frame_shift_ms / 1000. * hparams.sample_rate)
    win_length = int(hparams.frame_length_ms / 1000. * hparams.sample_rate)
    return librosa.stft(y=y, n_fft=n_fft, hop_length=hop_length, win_length=win_length)


def _istft(y):
    hop_length = int(hparams.frame_shift_ms / 1000. * hparams.sample_rate)
    win_length = int(hparams.frame_length_ms / 1000. * hparams.sample_rate)
    return librosa.istft(y, hop_length=hop_length, win_length=win_length)


# Conversions:
_mel_basis = None
_inv_mel_basis = None

def _linear_to_mel(spectrogram):
    global _mel_basis
    if _mel_basis is None:
        _mel_basis = _build_mel_basis()
    return np.dot(_mel_basis, spectrogram)

def _mel_to_linear(mel_spectrogram):
    global _inv_mel_basis
    if _inv_mel_basis is None:
        _inv_mel_basis = np.linalg.pinv(_build_mel_basis())
    return np.maximum(1e-10, np.dot(_inv_mel_basis, mel_spectrogram))

def _build_mel_basis():
    n_fft = (hparams.num_freq - 1) * 2
    return librosa.filters.mel(hparams.sample_rate, n_fft, n_mels=hparams.num_mels)

def _amp_to_db(x):
    return 20 * np.log10(np.maximum(1e-5, x))

def _db_to_amp(x):
    return np.power(10.0, x * 0.05)


def _preemphasis(x):
    return signal.lfilter([1, -hparams.preemphasis], [1], x)


def _inv_preemphasis(x):
    return signal.lfilter([1], [1, -hparams.preemphasis], x)

def _normalize(S):
    return np.clip((S - hparams.min_level_db) / -float(hparams.min_level_db), 0, 1)

def _denormalize(S):
    return (np.clip(S, 0, 1) * -hparams.min_level_db) + hparams.min_level_db
