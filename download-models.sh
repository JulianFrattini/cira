#!/bin/bash

FILE_MODELS='model/cira-models.zip'

if [ -e $FILE_MODELS ]; then
  echo "$FILE_MODELS already exists"
else
  echo "Download $FILE_MODELS"
  curl -# "https://zenodo.org/record/7186287/files/cira-models.zip?download=1" -o $FILE_MODELS --create-dirs
  echo "Extract $FILE_MODELS"
  unzip $FILE_MODELS -d model
fi