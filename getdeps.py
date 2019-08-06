#!/usr/bin/env python3

import re, sys, os, json, copy, zlib, string, random, math, shutil, htmlmin, cssmin, jsmin, argparse, glob

linkers = {
	'script': lambda c: '<script>' + jsmin.jsmin(c),
	'link': lambda c: '<style>' + cssmin.cssmin(c) + '</style>',
	'style': lambda c: '<style>' + cssmin.cssmin(c) + '</style>',
}

def compressNodeData(node):
	print(node)

def getJsonFileData(filepath):
	file = open(filepath, 'r')
	rawJsonString = file.read()
	jsonData = json.loads(rawJsonString)
	return jsonData

def main():
	print(getJsonFileData('../router/example/water/code.json'))

if __name__ == "__main__":
	main()