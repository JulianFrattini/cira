# CiRA Pipeline

## Summary of Artifact

This repostitory contains a Python implementation of the functions around the [causality in requirements artifacts (CiRA) initiative](http://www.cira.bth.se/). The initiative is centered around the notion of causal requirements and causality extraction for automatic test case generation. In particular, the main pipeline offers the following functionality:

1. Classifying a sentence regarding its causality (binary classification: causal/non-causal)
2. Labeling the elements of a causal relationship within a causal sentence.
3. Transforming a labeled sentence into a cause-effect graph representing the causal relationship.
4. Transforming a cause-effect graph into a minimal set of test cases (test suite) asserting the behavior implied by the sentence.

## Installation

To use the CiRA pipeline, perform the following steps:

1. Make sure all dependencies listed in the requirements.txt file are installed.
2. Download the pre-trained [classification](https://zenodo.org/record/5159501#.Ytq28ITP3-g) and [labeling](https://zenodo.org/record/5550387#.Ytq3QYTP3-g) (use the model named roberta_dropout_linear_layer_multilabel.ckpt for optimal performance) models.

## Usage

To use the CiRA pipeline, instantiate a src.cira.CiRAConverter object and supply it with the pre-trained models. Then, use the high-level functionality as shown in the demonstrator.ipynb file.