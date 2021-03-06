# Copyright 2021 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited ("QuantumBlack") name and logo
# (either separately or in combination, "QuantumBlack Trademarks") are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
# or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.

"""Example code for the nodes in the example pipeline. This code is meant
just for illustrating basic Kedro features.

Delete this when you start working on your own Kedro project.
"""
# pylint: disable=invalid-name

import logging
from typing import Any, Dict

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset


class Network(nn.Module):
    def __init__(self, in_features: int, mid_features: int, n_class: int) -> None:
        super(Network, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(in_features, mid_features),
            nn.LeakyReLU(),
            nn.Linear(mid_features, mid_features),
            nn.LeakyReLU(),
            nn.Linear(mid_features, n_class)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc(x)
        return x


def create_model(x_train: pd.DataFrame, y_train: pd.DataFrame, parameters: Dict[str, Any]) -> nn.Module:
    x_train = x_train.to_numpy()
    y_train = y_train.to_numpy()

    in_features = x_train.shape[1]
    n_class = len(np.unique(y_train))
    mid_features = parameters["nn_mid_features"]
    model = Network(in_features, mid_features, n_class)
    model.train()
    return model


def train_model(
    x_train: pd.DataFrame, y_train: pd.DataFrame, model: nn.Module, parameters: Dict[str, Any]
) -> nn.Module:
    """Node for training a simple multi-class logistic regression model. The
    number of training iterations as well as the learning rate are taken from
    conf/project/parameters.yml. All of the data as well as the parameters
    will be provided to this function at the time of execution.
    """
    n_epochs = parameters["n_epochs"]
    lr = parameters["learning_rate"]
    batch_size = parameters["batch_size"]
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    x_train = torch.tensor(x_train.to_numpy())
    y_train = torch.tensor(y_train.to_numpy())

    ds = TensorDataset(x_train, y_train)
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True)

    for epoch in range(n_epochs):
        for step, (data, targets) in enumerate(loader):
            optimizer.zero_grad()
            out = model(data)
            loss = criterion(out, targets)
            loss.backward()
            optimizer.step()

    return model


def predict(model: nn.Module, x_test: pd.DataFrame) -> np.ndarray:
    x_test = torch.tensor(x_test.drop("id", axis=1).to_numpy(), dtype=torch.float32)

    model.eval()
    with torch.no_grad():
        out = model(x_test)

    return out.numpy()


def create_submission(predictions: np.ndarray, submission_df) -> None:

    """Node for reporting the accuracy of the predictions performed by the
    previous node. Notice that this function has no outputs, except logging.
    """
    submission_df.loc[:, 1] = predictions

    submission_df.to_csv("data/08_reporting/submission.csv", header=False, index=False)
    log = logging.getLogger(__name__)
    log.info("??????????????????")
