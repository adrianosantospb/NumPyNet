# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import UpSampling2D
import tensorflow.keras.backend as K

from NumPyNet.layers.upsample_layer import Upsample_layer

import numpy as np
import pytest
from hypothesis import strategies as st
from hypothesis import given
from hypothesis import settings

from random import choice

__author__ = ['Mattia Ceccarelli', 'Nico Curti']
__email__ = ['mattia.ceccarelli3@studio.unibo.it', 'nico.curti2@unibo.it']

class TestUpsampleLayer:
  '''
  Tests:
    - costructor of UpSample_layer object
    - print function
    - forward function against tf.keras
    - backward function against tf.keras
  '''

  @given(b = st.integers(min_value=5, max_value=15),
         w = st.integers(min_value=15, max_value=100),
         h = st.integers(min_value=15, max_value=100),
         c = st.integers(min_value=1, max_value=10),
         stride=st.integers(min_value=-5, max_value=5),
         scales=st.floats(min_value=0, max_value=100, width=32))
  @settings(max_examples=100, deadline=None)
  def test_constructor(self, b, w, h, c, stride, scales):

    shape_choices  = [(b,w,h,c), None]
    stride_choices = [(stride, stride), (stride, -stride), stride]

    input_shape = choice(shape_choices)
    stride = choice(stride_choices)

    if hasattr(stride, '__iter__'):

      if stride[0] + stride[1]:

        layer = Upsample_layer(input_shape=input_shape, stride=stride, scales=scales)

        assert layer.input_shape == input_shape
        assert layer.stride == stride
        assert layer.scales == scales
        assert layer.reversed == np.sign(stride[0] + stride[1]) - 1

      else:

        with pytest.raises(NotImplementedError):
          layer = Upsample_layer(input_shape=input_shape, stride=stride, scales=scales)

    else :

      layer = Upsample_layer(input_shape=input_shape, stride=stride, scales=scales)

      assert layer.input_shape == input_shape
      assert layer.stride == stride
      assert layer.scales == scales
      assert layer.reversed == np.sign(stride) - 1


  @given(b = st.integers(min_value=5, max_value=15),
         w = st.integers(min_value=15, max_value=100),
         h = st.integers(min_value=15, max_value=100),
         c = st.integers(min_value=1, max_value=10),
         stride=st.integers(min_value=1, max_value=10),
         scales=st.floats(min_value=0, max_value=100, width=32))
  @settings(max_examples=20, deadline=None)
  def test_printer(self, b, w, h, c, stride, scales):

    layer = Upsample_layer(input_shape=(b, w ,h, c), stride=stride, scale=scales)

    print(layer)

    layer = Upsample_layer(input_shape=None, stride=stride, scales=scales)

    with pytest.raises(TypeError):
      print(layer)


  @given(b = st.integers(min_value=5, max_value=15),
         w = st.integers(min_value=15, max_value=100),
         h = st.integers(min_value=15, max_value=100),
         c = st.integers(min_value=1, max_value=10),
         stride=st.integers(min_value=1, max_value=10))
  @settings(max_examples=20, deadline=None)
  def test_forward(self, b, w, h, c, stride):

    scales = 1. # no scale factor for UpSampling2D

    inpt = np.random.uniform(low=0., high=1., size=(b, w, h, c))

    # NumPyNet model
    layer = Upsample_layer(input_shape=inpt.shape, stride=stride, scale=scales)

    # Keras Model
    inp   = Input(batch_shape=(b, w, h, c))
    x     = UpSampling2D(size=(stride, stride), data_format='channels_last', interpolation='nearest')(inp)
    model = Model(inputs=[inp], outputs=x)

    # FORWARD

    # Keras Forward
    forward_out_keras = model.predict(inpt)

    # numpynet forwrd
    layer.forward(inpt)
    forward_out_numpynet = layer.output

    # Forward check (Shape and Values)
    assert forward_out_keras.shape == forward_out_numpynet.shape
    assert np.allclose(forward_out_keras, forward_out_numpynet)


  @given(b = st.integers(min_value=5, max_value=15),
         w = st.integers(min_value=15, max_value=100),
         h = st.integers(min_value=15, max_value=100),
         c = st.integers(min_value=1, max_value=10),
         stride=st.integers(min_value=1, max_value=10))
  @settings(max_examples=20, deadline=None)
  def test_backward(self, b, w, h, c, stride):

    scales = 1.

    inpt = np.random.uniform(low=0., high=1., size=(b, w, h, c))

    # NumPyNet model
    layer = Upsample_layer(input_shape=(b, w, h, c), stride=stride, scale=scales)

    # Keras Model
    inp = Input(batch_shape=(b, w, h, c))
    x = UpSampling2D(size=(stride, stride), data_format='channels_last', interpolation='nearest')(inp)
    model = Model(inputs=[inp], outputs=x)

    # upsample-downsample
    # FORWARD

    # Keras Forward
    forward_out_keras = model.predict(inpt)

    # numpynet forwrd
    layer.forward(inpt)
    forward_out_numpynet = layer.output

    # Forward check (Shape and Values)
    assert forward_out_keras.shape == forward_out_numpynet.shape
    assert np.allclose(forward_out_keras, forward_out_numpynet)

    # BACKWARD

    layer.delta = layer.output
    delta = np.empty(shape=inpt.shape, dtype=float)
    layer.backward(delta)

    assert np.allclose(delta, inpt)

if __name__ == '__main__':

  test = TestUpsampleLayer()
  test.test_constructor()
