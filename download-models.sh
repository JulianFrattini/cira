#!/bin/bash

FILE_MODELS='model/cira-models.zip'
FILE_CLASSIFIER='model/cira-classifier.bin'
FILE_LABELER='model/cira-labeler.ckpt'

if [ -e $FILE_CLASSIFIER ] && [ -e $FILE_LABELER ] ; then
  echo "$FILE_MODELS already exists"
else
  echo "Download $FILE_MODELS"
  curl -# "https://zenodo.org/record/7186287/files/cira-models.zip?download=1" -o $FILE_MODELS --create-dirs
  echo "Extract $FILE_MODELS"
  unzip -o $FILE_MODELS -d model
fi
