#!/usr/bin/env python3

import re, sys, os, json, copy, zlib, string, random, math, shutil, htmlmin, cssmin, jsmin, argparse, glob

__author__ = "Igor Terletskiy"
__version__ = "0.1.5"
__license__ = "MIT"

compressors = {
	'style': cssmin.cssmin,
	'script': jsmin.jsmin
}

def selectCommonParts(dictContent):
	return saveTo(dictContent)

def simplifyPaths(dictContent):
	offset = 0
	keySplitted = [item.split('/') for item in dictContent]
	for key in keySplitted:
		matched = True
		for subkey in keySplitted:
			matched = matched and key[offset] == subkey[offset]
		if matched and offset < len(key) + 1:
			offset = offset + 1
	preparedKeys = ['/'.join(key[offset:]) for key in keySplitted]
	result = { newKey: dictContent['/'.join(keySplitted[index])] for index, newKey in enumerate(preparedKeys)}
	return result

def simplifyDict(dictContent):
	withSimplifiedPaths = simplifyPaths(dictContent)
	withCommonPart = selectCommonParts(withSimplifiedPaths)
	return saveTo(withCommonPart)

def getAttrsFromTag(tagcontent):
	startTag = tagcontent[:tagcontent.find('>') + 1]
	endTag = tagcontent[tagcontent.rfind('</'):]
	tagContent = tagcontent[len(startTag):-len(endTag)] if endTag else ''
	tagName = startTag[1:startTag.find(' ')]
	tagAttrsArr = startTag[startTag.find(' ') + 1:-1].split(' ') if startTag.find(' ') != -1 else []
	# tagAttrsKeyValueArr = [{ attrs[:attrs.find('=')]: attrs[attrs.find('=')+1:] } for attrs in tagAttrsArr]
	tagAttrsKeyValue = { attrs[:attrs.find('=')]: attrs[attrs.find('=')+1:]  for attrs in tagAttrsArr }
	result = {
		'tag': tagName
	}
	if tagAttrsKeyValue:
		# result['attrs'] = tagAttrsKeyValueArr
		result['attrs'] = tagAttrsKeyValue
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

def makeIsolate(filepath, filedict):
	print('makeIsolate')

def letsEmbedDepsIn(filepath, filedict):
	print('letsEmbedDepsIn')

def saveTo(jsonData, filename='log.txt'):
	file = open(filename, 'w+')
	file.seek(0)
	file.write(json.dumps(jsonData))
	file.truncate()
	file.close()
	return jsonData

def readFile(filepath):
	return open(filepath, 'r').read()

def spreadFolders(filepaths):
	result = []
	for filepath in filepaths:
		if(os.path.isdir(filepath)):
			result.extend([f for f in glob.glob(filepath + "/**/*.html", recursive=True)])
		else:
			result.append(filepath)
	return result


def readFiles(filepaths):
	preparedFilepaths = spreadFolders(filepaths)
	return { filepath: readFile(filepath) for filepath in preparedFilepaths }

def makeHTMLParsing(htmlFilepaths):
	htmlsDict = readFiles(htmlFilepaths)
	preparedHtmlsDict = prepareHTMLsDict(htmlsDict)
	optimisedHtmlsDict = optimiseHtmlsDict(preparedHtmlsDict)
	return optimisedHtmlsDict

def saveData(data, singlefile):
	if singlefile:
		return saveTo(simplifyDict(data), singlefile)
	for item in data:
		filename = item.replace('.html', '.json')
		saveTo(data[item], filename)
	return data

def getArgsData():
	parser = argparse.ArgumentParser()
	parser.add_argument('--input', nargs='+', help='input help')
	parser.add_argument('--singlefile', nargs='?', help='singlefile help')
	parser.add_argument('--built-in', action='store_true', help='built-in help')
	parser.add_argument('--isolate', action='store_true', help='isolate help')
	return parser.parse_args()

def main():
	args = getArgsData()
	preparedData = makeHTMLParsing(args.input)
	if args.built_in:
		letsEmbedDepsIn('x',{})
	if args.isolate:
		makeIsolate('y', {})

	# saveData(preparedData, args.singlefile)

if __name__ == "__main__":
	main()