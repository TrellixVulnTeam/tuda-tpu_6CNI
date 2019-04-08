"""Download and preprocess Tuda dataset for DeepSpeech model."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from os import listdir, remove
from os.path import isfile, join

import codecs
import fnmatch
import os
import sys
import tarfile
import tempfile
import unicodedata

from xml.etree import cElementTree as ET
from xml.dom import minidom
import re

from absl import app as absl_app
from absl import flags as absl_flags
import pandas
from six.moves import urllib
import tensorflow as tf

directory = "C:/Users/MaggieEzzat/Desktop/german-speechdata-package-v2.tar/german-speechdata-package-v2"

def delete():
    with open("C:/Users/MaggieEzzat/Desktop/deep_speech/data/corrupted.txt") as corfile:
        content = corfile.readlines()
    content = [x.strip() for x in content]
    cor = []
    for jk in range(len(content)):
        cor.append(content[jk][37:57])

    paths = ["test", "dev","train"]
    for path in paths:
        files = [f for f in listdir(join(directory, path)) if isfile(join(directory, path, f))]
        deleted = 0
        for file in files:
            if ("Kinect-Beam" in file) or ("Yamaha" in file) or ("Samson" in file) or (".wav" in file and os.path.getsize(join(directory, path, file)) <= 4096 ):
                deleted += 1
            else :
                for crptd in cor:
                    if( (".wav" in file) and (crptd in file)):
                        deleted += 1
                        break
        sofar = 1
        for file in files:
            if ("Kinect-Beam" in file) or ("Yamaha" in file) or ("Samson" in file) or (".wav" in file and os.path.getsize(join(directory, path, file)) <= 4096 ):
                remove(join(directory, path, file))
                print(
                            "Deleting from "
                            + path
                            + " : "
                            + str(int((sofar / deleted) * 100))
                            + "%",
                            end="\r",
                        )
                sofar += 1
            else :
                for crptd in cor:
                    if( (".wav" in file) and (crptd in file)):
                        remove(join(directory, path, file))
                        print(
                            "Deleting from "
                            + path
                            + " : "
                            + str(int((sofar / deleted) * 100))
                            + "%",
                            end="\r",
                        )
                        sofar += 1
                        break
        print()


def generate_csv():
    data_dir = directory
    sources = ["test", "dev", "train"]
    for source_name in sources:
        csv = []
        dir_path=os.path.join(data_dir, source_name)
        for file in os.listdir(dir_path):
            if file.endswith(".xml"):
                tree = ET.parse(os.path.join(dir_path, file))
                recording = tree.getroot()
                if(recording.find('html')):
                    print("error")
                    continue
                sent = recording.find('cleaned_sentence')
                sent = sent.text
                transcript = unicodedata.normalize("NFKD", sent).encode(
                    "ascii", "ignore").decode("ascii", "ignore").strip().lower()
                file_xml,_ = file.split(".",1)
                found = 0
                for file_wav in os.listdir(dir_path):
                    if file_wav.startswith(file_xml) and file_wav.endswith(".wav"):
                        file_wav_dir = os.path.join(dir_path,file_wav)
                        wav_filesize = os.path.getsize(file_wav_dir)
                        csv.append((file_wav_dir, wav_filesize, transcript))
                        found += 1
                    if found >= 2 :
                        break
                print(source_name + " : Proccessed : " +  file, end="\r")
        print()
        df = pandas.DataFrame(
            data=csv, columns=["wav_filename", "wav_filesize", "transcript"])
        output_file=os.path.join(data_dir,source_name+".csv")
        df.to_csv(output_file, index=False, sep="\t")

        tf.logging.info("Successfully generated csv file {}".format(output_file))



def main(_):
    delete()
    generate_csv()

if __name__ == "__main__":
  tf.logging.set_verbosity(tf.logging.INFO)
  absl_app.run(main)