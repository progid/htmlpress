#!/usr/bin/env python3

import re, sys, os, json, copy, zlib, string, random, math, shutil, htmlmin, cssmin, jsmin, argparse


__author__ = "Igor Terletskiy"
__version__ = "0.0.1"
__license__ = "MIT"

def optimiseHtmlHeadPart(headcontent):
	

def optimiseHtmlBodyPart(bodypart):
	

def simplifyDict(rawDict):
	


def optimiseHtmlsDict(htmlsdict):
	result = dict()
	for item in htmlsdict:
		htmldict = htmlsdict[item]
		result[item] = optimiseHtmlDict(htmldict)
	return simplifyDict(result)

def optimiseHtmlDict(htmldict):


def parseHTMLHeadPart(content):
	start = content.find('<head>') + len('<head>')
	end = content.rfind('</head>') + len('</head>')
	return content[start:end]

def parseHTMLBodyPart(content):
	start = content.find('<body>') + len('<body>')
	end = content.rfind('</body>') + len('</body>')
	return content[start:end]

def parseHTML(content):
	head = parseHTMLHeadPart(content)
	body = parseHTMLBodyPart(content)
	return { 'head': head, 'body': body }

def prepareHTMLsDict(htmlsDict):
	result = dict()
	for item in htmlsDict:
		htmlcontent = htmlmin.minify(htmlsDict[item])
		result[item] = parseHTML(htmlcontent)
	return result

def log(jsonData):
	file = open('log.txt', 'w+')
	file.seek(0)
	file.write(json.dumps(jsonData))
	file.truncate()
	file.close()
	return jsonData

def readFile(filepath):
	file = open(filepath, 'r')
	return file.read()

def readFiles(filepaths):
	result = dict()
	for filepath in filepaths:
		result[filepath] = readFile(filepath)
	return result

def makeHTMLParsing(htmlFilepaths):
	htmlsDict = readFiles(htmlFilepaths)
	preparedHtmlsDict = prepareHTMLsDict(htmlsDict)
	optimisedHtmlsDict = optimiseHtmlsDict(preparedHtmlsDict)
	# log(htmlsDict)

def getArgsData():
	parser = argparse.ArgumentParser()
	parser.add_argument('--input', nargs='+', help='input help')
	parser.add_argument('--singlefile', action='store_true', help='singlefile help')
	parser.add_argument('--multifiles', action='store_true', help='multifiles help')
	
	return parser.parse_args()

def main():
	args = getArgsData()
	preparedData = makeHTMLParsing(args.input)
	print(args);

if __name__ == "__main__":
	main()