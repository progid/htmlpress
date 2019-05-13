#!/usr/bin/env python3

import re, sys, os, json, copy, zlib, string, random, math, shutil, htmlmin, cssmin, jsmin, argparse

__author__ = "Igor Terletskiy"
__version__ = "0.1.4"
__license__ = "MIT"

compressors = {
	'style': cssmin.cssmin,
	'script': jsmin.jsmin
}

def getAttrsFromTag(tagcontent):
	startTag = tagcontent[:tagcontent.find('>') + 1]
	endTag = tagcontent[tagcontent.rfind('</'):]
	tagContent = tagcontent[len(startTag):-len(endTag)] if endTag else ''
	tagName = startTag[1:startTag.find(' ')]
	tagAttrsArr = startTag[startTag.find(' ') + 1:-1].split(' ') if startTag.find(' ') != -1 else []
	tagAttrsKeyValueArr = [{ attrs[:attrs.find('=')]: attrs[attrs.find('=')+1:] } for attrs in tagAttrsArr]
	result = {
		'tag': tagName
	}
	if tagAttrsKeyValueArr:
		result['attrs'] = tagAttrsKeyValueArr
	if tagContent:
		result['content'] = compressors[tagName](tagContent)
	return result

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

def parseHTMLSection(content, section):
	start = content.find('<' + section + '>') + len(section) + 2
	end = content.rfind('</' + section + '>')
	return content[start:end]

def parseHTML(content):
	head = parseHTMLSection(content, 'head')
	body = parseHTMLSection(content, 'body')
	return { 'head': head, 'body': body }

def prepareHTMLsDict(htmlsDict):
	return { item: parseHTML(htmlmin.minify(htmlsDict[item], remove_comments=True, remove_empty_space=True)) for item in htmlsDict }

def optimiseHtmlsDict(htmlsdict):
	return {item: optimiseHtmlDict(htmlsdict[item]) for item in htmlsdict}

def saveTo(jsonData, filename='out.txt'):
	file = open(filename, 'w+')
	file.seek(0)
	file.write(json.dumps(jsonData))
	file.truncate()
	file.close()
	return jsonData

def readFile(filepath):
	return open(filepath, 'r').read()

def readFiles(filepaths):
	return { filepath: readFile(filepath) for filepath in filepaths }

def makeHTMLParsing(htmlFilepaths):
	htmlsDict = readFiles(htmlFilepaths)
	preparedHtmlsDict = prepareHTMLsDict(htmlsDict)
	optimisedHtmlsDict = optimiseHtmlsDict(preparedHtmlsDict)
	return optimisedHtmlsDict

def saveData(data, singlefile):
	if singlefile:
		return saveTo(data, singlefile)
	for item in data:
		filename = item[item.rfind('/') + 1:item.rfind('.') + 1] + 'json'
		saveTo(data[item], filename)
	return data

def getArgsData():
	parser = argparse.ArgumentParser()
	parser.add_argument('--input', nargs='+', help='input help')
	parser.add_argument('--singlefile', nargs='?', help='singlefile help')
	return parser.parse_args()

def main():
	args = getArgsData()
	preparedData = makeHTMLParsing(args.input)
	saveData(preparedData, args.singlefile)

if __name__ == "__main__":
	main()