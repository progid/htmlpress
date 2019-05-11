#!/usr/bin/env python3

import re, sys, os, json, copy, zlib, string, random, math, shutil, htmlmin, cssmin, jsmin, argparse


__author__ = "Igor Terletskiy"
__version__ = "0.0.1"
__license__ = "MIT"

def simplifyDict(rawDict):
	log(rawDict)

def getAttrsFromTag(tagcontent):
	startTag = tagcontent[:tagcontent.find('>') + 1]
	endTag = tagcontent[tagcontent.rfind('</')+2:]
	tagContent = tagcontent[len(startTag):-len(endTag)] if endTag else ''
	tagName = startTag[1:startTag.find(' ')]
	tagAttrsArr = startTag[startTag.find(' ') + 1:].split(' ')
	tatAttrsKeyValueArr = [{ attrs[:attrs.find('=')]: attrs[attrs.find('=')+2:] } for attrs in tagAttrsArr]
	return {
		'tag': tagName,
		'attrs': tatAttrsKeyValueArr,
		'content': tagContent
	}

def getAttrsFromTags(tagslist):
	return [getAttrsFromTag(tag) for tag in tagslist]


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
	resultStyles = links
	for match in startStyleTags:
		startPos, endPos = match.span()
		styleTag = preparedHeadpart[startPos:startPos + preparedHeadpart[startPos:].find(endTag) + len(endTag)]
		resultStyles.append(styleTag)
	for index, item in enumerate(resultStyles):
		preparedHeadpart = preparedHeadpart.replace(item, '')
		resultStyles[index] = cssmin.cssmin(item)

	startTag = '<script>'
	endTag = '</script>'
	searchOpenedTag = startTag[:-1] + r'[^>]*>'
	searchClosedTag = searchOpenedTag + r'[^>]*>' + endTag
	connectScriptTags = re.findall(searchClosedTag, preparedHeadpart)
	preparedHeadpart = re.sub(searchClosedTag, '', preparedHeadpart)
	startScriptTags = re.finditer(searchOpenedTag, preparedHeadpart)
	resultScripts = connectScriptTags
	for match in startScriptTags:
		startPos, endPos = match.span()
		scriptTag = preparedHeadpart[startPos:startPos + preparedHeadpart[startPos:].find(endTag) + len(endTag)]
		resultScripts.append(scriptTag)
	for index, item in enumerate(resultScripts):
		preparedHeadpart = preparedHeadpart.replace(item, '')
		resultScripts[index] = jsmin.jsmin(item)
	return { 'content': preparedHeadpart, 'styles': getAttrsFromTags(resultStyles), 'scripts': getAttrsFromTags(resultScripts) }
	
def optimiseHtmlBodyPart(bodypart):
	startTag = '<script>'
	endTag = '</script>'
	searchOpenedTag = startTag[:-1] + r'[^>]*>'
	searchClosedTag = searchOpenedTag + r'[^>]*>' + endTag
	connectScriptTags = re.findall(searchClosedTag, bodypart)
	preparedBodypart = re.sub(searchClosedTag, '', bodypart)
	startScriptTags = re.finditer(searchOpenedTag, preparedBodypart)
	resultScripts = connectScriptTags
	for match in startScriptTags:
		startPos, endPos = match.span()
		scriptTag = preparedBodypart[startPos:startPos + preparedBodypart[startPos:].find(endTag) + len(endTag)]
		resultScripts.append(scriptTag)
	for index, item in enumerate(resultScripts):
		preparedBodypart = preparedBodypart.replace(item, '')
		resultScripts[index] = jsmin.jsmin(item)
	return { 'content': preparedBodypart, 'scripts': getAttrsFromTags(resultScripts) }


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
	return { filepath: readFile(filepath) for filepath in filepaths }

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