#!/bin/bash

FILE_CLASSIFIER='model/bertclassifier.bin'
FILE_CHECKPOINTS='model/checkpoints.zip'

if [ -e $FILE_CLASSIFIER ]; then
  echo "$FILE_CLASSIFIER already exists"
else
  echo "Download $FILE_CLASSIFIER"
  curl -# "https://zenodo.org/record/5159501/files/bertclassifier.bin?download=1" -o $FILE_CLASSIFIER --create-dirs
fi

if [ -e $FILE_CHECKPOINTS ]; then
  echo "$FILE_CHECKPOINTS already exists"
else
  echo "Download $FILE_CHECKPOINTS"
  curl -# "https://zenodo.org/record/5550387/files/checkpoints.zip?download=1" -o $FILE_CHECKPOINTS --create-dirs
  echo "Extract $FILE_CHECKPOINTS"
  unzip $FILE_CHECKPOINTS -d model
fi

