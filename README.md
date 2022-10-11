# CiRA Pipeline

[![GitHub](https://img.shields.io/github/license/JulianFrattini/cira)](./LICENSE)

## Summary of Artifact

This repostitory contains a Python implementation of the functions around the [causality in requirements artifacts (CiRA) initiative](http://www.cira.bth.se/). The initiative is centered around the notion of causal requirements and causality extraction for automatic test case generation. In particular, the main pipeline offers the following functionality:

1. Classifying a sentence regarding its causality (binary classification: causal/non-causal)
2. Labeling the elements of a causal relationship within a causal sentence.
3. Transforming a labeled sentence into a cause-effect graph representing the causal relationship.
4. Transforming a cause-effect graph into a minimal set of test cases (test suite) asserting the behavior implied by the sentence.

## Prerequisites

This package is built and tested using [Python 3.10.0](https://www.python.org/downloads/release/python-3100/). To use the CiRA pipeline, perform the following steps:

1. Make sure the [Rust compiler](https://www.rust-lang.org/tools/install) is installed on your system, as the `tokenizer` package depends on it.
2. Install all required dependencies via `pip3 install -r requirements.txt`.
3. Download and unzip the pre-trained [classification and labeling models](https://doi.org/10.5281/zenodo.7186287) or use the `download-models.sh` script.
4. Create a `.env` file and specify the variables `MODEL_CLASSIFICATION` and `MODEL_LABELING` with the location of the respective models.

## Development inside a Docker Container

You can develop inside a Docker container using a [pre-build image](https://hub.docker.com/r/andib/cira-dev) that contains all dependencies and the recommended classification and labeling models.

For this setup, you need

1. [Docker](https://www.docker.com)
2. [Visual Studio Code](https://code.visualstudio.com)
3. [Remote Development Extension Pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)

Use then the `Remote-Containers: Open Workspace in Container...` command to open the project inside the container.

You can find detailed information about the development container setup [here](https://code.visualstudio.com/docs/remote/containers).

## Tests

Run all tests via `pytest`.

## Usage

To use the CiRA pipeline, instantiate a `src.cira.CiRAConverter` object and specify the location of the pre-trained models.
Then, use the high-level functionality as shown in the [demonstration.ipynb](./demonstration.ipynb) file.
