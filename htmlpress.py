#!/usr/bin/env python3

import re, sys, os, json, copy, zlib, string, random, math, shutil, htmlmin, cssmin, jsmin, argparse


__author__ = "Igor Terletskiy"
__version__ = "0.0.1"
__license__ = "MIT"

def simplifyDict(rawDict):
	log(rawDict)

def optimiseHtmlHeadPart(headpart):
	links = re.findall(r'<link[^>]*>', headpart)
	preparedHeadpart = re.sub(r'<link[^>]*>', '', headpart)
	startStyleTags = re.finditer(r'<style[^>]*>', headpart)
	result = links
	for match in startStyleTags:
		startPos, endPos = match.span()
		styleTag = headpart[startPos:startPos + headpart[startPos:].find('</style>')]
		result.append(styleTag)
	return result
	
def optimiseHtmlBodyPart(bodypart):
	connectScriptTags = re.findall(r'<script[^>]*></script>', bodypart)
	preparedBodypart = re.sub(r'<script[^>]*></script>', '', bodypart)
	startScriptTags = re.finditer(r'<script[^>]*>', bodypart)
	result = connectScriptTags
	for match in startScriptTags:
		startPos, endPos = match.span()
		scriptTag = bodypart[startPos:startPos + bodypart[startPos:].find('</script>')]
		result.append(scriptTag)
	return result


def optimiseHtmlDict(htmldict):
	head = optimiseHtmlHeadPart(htmldict['head'])
	body = optimiseHtmlBodyPart(htmldict['body'])
	return { 'head': head, 'body': body }

def optimiseHtmlsDict(htmlsdict):
	result = dict()
	for item in htmlsdict:
		htmldict = htmlsdict[item]
		result[item] = optimiseHtmlDict(htmldict)
	return simplifyDict(result)

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
	parser.add_argument('--singlefile', nargs='?', help='singlefile help')
	
	return parser.parse_args()

def main():
	args = getArgsData()
	preparedData = makeHTMLParsing(args.input)

if __name__ == "__main__":
	main()