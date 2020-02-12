import sys
import math
from abc import ABC, abstractmethod
import numpy as np
import tensorflow as tf


def print_loader(progress, total, interval):
    bar = "=" * int(progress / interval) + ">" + " " * (int(total / interval) - int(progress / interval))
    sys.stdout.write(f"\r[{bar}] {int(progress / total * 100)}%")
    sys.stdout.flush()


def convert_string_list_to_tuple_list(string_list):
    return [(int(string_pos[0]), int(string_pos[1])) for string_pos in string_list]


def string_to_np_array(string):
    return np.array([int(string_num) for string_num in string])


class SplitGD(ABC):
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

    @abstractmethod
    def modify_gradients(self, gradients):
        return gradients

    # This returns a tensor of losses, OR the value of the averaged tensor.  Note: use .numpy() to get the
    # value of a tensor.
    def gen_loss(self, features, targets, avg=False):
        predictions = self.model.predict(features)  # Feed-forward pass to produce outputs/predictions
        loss = self.model.loss_functions[0](targets, predictions)
        return tf.reduce_mean(loss).numpy() if avg else loss

    def fit(self, features, targets, epochs=1, mbs=1, vfrac=0.1, verbose=True):
        params = self.model.trainable_weights
        train_ins, train_targs, val_ins, val_targs = split_training_data(features, targets, vfrac=vfrac)
        for _ in range(epochs):
            for _ in range(math.floor(epochs / mbs)):
                with tf.GradientTape() as tape:  # Read up on tf.GradientTape !!
                    feaset, tarset = gen_random_minibatch(train_ins, train_targs, mbs=mbs)
                    # loss = self.gen_loss(feaset, tarset, avg=False)
                    predictions = self.model.predict(features)
                    loss = [param**2 for param in params]
                    gradients = tape.gradient(loss, params)
                    gradients = self.modify_gradients(gradients)
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
    def __init__(self, keras_model, critic):
        super().__init__(keras_model)
        self.critic = critic

    def modify_gradients(self, gradients):
        new_eligibility = self.critic.get_eligibility_trace(self.critic.last_current_state) + gradients
        self.critic.set_eligibility_trace(self.critic.last_current_state.get_state(), new_eligibility)
        return self.critic.calculate_td_error(
            self.critic.last_current_state,
            self.critic.last_next_state,
            self.critic.last_reward) * new_eligibility

