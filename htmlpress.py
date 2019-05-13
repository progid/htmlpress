#!/usr/bin/env python3

import re, sys, os, json, copy, zlib, string, random, math, shutil, htmlmin, cssmin, jsmin, argparse


__author__ = "Igor Terletskiy"
__version__ = "0.1.1"
__license__ = "MIT"

def simplifyDict(rawDict):
	log(rawDict)

def getAttrsFromTag(tagcontent):
	startTag = tagcontent[:tagcontent.find('>') + 1]
	endTag = tagcontent[tagcontent.rfind('</'):]
	tagContent = tagcontent[len(startTag):-len(endTag)] if endTag else ''
	tagName = startTag[1:startTag.find(' ')]
	tagAttrsArr = startTag[startTag.find(' ') + 1:-1].split(' ') if startTag.find(' ') != -1 else []
	tagAttrsKeyValueArr = [{ attrs[:attrs.find('=')]: attrs[attrs.find('=')+1:] } for attrs in tagAttrsArr]
	return {
		'tag': tagName,
		'attrs': tagAttrsKeyValueArr,
		'content': tagContent
	}

def getAttrsFromTags(tagslist):
	return [getAttrsFromTag(tag) for tag in tagslist]

def findSimpleTagsWithName(tagName, context, closedTag=False):
	searchTag = r'<' + tagName + r'[^>]*>' + (r'</' + tagName + r'>' if closedTag else '')
	return re.findall(searchTag, context)

def removeSimpleTagsWithName(tagName, context, closedTag=False):
	searchTag = r'<' + tagName + r'[^>]*>' + (r'</' + tagName + r'>' if closedTag else '')
	return re.sub(searchTag, '', context)

def findCompositeTagsWithName(tagName, context):
	result = []
	searchOpenedTag = r'<' + tagName + r'[^>]*>'
	searchClosedTag = r'</' + tagName + r'>'
	findedStartTags = re.finditer(searchOpenedTag, context)
	for match in findedStartTags:
		startPos, endPos = match.span()
		findedTag = context[startPos:endPos + context[endPos:].find(searchClosedTag) + len(searchClosedTag)]
		result.append(findedTag)
	return result

def removeCompositeTagsWithName(tagName, content):
	findedTags = findCompositeTagsWithName(tagName, content)
	preparedContent = content
	for index, item in enumerate(findedTags):
		preparedContent = preparedContent.replace(item, '')
	return preparedContent

def optimiseHtmlPartOf(content):
	links = findSimpleTagsWithName('link', content)
	preparedContent = removeSimpleTagsWithName('link', content)
	styles = findCompositeTagsWithName('style', preparedContent)
	preparedContent = removeCompositeTagsWithName('style', preparedContent)
	connectScripts = findSimpleTagsWithName('script', preparedContent, True)
	preparedContent = removeSimpleTagsWithName('script', preparedContent, True)
	innerScripts = findCompositeTagsWithName('script', preparedContent)
	preparedContent = removeCompositeTagsWithName('script', preparedContent)
	return { 'content': preparedContent, 'styles': getAttrsFromTags(links + styles), 'scripts': getAttrsFromTags(connectScripts + innerScripts) }

def optimiseHtmlDict(htmldict):
	head = optimiseHtmlPartOf(htmldict['head'])
	body = optimiseHtmlPartOf(htmldict['body'])
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