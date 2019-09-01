#!/usr/bin/env python3

import re, sys, os, json, copy, zlib, string, random, math, shutil, htmlmin, cssmin, jsmin, argparse, glob

compressors = {
	'script': jsmin.jsmin,
	'style': cssmin.cssmin,
}

root = False

def getCommonPathOf(paths):
	absolutePaths = []
	minPathSize = 8192
	offset = -1
	for path in paths:
		temp = os.path.abspath(path)[1:].split('/')
		absolutePaths.append(temp)
		minPathSize = len(temp) if len(temp) < minPathSize else minPathSize

	for i in range(minPathSize):
		temp = ''
		for subpath in absolutePaths:
			temp = subpath[i] if not temp else temp
			if(temp != subpath[i]):
				temp = ''
				break
		if(not temp):
			break;
		else:
			offset = i + 1
		temp = ''

	return ['/'.join(path[offset:]) for path in absolutePaths]

def makeBuild(targetPath, jsonData):
	# print(os.path.abspath(targetPath))
	# print(BUILDPATH)
	if(not os.path.exists(targetPath)):
		os.mkdir(targetPath)
		root = os.path.abspath(targetPath)
		


def getJsonFileData(filepath):
	return json.loads(getFileData(filepath))

def getFileData(filepath):
	file = open(filepath, 'r')
	return file.read()

def main():
	# chunkData = getJsonFileData('../router/example/water/code.json')
	xdata = [
		'/Users/inna/igor/HoldTest/extentions',
		'/Users/inna/igor/HoldTest/fonts',
		'/Users/inna/igor/HoldTest/game.html',
		'/Users/inna/igor/HoldTest/img',
		'/Users/inna/igor/HoldTest/index.html',
		'/Users/inna/igor/HoldTest/main.html',
		'/Users/inna/igor/HoldTest/results.html',
		'/Users/inna/igor/HoldTest/scripts',
		'/Users/inna/igor/HoldTest/settings.html',
		'/Users/inna/igor/HoldTest/styles/core.css',
		'/Users/inna/igor/HoldTest/styles/fonts.css'
	]
	# bundledChunkData = makeBuild('../buil', {})
	print('-------------------------------------------------')
	print(getCommonPathOf(xdata))
	print('-------------------------------------------------')
	# print(bundledChunkData)

if __name__ == "__main__":
	main()