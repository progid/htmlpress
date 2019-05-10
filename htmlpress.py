#!/usr/bin/env python3

import re, sys, os, json, copy, zlib, string, random, math, shutil, htmlmin, cssmin, jsmin, argparse


__author__ = "Igor Terletskiy"
__version__ = "0.0.1"
__license__ = "MIT"

def simplifyDict(rawDict):
	log(rawDict)

def optimiseHtmlHeadPart(headpart):
	linkTag = '<link>'
	startTag = r'<style>'
	endTag = r'</style>'
	searchOpenedTag = startTag[:-1] + r'[^>]*>'
	searchClosedTag = searchOpenedTag + r'[^>]*>' + endTag
	searchLinkTag = linkTag[:-1] + r'[^>]*>'
	links = re.findall(searchLinkTag, headpart)
	preparedHeadpart = re.sub(searchLinkTag, '', headpart)
	startStyleTags = re.finditer(searchOpenedTag, preparedHeadpart)
	result = links
	for match in startStyleTags:
		startPos, endPos = match.span()
		styleTag = preparedHeadpart[startPos:startPos + preparedHeadpart[startPos:].find(endTag) + len(endTag)]
		result.append(styleTag)
	for index, item in enumerate(result):
		preparedHeadpart = preparedHeadpart.replace(item, '')
		result[index] = cssmin.cssmin(item[len(startTag):-len(endTag)])
	return { 'content': preparedHeadpart, 'styles': result }
	
def optimiseHtmlBodyPart(bodypart):
	startTag = '<script>'
	endTag = '</script>'
	searchOpenedTag = startTag[:-1] + r'[^>]*>'
	searchClosedTag = searchOpenedTag + r'[^>]*>' + endTag
	connectScriptTags = re.findall(searchClosedTag, bodypart)
	preparedBodypart = re.sub(searchClosedTag, '', bodypart)
	startScriptTags = re.finditer(searchOpenedTag, preparedBodypart)
	result = connectScriptTags
	for match in startScriptTags:
		startPos, endPos = match.span()
		scriptTag = preparedBodypart[startPos:startPos + preparedBodypart[startPos:].find(endTag) + len(endTag)]
		result.append(scriptTag)
	for index, item in enumerate(result):
		preparedBodypart = preparedBodypart.replace(item, '')
		result[index] = jsmin.jsmin(item[len(startTag):-len(endTag)])
	return { 'content': preparedBodypart, 'scripts': result }


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
	end = content.rfind('</head>')
	return content[start:end]

def parseHTMLBodyPart(content):
	start = content.find('<body>') + len('<body>')
	end = content.rfind('</body>')
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