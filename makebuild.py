#!/usr/bin/env python3

import re, sys, os, json, copy, zlib, string, random, math, shutil, htmlmin, cssmin, jsmin, argparse, glob

compressors = {
	'script': jsmin.jsmin,
	'style': cssmin.cssmin,
}

def makeBundle(externalPath, jsonData):
	resultJsonData = copy.deepcopy(jsonData)
	list = (resultJsonData['head']['scripts'] +
		resultJsonData['head']['styles'] +
		resultJsonData['body']['scripts'] +
		resultJsonData['body']['styles'])
	for node in list:
		tag = node['tag'] = 'style' if node['tag'] == 'link' else node['tag']
		attrs = node['attrs'] if 'attrs' in node else {}
		accessor = 'href' if 'href' in attrs else 'src' if 'src' in attrs else ''
		if accessor and attrs[accessor]:
			attrs[accessor] = externalPath + attrs[accessor]
			node['content'] = compressors[tag](getFileData(attrs[accessor]))
			del attrs[accessor]
		if 'attrs' in node and not len(attrs):
			del node['attrs']
	return resultJsonData

def getJsonFileData(filepath):
	return json.loads(getFileData(filepath))

def getFileData(filepath):
	file = open(filepath, 'r')
	return file.read()

def main():
	chunkData = getJsonFileData('../router/example/water/code.json')
	bundledChunkData = makeBundle('../router/example/water/', chunkData)
	print(bundledChunkData)

if __name__ == "__main__":
	main()