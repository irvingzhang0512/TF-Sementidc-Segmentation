import collections
import tensorflow as tf
from ..backends import xception_deeplab, resnet50

BackendDescriptor = collections.namedtuple(
    'DatasetDescriptor',
    [
        'input_size',
        'downsample_stride',
        'preprocess_fn'
    ])


_MEAN_BGR = [103.939, 116.779, 123.68]


def _preprocess_caffe(inputs, dtype=tf.float32):
    """convert RGB to BGR and subject means"""
    mean_bgr = tf.reshape(_MEAN_BGR, [1, 1, 1, 3])
    inputs = tf.reverse(inputs, axis=[-1])
    return tf.cast(tf.cast(inputs, tf.float32) - mean_bgr,
                   dtype=dtype)


def _preprocess_tf(inputs, dtype=tf.float32):
    """Map image values from [0, 255] to [-1, 1]."""
    preprocessed_inputs = (1.0 / 127.5) * tf.cast(inputs, tf.float32) - 1.0
    return tf.cast(preprocessed_inputs, dtype=dtype)


def _preprocess_torch(inputs, dtype=tf.float32):
    inputs = tf.cast(inputs, tf.float32) / 255.
    mean_rgb = tf.reshape([0.485, 0.456, 0.406], [1, 1, 1, 3])
    std_rgb = tf.reshape([0.229, 0.224, 0.225], [1, 1, 1, 3])
    inputs = (inputs - mean_rgb) / std_rgb
    return inputs


def _preporcess_zero_to_one(inputs, dtype=tf.float32):
    return tf.cast(tf.cast(inputs, tf.float32)/255., tf.float32)


XCEPTION = 'xception'
_XCEPTION_INFORMATION = BackendDescriptor(
    input_size=(299, 299, 3),
    downsample_stride=32,
    preprocess_fn=_preporcess_zero_to_one,
)


RESNET50 = 'resnet50'
_RESNET50_INFORMATION = BackendDescriptor(
    input_size=(224, 224, 3),
    downsample_stride=32,
    preprocess_fn=_preprocess_caffe,
)


BACKEND_INFORMATION = {
    XCEPTION: _XCEPTION_INFORMATION,
    RESNET50: _RESNET50_INFORMATION,
}


def build_preprocess_fn(backend_type):
    if backend_type in BACKEND_INFORMATION:
        return BACKEND_INFORMATION[backend_type].preprocess_fn
    raise ValueError('unknown backend type {}'.format(backend_type))


def build_backend(backend_type,
                  input_shape=(513, 513, 3),
                  input_tensor=None,
                  OS=16,
                  fine_tune_batch_norm=False,):
    if backend_type == XCEPTION:
        return xception_deeplab.Xception(
            input_shape=input_shape,
            OS=OS,
        )
    elif backend_type == RESNET50:
        return resnet50.ResNet50(
            input_shape=input_shape,
        )
    raise ValueError('unknown backend type {}'.format(backend_type))
