# Copyright (c) 2017 Mycroft AI Inc.
from typing import *

import numpy as np

from precise.params import pr
from precise.util import load_audio

inhibit_t = 0.4
inhibit_dist_t = 1.0
inhibit_hop_t = 0.1


def vectorize_raw(audio: np.ndarray) -> np.ndarray:
    """Turns audio into feature vectors, without clipping for length"""
    from speechpy.feature import mfcc
    return mfcc(audio, pr.sample_rate, pr.window_t, pr.hop_t, pr.n_mfcc, pr.n_filt, pr.n_fft)


def vectorize(audio: np.ndarray) -> np.ndarray:
    """
    Args:
        audio: Audio verified to be of `sample_rate`

    Returns:
        array<float>: Vector representation of audio
    """
    if len(audio) > pr.max_samples:
        audio = audio[-pr.max_samples:]
    features = vectorize_raw(audio)
    if len(features) < pr.n_features:
        features = np.concatenate(
            [np.zeros((pr.n_features - len(features), len(features[0]))), features])
    if len(features) > pr.n_features:
        features = features[-pr.n_features:]

    return features


def vectorize_inhibit(audio: np.ndarray) -> np.ndarray:
    """
    Returns an array of inputs generated from the
    keyword audio that shouldn't cause an activation
    """

    def samp(x):
        return int(pr.sample_rate * x)

    inputs = []
    for offset in range(samp(inhibit_t), samp(inhibit_dist_t), samp(inhibit_hop_t)):
        if len(audio) - offset < samp(pr.buffer_t / 2.):
            break
        inputs.append(vectorize(audio[:-offset]))
    return np.array(inputs) if inputs else np.empty((0, pr.n_features, pr.feature_size))


def load_vector(name: str, vectorizer: Callable = vectorize) -> np.ndarray:
    """Loads and caches a vector input from a wav or npy file"""
    import os

    save_name = name if name.endswith('.npy') else os.path.join('.cache', str(abs(hash(pr))),
                                                                vectorizer.__name__ + '.' + name + '.npy')

    if os.path.isfile(save_name):
        return np.load(save_name)

    print('Loading ' + name + '...')
    os.makedirs(os.path.dirname(save_name), exist_ok=True)

    vec = vectorizer(load_audio(name))
    np.save(save_name, vec)
    return vec
