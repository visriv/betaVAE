"""
Implements the betaVAE from the paper: https://arxiv.org/pdf/1606.05579.pdf
"""
import sys
sys.path.append("../utils")

import torch
import torch.nn as nn

from vae import VAE
from model_utils import *
from utils import *


class betaVAE(VAE):
    """ Class that implements a Disentangled Variational Autoencoder (Beta VAE) """

    def __init__(self, architecture, hyperparameters, dataset_info):
        """
        :param architecture: (dict)  A dictionary containing the hyperparameters that define the
                                     architecture of the model.
        :param input_shape:  (tuple) A tuple that corresponds to the shape of the input.
        :param z_dimension:  (int)   The dimension of the latent vector z (bottleneck).
        :param beta:         (float) The disentanglment factor to be multiplied with the KL
                                     divergence.

        The constructor of the Disentangled Variational Autoencoder.
        """

        # invoke the constructor of the VAE class, as the architecture is the same
        super(betaVAE, self).__init__(architecture, hyperparameters, dataset_info)

        # store the value of beta in the class as it exists only in this VAE variation
        self.beta = hyperparameters["beta"]


    def criterion(self, X, X_hat, mean, std):
        """
        :param X:     (Tensor) The original input data that was passed to the VAE.
                               (N, input_shape[1], H, W)
        :param X_hat: (Tensor) The reconstructed data, the output of the VAE.
                               (N, input_shape[1], H, W)
        :param mean:  (Tensor) The output of the mean layer, computed with the output of the
                               encoder. (N, z_dim)
        :param std:   (Tensor) The output of the standard deviation layer, computed with the output
                               of the encoder. (N, z_dim)

        :return: (Dict) A dictionary containing the values of the losses computed.

        This method computes the loss of the betaVAE using the formula:

            L(x, x_hat) = - E_{z ~ Q_{phi}(z | x)}[log(P_{theta}(x|z))]
                          + beta * D_{KL}[Q_{phi}(z | x) || P_{theta}(x)]

        Intuitively, the expectation term is the Data Fidelity term, and the second term is a
        regularizer that makes sure the distribution of the encoder and the decoder stay close.
        """
        # get the 2 losses
        data_fidelity_loss = VAE._data_fidelity_loss(X, X_hat)
        kl_divergence_loss = VAE._kl_divergence_loss(mean, std)

        # add them, and then compute the mean over all training examples
        loss = -data_fidelity_loss + self.beta * kl_divergence_loss
        loss = torch.mean(loss)

        # place them all inside a dictionary and return it
        losses = {"data_fidelity": torch.mean(data_fidelity_loss),
                  "kl-divergence": torch.mean(kl_divergence_loss),
                  "beta_kl-divergence": torch.mean(self.beta * kl_divergence_loss),
                  "loss": loss}
        return losses
