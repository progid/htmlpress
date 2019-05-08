#!/usr/bin/env python3

import re, sys, os, json, copy, zlib, string, random, math, shutil, htmlmin, cssmin, jsmin, argparse


__author__ = "Igor Terletskiy"
__version__ = "0.0.1"
__license__ = "MIT"



def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--input', nargs='+', help='input help')
	parser.add_argument('--output', nargs='?', help='output help')
	args = parser.parse_args()

	print(args.output);

if __name__ == "__main__":
	main()