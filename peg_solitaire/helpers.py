import math
import numpy as np


def convert_string_list_to_tuple_list(string_list):
    return [(int(string_pos[0]), int(string_pos[1])) for string_pos in string_list]


def string_to_np_array(string):
    return np.array([int(string_num) for string_num in string])


class SplitGD:
    """
    !!CODE TAKEN FROM CLASS WEBSITE!!
    This "exposes" the gradients during gradient descent by breaking the call to "fit" into two calls: tape.gradient
    and optimizer.apply_gradients.  This enables intermediate modification of the gradients.  You can find many other
    examples of this concept online and in the (excellent) book "Hands-On Machine Learning with Scikit-Learn, Keras,
    and Tensorflow", 2nd edition, (Geron, 2019).

    This class serves as a wrapper around a keras model.  Then, instead of calling keras_model.fit, just call
    SplitGD.fit.  To use this class, just subclass it and write your own code for the "modify_gradients" method.
    """
    def __init__(self, keras_model):
        self.model = keras_model

    def modify_gradients(self, gradients, delta):
        return gradients

    # This returns a tensor of losses, OR the value of the averaged tensor.  Note: use .numpy() to get the
    # value of a tensor.
    def gen_loss(self, features, targets,  avg=False):
        import tensorflow as tf
        predictions = self.model(tf.convert_to_tensor(features, dtype='float32'))  # Feed-forward pass to produce outputs/predictions
        loss = tf.reduce_sum((targets - predictions)**2)
        return tf.reduce_mean(loss).numpy() if avg else loss

    def fit(self, features, targets, delta, epochs=1, mbs=1, vfrac=0.1, verbose=True):
        import tensorflow as tf
        params = self.model.trainable_weights
        train_ins, train_targs, val_ins, val_targs = split_training_data(features, targets, vfrac=vfrac)
        for _ in range(epochs):
            for _ in range(math.floor(epochs / mbs)):
                with tf.GradientTape() as tape:  # Read up on tf.GradientTape !!
                    feaset, tarset = gen_random_minibatch(train_ins, train_targs, mbs=mbs)
                    loss = self.gen_loss(feaset, tarset)
                    gradients = tape.gradient(loss, params)
                    gradients = self.modify_gradients(gradients, delta)
                    self.model.optimizer.apply_gradients(zip(gradients, params))
            if verbose:
                self.end_of_epoch_display(train_ins, train_targs, val_ins, val_targs)

    # Use the 'metric' to run a quick test on any set of features and targets.  A typical metric is some form of
    # 'accuracy', such as 'categorical_accuracy'.  Read up on Keras.metrics !!
    # Note that the model.metrics__names slot includes the name of the loss function (as 0th entry),
    # whereas the model.metrics slot does not include the loss function, hence the index+1 in the final line.
    # Use your debugger and go through the long list of slots for a keras model.  There are a lot of useful things
    # that you have access to.

    def gen_evaluation(self, features, targets, avg=False, index=0):
        import tensorflow as tf
        predictions = self.model(features)
        evaluation = self.model.metrics[index](targets, predictions)
        #  Note that this returns both a tensor (or value) and the NAME of the metric
        return tf.reduce_mean(evaluation).numpy() if avg else evaluation, self.model.metrics_names[index + 1]

    def status_display(self, features, targets, mode='Train'):
        print(mode + ' *** ', end='')
        print('Loss: ', self.gen_loss(features, targets, avg=True), end=' : ')
        val, name = self.gen_evaluation(features, targets)
        print('Eval({0}): {1} '.format(name, val))

    def end_of_epoch_display(self, train_ins, train_targs, val_ins, val_targs):
        self.status_display(train_ins, train_targs, mode='Train')
        if len(val_ins) > 0:
            self.status_display(val_ins, val_targs, mode='      Validation')


# A few useful auxiliary functions
def gen_random_minibatch(inputs, targets, mbs=1):
    indices = np.random.randint(len(inputs), size=mbs)
    return inputs[indices], targets[indices]


# This returns: train_features, train_targets, validation_features, validation_targets
def split_training_data(inputs, targets, vfrac=0.1, mix=True):
    vc = round(vfrac * len(inputs))  # vfrac = validation_fraction
    # pairs = np.array(list(zip(inputs,targets)))
    if vfrac > 0:
        pairs = list(zip(inputs, targets))
        if mix: np.random.shuffle(pairs)
        vcases = pairs[0:vc]; tcases = pairs[vc:]
        return np.array([tc[0] for tc in tcases]), np.array([tc[1] for tc in tcases]),\
               np.array([vc[0] for vc in vcases]), np.array([vc[1] for vc in vcases])
        #  return tcases[:,0], tcases[:,1], vcases[:,0], vcases[:,1]  # Can't get this to work properly
    else:
        return inputs, targets, [], []


class KerasModelWrapper(SplitGD):
    def __init__(self, keras_model, lambd, gamma):
        super().__init__(keras_model)
        self.eligibilities = []
        self.lambd = lambd
        self.gamma = gamma
        for tensor in self.model.trainable_weights:
            self.eligibilities.append(np.array(np.zeros(tensor.shape)))

    def modify_gradients(self, gradients, delta):
        """
        Updates eligibility trace based on the gradients, and further updates the gradients
        based on the new eligibilities and td-error
        :param gradients: loss function gradients for each weight: list of tensors
        :param delta: TD-error: float
        :return: the updated gradients: list of tensors
        """
        import tensorflow as tf
        for index, tensor in enumerate(self.eligibilities):
            if index % 2 == 0:
                tensor = tensor*self.lambd*self.gamma - gradients[index]
                gradients[index] = tf.math.scalar_mul(delta, tensor)
        return gradients

