import os
import subprocess
import sys
import re
import gc
import signal
from htmlentitydefs import name2codepoint

### PARAMS ####################################################################

# To count the number of categories and to save list of categories
catCount = 0
catList = []

# This is obtained from the dump itself
prefix = None

##
# Whether to preseve links in output
#
keepLinks = False

##
# Whether to transform sections into HTML
#
keepSections = True

##
# Recognize only these namespaces
# w: Internal links to the Wikipedia
#
acceptedNamespaces = set(['w'])

##
# Drop these elements from article text
#
discardElements = set([
    'gallery', 'timeline', 'noinclude', 'pre',
    'table', 'tr', 'td', 'th', 'caption',
    'form', 'input', 'select', 'option', 'textarea',
    'ul', 'li', 'ol', 'dl', 'dt', 'dd', 'menu', 'dir',
    'ref', 'references', 'img', 'imagemap', 'source'
])

##### Main function ###########################################################

#------------------------------------------------------------------------------

selfClosingTags = [ 'br', 'hr', 'nobr', 'ref', 'references' ]

# handle 'a' separetely, depending on keepLinks
ignoredTags = [
        'b', 'big', 'blockquote', 'center', 'cite', 'div', 'em',
        'font', 'h1', 'h2', 'h3', 'h4', 'hiero', 'i', 'kbd', 'nowiki',
        'p', 'plaintext', 's', 'small', 'span', 'strike', 'strong',
        'sub', 'sup', 'tt', 'u', 'var',
]

placeholder_tags = {'math':'formula', 'code':'codice'}

def WikiDocument(id, title, text):
    global fgetPlainTextById, fgetPlainTextByTitle, fgetXmlTextById, fgetXmlTextByTitle
    global catCount, catList
    global fgetPlainTextByIdProc,fgetPlainTextByTitleProc,fgetXmlTextByIdProc,fgetXmlTextByTitleProc,fgetTotalCatByIdProc, \
    fgetTotalCatByTitleProc,fgetListOfCatByIdProc,fgetListOfCatByTitleProc
    url = get_url(id, prefix)

    xmlText = text
    text = clean(text)

    #fgetPlainTextById.write(id + "\t")
    fgetPlainTextByIdProc.stdin.write(id + "\t")

    #fgetPlainTextByTitle.write(title)
    fgetPlainTextByTitleProc.stdin.write(title)

    #fgetPlainTextByTitle.write("\t")
    fgetPlainTextByTitleProc.stdin.write("\t")

    #fgetXmlTextById.write(id + "\t")
    fgetXmlTextByIdProc.stdin.write(id + "\t")

    #fgetXmlTextByTitle.write(title)
    fgetXmlTextByTitleProc.stdin.write(title)

    #fgetXmlTextByTitle.write("\t")
    fgetXmlTextByTitleProc.stdin.write("\t")

    for line in compact(text):
        #fgetPlainTextById.write(line.encode('utf-8') + " ")
        fgetPlainTextByIdProc.stdin.write(line.encode('utf-8') + " ")

        #fgetPlainTextByTitle.write(line.encode('utf-8') + " ")
        fgetPlainTextByTitleProc.stdin.write(line.encode('utf-8') + " ")

    for line in compact(xmlText):
        #fgetXmlTextById.write(line.encode('utf-8') + " ")
        fgetXmlTextByIdProc.stdin.write(line.encode('utf-8') + " ")

        #fgetXmlTextByTitle.write(line.encode('utf-8') + " ")
        fgetXmlTextByTitleProc.stdin.write(line.encode('utf-8') + " ")

    #fgetPlainTextById.write("\n")
    fgetPlainTextByIdProc.stdin.write("\n")

    #fgetPlainTextByTitle.write("\n")
    fgetPlainTextByTitleProc.stdin.write("\n")

    #fgetXmlTextById.write("\n")
    fgetXmlTextByIdProc.stdin.write("\n")

    #fgetXmlTextByTitle.write("\n")
    fgetXmlTextByTitleProc.stdin.write("\n")

    #fgetTotalCatById.write(id + "\t" + str(catCount) + "\n")
    fgetTotalCatByIdProc.stdin.write(id + "\t" + str(catCount) + "\n")

    #fgetTotalCatByTitle.write(title)
    fgetTotalCatByTitleProc.stdin.write(title)

    #fgetTotalCatByTitle.write("\t" + str(catCount) + "\n")
    fgetTotalCatByTitleProc.stdin.write("\t" + str(catCount) + "\n")

    #fgetListOfCatById.write(id + "\t")
    fgetListOfCatByIdProc.stdin.write(id + "\t")

    for i in range(len(catList)):
        #fgetListOfCatById.write(catList[i])
        fgetListOfCatByIdProc.stdin.write(catList[i])

        #fgetListOfCatByTitle.write(catList[i])
        fgetListOfCatByTitleProc.stdin.write(catList[i])

        if i != len(catList) - 1:
            #fgetListOfCatById.write(",")
            fgetListOfCatByIdProc.stdin.write(",")

            #fgetListOfCatByTitle.write(",")
            fgetListOfCatByTitleProc.stdin.write(",")

    #fgetListOfCatById.write("\n")
    fgetListOfCatByIdProc.stdin.write("\n")

    #fgetListOfCatByTitle.write("\n")
    fgetListOfCatByTitleProc.stdin.write("\n")
    catCount = 0
    catList = []

def get_url(id, prefix):
    return "%s?curid=%s" % (prefix, id)

# Normalize title
def normalizeTitle(title):
  title=title.replace(' ', '_').replace('&quot;', '"').replace('&amp;', '&').replace("&#039;", "'").encode('utf-8')
  return title

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        code = m.group(1)
        try:
            if text[1] == "#":  # character reference
                if text[2] == "x":
                    return unichr(int(code[1:], 16))
                else:
                    return unichr(int(code))
            else:               # named entity
                return unichr(name2codepoint[code])
        except:
            return text # leave as is

    return re.sub("&#?(\w+);", fixup, text)


# Match HTML comments
comment = re.compile(r'<!--.*?-->', re.DOTALL)

# Match elements to ignore
discard_element_patterns = []
for tag in discardElements:
    pattern = re.compile(r'<\s*%s\b[^>]*>.*?<\s*/\s*%s>' % (tag, tag), re.DOTALL | re.IGNORECASE)
    discard_element_patterns.append(pattern)

# Match ignored tags
ignored_tag_patterns = []


def ignoreTag(tag):
    left = re.compile(r'<\s*%s\b[^>]*>' % tag, re.IGNORECASE)
    right = re.compile(r'<\s*/\s*%s>' % tag, re.IGNORECASE)
    ignored_tag_patterns.append((left, right))


for tag in ignoredTags:
    ignoreTag(tag)

# Match selfClosing HTML tags
selfClosing_tag_patterns = []
for tag in selfClosingTags:
    pattern = re.compile(r'<\s*%s\b[^/]*/\s*>' % tag, re.DOTALL | re.IGNORECASE)
    selfClosing_tag_patterns.append(pattern)

# Match HTML placeholder tags
placeholder_tag_patterns = []
for tag, repl in placeholder_tags.items():
    pattern = re.compile(r'<\s*%s(\s*| [^>]+?)>.*?<\s*/\s*%s\s*>' % (tag, tag), re.DOTALL | re.IGNORECASE)
    placeholder_tag_patterns.append((pattern, repl))

# Match preformatted lines
preformatted = re.compile(r'^ .*?$', re.MULTILINE)

# Match external links (space separates second optional parameter)
externalLink = re.compile(r'\[\w+.*? (.*?)\]')
externalLinkNoAnchor = re.compile(r'\[\w+[&\]]*\]')

# Matches bold/italic
bold_italic = re.compile(r"'''''([^']*?)'''''")
bold = re.compile(r"'''(.*?)'''")
italic_quote = re.compile(r"''\"(.*?)\"''")
italic = re.compile(r"''([^']*)''")
quote_quote = re.compile(r'""(.*?)""')
# Matches space
spaces = re.compile(r' {2,}')

# Matches dots
dots = re.compile(r'\.{4,}')


# A matching function for nested expressions, e.g. namespaces and tables.
def dropNested(text, openDelim, closeDelim):
    openRE = re.compile(openDelim)
    closeRE = re.compile(closeDelim)
    # partition text in separate blocks { } { }
    matches = []  # pairs (s, e) for each partition
    nest = 0  # nesting level
    start = openRE.search(text, 0)
    if not start:
        return text
    end = closeRE.search(text, start.end())
    next = start
    while end:
        next = openRE.search(text, next.end())
        if not next:  # termination
            while nest:  # close all pending
                nest -= 1
                end0 = closeRE.search(text, end.end())
                if end0:
                    end = end0
                else:
                    break
            matches.append((start.start(), end.end()))
            break
        while end.end() < next.start():
            # { } {
            if nest:
                nest -= 1
                # try closing more
                last = end.end()
                end = closeRE.search(text, end.end())
                if not end:  # unbalanced
                    if matches:
                        span = (matches[0][0], last)
                    else:
                        span = (start.start(), last)
                    matches = [span]
                    break
            else:
                matches.append((start.start(), end.end()))
                # advance start, find next close
                start = next
                end = closeRE.search(text, next.end())
                break  # { }
        if next != start:
            # { { }
            nest += 1
    # collect text outside partitions
    res = ''
    start = 0
    for s, e in matches:
        res += text[start:s]
        start = e
    res += text[start:]
    return res


def dropSpans(matches, text):
    """Drop from text the blocks identified in matches"""
    matches.sort()
    res = ''
    start = 0
    for s, e in matches:
        res += text[start:s]
        start = e
    res += text[start:]
    return res


# Match interwiki links, | separates parameters.
# First parameter is displayed, also trailing concatenated text included
# in display, e.g. s for plural).
#
# Can be nested [[File:..|..[[..]]..|..]], [[Category:...]], etc.
# We first expand inner ones, than remove enclosing ones.
#
wikiLink = re.compile(r'\[\[([^[]*?)(?:\|([^[]*?))?\]\](\w*)')

parametrizedLink = re.compile(r'\[\[.*?\]\]')


# Function applied to wikiLinks
def make_anchor_tag(match):
    global keepLinks, catCount, catList
    link = match.group(1)
    colon = link.find(':')
    # print link[:colon]
    if colon > 0 and link[:colon] == "Category":
        catList.append(normalizeTitle(link[colon + 1:]))
        catCount += 1
        # print catCount

    if colon > 0 and link[:colon] not in acceptedNamespaces:
        return ''
    trail = match.group(3)
    anchor = match.group(2)
    if not anchor:
        anchor = link
    anchor += trail
    if keepLinks:
        return '<a href="%s">%s</a>' % (link, anchor)
    else:
        return anchor


def clean(text):
    # FIXME: templates should be expanded
    # Drop transclusions (template, parser functions)
    # See: http://www.mediawiki.org/wiki/Help:Templates
    text = dropNested(text, r'{{', r'}}')

    # Drop tables
    text = dropNested(text, r'{\|', r'\|}')

    # Expand links
    text = wikiLink.sub(make_anchor_tag, text)
    # Drop all remaining ones
    text = parametrizedLink.sub('', text)

    # Handle external links
    text = externalLink.sub(r'\1', text)
    text = externalLinkNoAnchor.sub('', text)

    # Handle bold/italic/quote
    text = bold_italic.sub(r'\1', text)
    text = bold.sub(r'\1', text)
    text = italic_quote.sub(r'&quot;\1&quot;', text)
    text = italic.sub(r'&quot;\1&quot;', text)
    text = quote_quote.sub(r'\1', text)
    text = text.replace("'''", '').replace("''", '&quot;')

    # text = text.replace('&quot;', '"')

    ################ Process HTML ###############

    # turn into HTML
    text = unescape(text)
    # do it again (&amp;nbsp;)
    text = unescape(text)

    # Collect spans

    matches = []
    # Drop HTML comments
    for m in comment.finditer(text):
        matches.append((m.start(), m.end()))

    # Drop self-closing tags
    for pattern in selfClosing_tag_patterns:
        for m in pattern.finditer(text):
            matches.append((m.start(), m.end()))

    # Drop ignored tags
    for left, right in ignored_tag_patterns:
        for m in left.finditer(text):
            matches.append((m.start(), m.end()))
        for m in right.finditer(text):
            matches.append((m.start(), m.end()))

    # Bulk remove all spans
    text = dropSpans(matches, text)

    # Cannot use dropSpan on these since they may be nested
    # Drop discarded elements
    for pattern in discard_element_patterns:
        text = pattern.sub('', text)

    # Expand placeholders
    for pattern, placeholder in placeholder_tag_patterns:
        index = 1
        for match in pattern.finditer(text):
            text = text.replace(match.group(), '%s_%d' % (placeholder, index))
            index += 1

    #############################################

    # Drop preformatted
    # This can't be done before since it may remove tags
    text = preformatted.sub('', text)

    # Cleanup text
    text = text.replace('\t', ' ')
    text = spaces.sub(' ', text)
    text = dots.sub('...', text)
    text = re.sub(r'\n\W+?\n', '\n', text)  # lines with only punctuations
    text = text.replace(',,', ',').replace(',.', '.')
    return text


section = re.compile(r'(==+)\s*(.*?)\s*\1')


def compact(text):
    """Deal with headers, lists, empty sections, residuals of tables"""
    page = []  # list of paragraph
    headers = {}  # Headers for unfilled sections
    emptySection = False  # empty sections are discarded
    inList = False  # whether opened <UL>

    for line in text.split('\n'):

        if not line:
            continue
        # Handle section titles
        m = section.match(line)
        if m:
            title = m.group(2)
            lev = len(m.group(1))
            if keepSections:
                page.append("%s:" % (title))
            if title and title[-1] not in '!?':
                title += '.'
            headers[lev] = title
            # drop previous headers
            for i in headers.keys():
                if i > lev:
                    del headers[i]
            emptySection = True
            continue
        # Handle page title
        if line.startswith('++'):
            title = line[2:-2]
            if title:
                if title[-1] not in '!?':
                    title += '.'
                page.append(title)
        # handle lists
        elif line[0] in '*#:;':
            if keepSections:
                page.append(line)
            else:
                continue
        # Drop residuals of lists
        elif line[0] in '{|' or line[-1] in '}':
            continue
        # Drop irrelevant lines
        elif (line[0] == '(' and line[-1] == ')') or line.strip('.-') == '':
            continue
        elif len(headers):
            items = headers.items()
            items.sort()
            for (i, v) in items:
                page.append(v)
            headers.clear()
            page.append(line)  # first line
            emptySection = False
        elif not emptySection:
            page.append(line)

    return page


def handle_unicode(entity):
    numeric_code = int(entity[2:-1])
    if numeric_code >= 0x10000: return ''
    return unichr(numeric_code)




### Files to write output ##########
# fcheckPageId = open("checkPageId.txt", "w")
# fcheckPageTitle = open("checkPageTitle.txt", "w")
# fgetPageTitleById = open("getPageTitleById.txt", "w")
# fgetPageIdByTitle = open("getPageIdByTitle.txt", "w")
# fcheckRedirectById = open("checkRedirectById.txt", "w")
# fcheckRedirectByTitle = open("checkRedirectByTitle.txt", "w")
# fgetRedirectTitleById = open("getRedirectTitleById.txt", "w")
# fgetRedirectTitleByTitle = open("getRedirectTitleByTitle.txt", "w")
# fgetPageURLById = open("getPageURLById.txt", "w")
# fgetPageURLByTitle = open("getPageURLByTitle.txt", "w")
# fgetPlainTextById = open("getPlainTextById.txt", "w")
# fgetPlainTextByTitle = open("getPlainTextByTitle.txt", "w")
# fgetXmlTextById = open("getXmlTextById.txt", "w")
# fgetXmlTextByTitle = open("getXmlTextByTitle.txt", "w")
# fcheckDisambiguationById = open("checkDisambiguationById.txt", "w")
# fcheckDisambiguationByTitle = open("checkDisambiguationByTitle.txt", "w")
# fgetTotalCatById = open("getTotalCatById.txt", "w")
# fgetTotalCatByTitle = open("getTotalCatByTitle.txt", "w")
# fgetListOfCatById = open("getListOfCatById.txt", "w")
# fgetListOfCatByTitle = open("getListOfCatByTitle.txt", "w")
# fcheckCategoryId = open("checkCategoryId.txt", "w")
# fgetCategoryIdByTitle = open("getCategoryIdByTitle.txt", "w")
# fcheckCategoryTitle = open("checkCategoryTitle.txt", "w")
# fgetCategoryTitleById = open("getCategoryTitleById.txt", "w")
# fgetCategoryURLById = open("getCategoryURLById.txt", "w")
# fgetCategoryURLByTitle = open("getCategoryURLByTitle.txt", "w")

fcheckPageId = '/pythonOutputFiles/checkPageId.txt'
fcheckPageIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fcheckPageId], stdin=subprocess.PIPE)
fcheckPageTitle = '/pythonOutputFiles/checkPageTitle.txt'
fcheckPageTitleProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fcheckPageTitle], stdin=subprocess.PIPE)
fgetPageTitleById = '/pythonOutputFiles/getPageTitleById.txt'
fgetPageTitleByIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetPageTitleById], stdin=subprocess.PIPE)
fgetPageIdByTitle = '/pythonOutputFiles/getPageIdByTitle.txt'
fgetPageIdByTitleProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetPageIdByTitle], stdin=subprocess.PIPE)
fcheckRedirectById = '/pythonOutputFiles/checkRedirectById.txt'
fcheckRedirectByIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fcheckRedirectById], stdin=subprocess.PIPE)
fcheckRedirectByTitle = '/pythonOutputFiles/checkRedirectByTitle.txt'
fcheckRedirectByTitleProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fcheckRedirectByTitle], stdin=subprocess.PIPE)
fgetRedirectTitleById = '/pythonOutputFiles/getRedirectTitleById.txt'
fgetRedirectTitleByIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetRedirectTitleById], stdin=subprocess.PIPE)
fgetRedirectTitleByTitle = '/pythonOutputFiles/getRedirectTitleByTitle.txt'
fgetRedirectTitleByTitleProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetRedirectTitleByTitle], stdin=subprocess.PIPE)
fgetPageURLById = '/pythonOutputFiles/getPageURLById.txt'
fgetPageURLByIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetPageURLById], stdin=subprocess.PIPE)
fgetPageURLByTitle = '/pythonOutputFiles/getPageURLByTitle.txt'
fgetPageURLByTitleProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetPageURLByTitle], stdin=subprocess.PIPE)
fgetPlainTextById = '/pythonOutputFiles/getPlainTextById.txt'
fgetPlainTextByIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetPlainTextById], stdin=subprocess.PIPE)
fgetPlainTextByTitle = '/pythonOutputFiles/getPlainTextByTitle.txt'
fgetPlainTextByTitleProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetPlainTextByTitle], stdin=subprocess.PIPE)
fgetXmlTextById = '/pythonOutputFiles/getXmlTextById.txt'
fgetXmlTextByIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetXmlTextById], stdin=subprocess.PIPE)
fgetXmlTextByTitle = '/pythonOutputFiles/getXmlTextByTitle.txt'
fgetXmlTextByTitleProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetXmlTextByTitle], stdin=subprocess.PIPE)
fcheckDisambiguationById = '/pythonOutputFiles/checkDisambiguationById.txt'
fcheckDisambiguationByIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fcheckDisambiguationById], stdin=subprocess.PIPE)
fcheckDisambiguationByTitle = '/pythonOutputFiles/checkDisambiguationByTitle.txt'
fcheckDisambiguationByTitleProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fcheckDisambiguationByTitle], stdin=subprocess.PIPE)
fgetTotalCatById = '/pythonOutputFiles/getTotalCatById.txt'
fgetTotalCatByIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetTotalCatById], stdin=subprocess.PIPE)
fgetTotalCatByTitle = '/pythonOutputFiles/getTotalCatByTitle.txt'
fgetTotalCatByTitleProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetTotalCatByTitle], stdin=subprocess.PIPE)
fgetListOfCatById = '/pythonOutputFiles/getListOfCatById.txt'
fgetListOfCatByIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetListOfCatById], stdin=subprocess.PIPE)
fgetListOfCatByTitle = '/pythonOutputFiles/getListOfCatByTitle.txt'
fgetListOfCatByTitleProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetListOfCatByTitle], stdin=subprocess.PIPE)
fcheckCategoryId = '/pythonOutputFiles/checkCategoryId.txt'
fcheckCategoryIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fcheckCategoryId], stdin=subprocess.PIPE)
fgetCategoryIdByTitle = '/pythonOutputFiles/getCategoryIdByTitle.txt'
fgetCategoryIdByTitleProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetCategoryIdByTitle], stdin=subprocess.PIPE)
fcheckCategoryTitle = '/pythonOutputFiles/checkCategoryTitle.txt'
fcheckCategoryTitleProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fcheckCategoryTitle], stdin=subprocess.PIPE)
fgetCategoryTitleById = '/pythonOutputFiles/getCategoryTitleById.txt'
fgetCategoryTitleByIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetCategoryTitleById], stdin=subprocess.PIPE)
fgetCategoryURLById = '/pythonOutputFiles/getCategoryURLById.txt'
fgetCategoryURLByIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetCategoryURLById], stdin=subprocess.PIPE)
fgetCategoryURLByTitle = '/pythonOutputFiles/getCategoryURLByTitle.txt'
fgetCategoryURLByTitleProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetCategoryURLByTitle], stdin=subprocess.PIPE)




def closeFile():
    #global fcheckPageId, fcheckPageTitle, fgetPageTitleById, fgetPageIdByTitle, fgetPageURLById, fgetPageURLByTitle
    global fcheckPageIdProc, fcheckPageTitleProc, fgetPageTitleByIdProc, fgetPageIdByTitleProc, fgetPageURLByIdProc, \
        fgetPageURLByTitleProc

    #global fcheckDisambiguationById, fcheckDisambiguationByTitle
    global fcheckDisambiguationByIdProc, fcheckDisambiguationByTitleProc

    #global fcheckRedirectById, fcheckRedirectByTitle, fgetRedirectTitleById, fgetRedirectTitleByTitle
    global fcheckRedirectByIdProc, fcheckRedirectByTitleProc, fgetRedirectTitleByIdProc, fgetRedirectTitleByTitleProc

    #global fcheckCategoryId, fgetCategoryIdByTitle, fcheckCategoryTitle, fgetCategoryTitleById
    global fcheckCategoryIdProc, fgetCategoryIdByTitleProc, fcheckCategoryTitleProc, fgetCategoryTitleByIdProc

    #global fgetCategoryURLById, fgetCategoryURLByTitle
    global fgetCategoryURLByIdProc, fgetCategoryURLByTitleProc

    #fcheckPageId.close()
    os.killpg(os.getpgid(fcheckPageIdProc.pid), signal.SIGTERM)

    #fcheckPageTitle.close()
    os.killpg(os.getpgid(fcheckPageTitleProc.pid), signal.SIGTERM)

    #fgetPageTitleById.close()
    os.killpg(os.getpgid(fgetPageTitleByIdProc.pid), signal.SIGTERM)

    #fgetPageIdByTitle.close()
    os.killpg(os.getpgid(fgetPageIdByTitleProc.pid), signal.SIGTERM)

    #fcheckRedirectById.close()
    os.killpg(os.getpgid(fcheckRedirectByIdProc.pid), signal.SIGTERM)

    #fcheckRedirectByTitle.close()
    os.killpg(os.getpgid(fcheckRedirectByTitleProc.pid), signal.SIGTERM)

    #fgetRedirectTitleById.close()
    os.killpg(os.getpgid(fgetRedirectTitleByIdProc.pid), signal.SIGTERM)

    #fgetRedirectTitleByTitle.close()
    os.killpg(os.getpgid(fgetRedirectTitleByTitleProc.pid), signal.SIGTERM)

    #fgetPageURLById.close()
    os.killpg(os.getpgid(fgetPageURLByIdProc.pid), signal.SIGTERM)

    #fgetPageURLByTitle.close()
    os.killpg(os.getpgid(fgetPageURLByTitleProc.pid), signal.SIGTERM)

    #fgetPlainTextById.close()
    os.killpg(os.getpgid(fgetPlainTextByIdProc.pid), signal.SIGTERM)

    #fgetPlainTextByTitle.close()
    os.killpg(os.getpgid(fgetPlainTextByTitleProc.pid), signal.SIGTERM)

    #fgetXmlTextById.close()
    os.killpg(os.getpgid(fgetXmlTextByIdProc.pid), signal.SIGTERM)

    #fgetXmlTextByTitle.close()
    os.killpg(os.getpgid(fgetXmlTextByTitleProc.pid), signal.SIGTERM)

    #fcheckDisambiguationById.close()
    os.killpg(os.getpgid(fcheckDisambiguationByIdProc.pid), signal.SIGTERM)

    #fcheckDisambiguationByTitle.close()
    os.killpg(os.getpgid(fcheckDisambiguationByTitleProc.pid), signal.SIGTERM)

    #fgetTotalCatById.close()
    os.killpg(os.getpgid(fgetTotalCatByIdProc.pid), signal.SIGTERM)

    #fgetTotalCatByTitle.close()
    os.killpg(os.getpgid(fgetTotalCatByTitleProc.pid), signal.SIGTERM)

    #fgetListOfCatById.close()
    os.killpg(os.getpgid(fgetListOfCatByIdProc.pid), signal.SIGTERM)

    #fgetListOfCatByTitle.close()
    os.killpg(os.getpgid(fgetListOfCatByTitleProc.pid), signal.SIGTERM)

    #fcheckCategoryId.close()
    os.killpg(os.getpgid(fcheckCategoryIdProc.pid), signal.SIGTERM)

    #fgetCategoryIdByTitle.close()
    os.killpg(os.getpgid(fgetCategoryIdByTitleProc.pid), signal.SIGTERM)

    #fcheckCategoryTitle.close()
    os.killpg(os.getpgid(fcheckCategoryTitleProc.pid), signal.SIGTERM)

    #fgetCategoryTitleById.close()
    os.killpg(os.getpgid(fgetCategoryTitleByIdProc.pid), signal.SIGTERM)

    #fgetCategoryURLById.close()
    os.killpg(os.getpgid(fgetCategoryURLByIdProc.pid), signal.SIGTERM)

    #fgetCategoryURLByTitle.close()
    os.killpg(os.getpgid(fgetCategoryURLByTitleProc.pid), signal.SIGTERM)


### Function to write outputbto files #########################################

def pageUrlWriter(id, title):
    #global fcheckPageId, fcheckPageTitle, fgetPageTitleById, fgetPageIdByTitle, fgetPageURLById, fgetPageURLByTitle
    global fcheckDisambiguationById, fcheckDisambiguationByTitle
    global fcheckPageIdProc,fcheckPageTitleProc,fgetPageTitleByIdProc,fgetPageIdByTitleProc,fgetPageURLByIdProc, \
            fgetPageURLByTitleProc,fcheckDisambiguationByIdProc,fcheckDisambiguationByTitleProc

    url = get_url(id, prefix)

    #fcheckPageId.write(id + "\t" + "true" + "\n")
    fcheckPageIdProc.stdin.write(id + "\t" + "true" + "\n")

    #fcheckPageTitle.write(title)
    fcheckPageTitleProc.stdin.write(title)

    #fcheckPageTitle.write("\t" + "true" + "\n")
    fcheckPageTitleProc.stdin.write("\t" + "true" + "\n")

    #fgetPageTitleById.write(id + "\t")
    fgetPageTitleByIdProc.stdin.write(id + "\t")

    #fgetPageTitleById.write(title)
    fgetPageTitleByIdProc.stdin.write(title)

    #fgetPageTitleById.write("\n")
    fgetPageTitleByIdProc.stdin.write("\n")

    #fgetPageIdByTitle.write(title)
    fgetPageIdByTitleProc.stdin.write(title)

    #fgetPageIdByTitle.write("\t" + id + "\n")
    fgetPageIdByTitleProc.stdin.write("\t" + id + "\n")

    #fgetPageURLById.write(id + "\t" + url + "\n")
    fgetPageURLByIdProc.stdin.write(id + "\t" + url + "\n")

    #fgetPageURLByTitle.write(title)
    fgetPageURLByTitleProc.stdin.write(title)

    #fgetPageURLByTitle.write("\t" + url + "\n")
    fgetPageURLByTitleProc.stdin.write("\t" + url + "\n")

    matchObj = re.search(r'((.*))', title, re.M | re.I)

    # print "try" + matchObj.group(1)

    if title.find('(disambiguation)') != -1:
        #fcheckDisambiguationById.write(id + "\t" + "true" + "\n")
        fcheckDisambiguationByIdProc.stdin.write(id + "\t" + "true" + "\n")

        #fcheckDisambiguationByTitle.write(title)
        fcheckDisambiguationByTitleProc.stdin.write(title)

        #fcheckDisambiguationByTitle.write("\t" + "true" + "\n")
        fcheckDisambiguationByTitleProc.stdin.write("\t" + "true" + "\n")


def categoryWriter(id, title):
    #global fcheckCategoryId, fgetCategoryIdByTitle, fcheckCategoryTitle, fgetCategoryTitleById
    global fcheckCategoryIdProc, fgetCategoryIdByTitleProc, fcheckCategoryTitleProc, fgetCategoryTitleByIdProc
    global fgetCategoryURLByTitleProc
    #global fgetCategoryURLById, fgetCategoryURLByTitle

    url = get_url(id, prefix)

    #fcheckCategoryId.write(id + "\t" + "true" + "\n")
    fcheckCategoryIdProc.stdin.write(id + "\t" + "true" + "\n")

    #fcheckCategoryTitle.write(title)
    fcheckCategoryTitleProc.stdin.write(title)

    #fcheckCategoryTitle.write("\t" + "true" + "\n")
    fcheckCategoryTitleProc.stdin.write("\t" + "true" + "\n")

    #fgetCategoryTitleById.write(id + "\t")
    fgetCategoryTitleByIdProc.stdin.write(id + "\t")

    #fgetCategoryTitleById.write(title)
    fgetCategoryTitleByIdProc.stdin.write(title)

    #fgetCategoryTitleById.write("\n")
    fgetCategoryTitleByIdProc.stdin.write("\n")

    #fgetCategoryIdByTitle.write(title)
    fgetCategoryIdByTitleProc.stdin.write(title)

    #fgetCategoryIdByTitle.write("\t" + id + "\n")
    fgetCategoryIdByTitleProc.stdin.write("\t" + id + "\n")

    #fgetCategoryURLById.write(id + "\t" + url + "\n")
    fgetCategoryURLByIdProc.stdin.write(id + "\t" + url + "\n")

    #fgetCategoryURLByTitle.write(title)
    fgetCategoryURLByTitleProc.stdin.write(title)

    #fgetCategoryURLByTitle.write("\t" + url + "\n")
    fgetCategoryURLByTitleProc.stdin.write("\t" + url + "\n")


## function to write redirect details to file ##

def redirectWriter(id, title, redirectTitle):
    #global fcheckRedirectById, fcheckRedirectByTitle, fgetRedirectTitleById, fgetRedirectTitleByTitle
    global fcheckRedirectByIdProc, fcheckRedirectByTitleProc, fgetRedirectTitleByIdProc, fgetRedirectTitleByTitleProc

    #fcheckRedirectById.write(id + "\t" + "true" + "\n")
    fcheckRedirectByIdProc.stdin.write(id + "\t" + "true" + "\n")

    #fcheckRedirectByTitle.write(title)
    fcheckRedirectByTitleProc.stdin.write(title)

    #fcheckRedirectByTitle.write("\t" + "true" + "\n")
    fcheckRedirectByTitleProc.stdin.write("\t" + "true" + "\n")

    #fgetRedirectTitleById.write(id + "\t")
    fgetRedirectTitleByIdProc.stdin.write(id + "\t")

    #fgetRedirectTitleById.write(redirectTitle)
    fgetRedirectTitleByIdProc.stdin.write(redirectTitle)

    #fgetRedirectTitleById.write("\n")
    fgetRedirectTitleByIdProc.stdin.write("\n")

    #fgetRedirectTitleByTitle.write(title)
    fgetRedirectTitleByTitleProc.stdin.write("\n")

    #fgetRedirectTitleByTitle.write("\t")
    fgetRedirectTitleByTitleProc.stdin.write("\t")

    #fgetRedirectTitleByTitle.write(redirectTitle)
    fgetRedirectTitleByTitleProc.stdin.write(redirectTitle)

    #fgetRedirectTitleByTitle.write("\n")
    fgetRedirectTitleByTitleProc.stdin.write("\n")


## function to write redirect list to file ##

def redirectList():
    #print "Creating redirect api data..."
    global fgetRedirectTitleByTitleProc,fgetRedirectTitleByIdProc

    os.killpg(os.getpgid(fgetRedirectTitleByTitleProc.pid), signal.SIGTERM)

    #freadTitle = open("getRedirectTitleByTitle.txt", "r")
    #getTotalRedirectByTitle = open("getTotalRedirectByTitle.txt", "w")
    #getListOfRedirectByTitle = open("getListOfRedirectTitleByTitle.txt", "w")

    freadTitle = '/pythonOutputFiles/getRedirectTitleByTitle.txt'
    freadTitleProc = subprocess.Popen(['hadoop', 'fs', '-cat', '-', freadTitle], stdin=subprocess.PIPE)

    getTotalRedirectByTitle = '/pythonOutputFiles/getTotalRedirectByTitle.txt'
    getTotalRedirectByTitleProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', getTotalRedirectByTitle],
                                                   stdin=subprocess.PIPE)

    getListOfRedirectByTitle = '/pythonOutputFiles/getListOfRedirectTitleByTitle.txt'
    getListOfRedirectByTitleProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', getListOfRedirectByTitle],
                                                    stdin=subprocess.PIPE)

    #get_list_total(freadTitle, getTotalRedirectByTitle, getListOfRedirectByTitle)

    get_list_total(freadTitleProc, getTotalRedirectByTitleProc, getListOfRedirectByTitleProc)

    os.killpg(os.getpgid(getTotalRedirectByTitleProc.pid), signal.SIGTERM)

    os.killpg(os.getpgid(getListOfRedirectByTitleProc.pid), signal.SIGTERM)

    #getTotalRedirectByTitle.close()
    #getListOfRedirectByTitle.close()

    os.killpg(os.getpgid(fgetRedirectTitleByIdProc.pid), signal.SIGTERM)

    #freadId = open("getRedirectTitleById.txt", "r")
    #getTotalRedirectById = open("getTotalRedirectById.txt", "w")
    #getListOfRedirectById = open("getListOfRedirectTitleById.txt", "w")

    freadId = '/pythonOutputFiles/getRedirectTitleById.txt'
    freadIdProc = subprocess.Popen(['hadoop', 'fs', '-cat', '-', freadId], stdin=subprocess.PIPE)

    getTotalRedirectById = '/pythonOutputFiles/getTotalRedirectById.txt'
    getTotalRedirectByIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', getTotalRedirectById],
                                                   stdin=subprocess.PIPE)

    getListOfRedirectById = '/pythonOutputFiles/getListOfRedirectTitleById.txt'
    getListOfRedirectByIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', getListOfRedirectById],
                                                    stdin=subprocess.PIPE)

    #get_list_total(freadId, getTotalRedirectById, getListOfRedirectById)

    get_list_total(freadIdProc, getTotalRedirectByIdProc, getListOfRedirectByIdProc)

    os.killpg(os.getpgid(getTotalRedirectByIdProc.pid), signal.SIGTERM)

    os.killpg(os.getpgid(getListOfRedirectByIdProc.pid), signal.SIGTERM)

    #getTotalRedirectByTitle.close()
    #getListOfRedirectByTitle.close()

    #print "Done"


def get_list_total(fread, fwriteTotal, fwriteList):
    newList = [[]]

    for line in fread:
        wordList = line.strip().split()
        if len(wordList) == 2:
            wordList.reverse()
            newList.append(wordList)

    i = 0
    list = []
    prev = ""

    for row in sorted(newList):

        if len(row) == 2:

            if prev == row[0]:
                list.append(row[1])

                if i == len(newList) - 1:
                    fwriteList.write(row[0] + "\t")
                    fwriteList.stdin.write(row[0] + "\t")

                    fwriteTotal.write(row[0] + "\t")
                    fwriteTotal.stdin.write(row[0] + "\t")

                    count = len(list)
                    for x in range(count):
                        fwriteList.write(str(list[x]))
                        fwriteList.stdin.write(str(list[x]))

                        if x != count - 1:
                            fwriteList.write(",")
                            fwriteList.stdin.write(",")

                    fwriteTotal.write(str(count) + "\n")
                    fwriteTotal.stdin.write(str(count) + "\n")

            else:
                if i != 0:
                    fwriteList.write(prev + "\t")
                    fwriteList.stdin.write(prev + "\t")

                    fwriteTotal.write(prev + "\t")
                    fwriteTotal.stdin.write(prev + "\t")

                    fwriteTotal.write(str(count) + "\n")
                    fwriteTotal.stdin.write(str(count) + "\n")

                    count = len(list)
                    for x in range(count):
                        fwriteList.write(str(list[x]))
                        fwriteList.stdin.write(str(list[x]))

                        if x != count - 1:
                            fwriteList.write(",")
                            fwriteList.stdin.write(",")

                    fwriteList.write("\n")
                    fwriteList.stdin.write("\n")

                    fwriteTotal.write(str(count) + "\n")
                    fwriteTotal.stdin.write(str(count) + "\n")

                prev = row[0]
                list = []

                list.append(row[1])
                i = +1

    del newList

# ------------------------------------------------------------------------------

tagRE = re.compile(r'(.*?)<(/?\w+)[^>]*>(?:([^<]*)(<.*?>)?)?')

### READER ###################################################################
def process_data():
    global prefix
    global ftitle, fid, ftext, fxml

    page = []
    id = None
    inText = False
    redirect = False
    #fname = raw_input("Enter the input xml file name: ")
    #finput = codecs.open(fname, "r")
    #print "Creating page api data..."
    #for line in sys.stdin:
    for line in sys.stdin:
        line = line.decode('utf-8')
        tag = ''
        if '<' in line:
            m = tagRE.search(line)
            if m:
                tag = m.group(2)
        if tag == 'page':
            page = []
            redirect = False
        elif tag == 'id' and not id:
            id = m.group(3)
        elif tag == 'title':
            title = m.group(3)
        elif tag == 'redirect':
            redirect = True
            matchObj = re.search(r'title="(.*)"', line, re.M | re.I)
            redirectTitle = matchObj.group(1)
        elif tag == 'text':
            inText = True
            line = line[m.start(3):m.end(3)] + '\n'
            page.append(line)
            if m.lastindex == 4:  # open-close
                inText = False
        elif tag == '/text':
            if m.group(1):
                page.append(m.group(1) + '\n')
            inText = False
        elif inText:
            page.append(line)
        elif tag == '/page':
            colon = title.find(':')
            if (colon < 0 or title[:colon] in acceptedNamespaces) and \
                    not redirect:
                title = normalizeTitle(title)
            WikiDocument(id, title, ''.join(page))
            pageUrlWriter(id, title)
        if (colon < 0 or title[:colon] in acceptedNamespaces) and \
                redirect:
            title = normalizeTitle(title)
        redirectTitle = normalizeTitle(redirectTitle)
        pageUrlWriter(id, title)
        redirectWriter(id, title, redirectTitle)
        if title[:colon] == 'Category':
            title = normalizeTitle(title[colon + 1:])
            categoryWriter(id, title)
            id = None
            page = []
        elif tag == 'base':
            # discover prefix from the xml dump file
            # /mediawiki/siteinfo/base
            base = m.group(3)
            prefix = base[:base.rfind("/")]

    #print "Done"

if __name__ == '__main__':
    process_data()
    ##Forcing Garabage collector to release unreferenced variables
    gc.collect()
    redirectList()
    closeFile()