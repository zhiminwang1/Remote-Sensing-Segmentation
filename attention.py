from tensorflow.keras.layers import Activation, Conv2D
import tensorflow.keras.backend as K
import tensorflow as tf
from tensorflow.keras.layers import Layer


class PAM(Layer):
    def __init__(self,filters,**kwargs):
        super(PAM, self).__init__(**kwargs)
        self.gamma_initializer =  tf.zeros_initializer()
        self.gamma_regularizer = None
        self.gamma_constraint = None
        self.filters = filters
        self.conv2b = Conv2D(filters // 8, 1, use_bias=False, kernel_initializer='he_normal')
        self.conv2c = Conv2D(filters // 8, 1, use_bias=False, kernel_initializer='he_normal')
        self.conv2d = Conv2D(filters, 1, use_bias=False, kernel_initializer='he_normal')

    
    def build(self, input_shape):
        self.gamma = self.add_weight(shape=(1, ),
                                     initializer=self.gamma_initializer,
                                     name='gamma',
                                     regularizer=self.gamma_regularizer,
                                     constraint=self.gamma_constraint)

        self.built = True

    def call(self, input):
        input_shape = input.get_shape().as_list()
        _, h, w, filters = input_shape

        
        b = self.conv2b(input)
        c = self.conv2c(input)
        d = self.conv2d(input)

        vec_b = K.reshape(b, (-1, h * w, filters // 8))
        vec_cT = tf.transpose(K.reshape(c, (-1, h * w, filters // 8)), (0, 2, 1))
        bcT = K.batch_dot(vec_b, vec_cT)
        softmax_bcT = Activation('softmax')(bcT)
        vec_d = K.reshape(d, (-1, h * w, filters))
        bcTd = K.batch_dot(softmax_bcT, vec_d)
        bcTd = K.reshape(bcTd, (-1, h, w, filters))

        out = self.gamma*bcTd + input
        return out
    
    def compute_output_shape(self, input_shape):
        return input_shape

    def get_config(self):
        config = {"filters":self.filters}
        base_config = super(PAM, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))

class CAM(Layer):
    def __init__(self,**kwargs):
        super(CAM, self).__init__(**kwargs)
        self.gamma_initializer =  tf.zeros_initializer()
        self.gamma_regularizer = None
        self.gamma_constraint = None

    def build(self, input_shape):
        self.gamma = self.add_weight(shape=(1, ),
                                     initializer=self.gamma_initializer,
                                     name='gamma',
                                     regularizer=self.gamma_regularizer,
                                     constraint=self.gamma_constraint)

        self.built = True

    def compute_output_shape(self, input_shape):
        return input_shape
    
    
    def call(self, inputs):
        input_shape = inputs.get_shape().as_list()
        _, h, w, filters = input_shape

        vec_a = K.reshape(inputs, (-1, h * w, filters))
        vec_aT = tf.transpose(vec_a, (0, 2, 1))
        aTa = K.batch_dot(vec_aT, vec_a)
        softmax_aTa = Activation('softmax')(aTa)
        aaTa = K.batch_dot(vec_a, softmax_aTa)
        aaTa = K.reshape(aaTa, (-1, h, w, filters))

        out = self.gamma*aaTa + inputs
        return out

