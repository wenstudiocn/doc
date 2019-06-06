import json
import re
import requests
import os

from zipfile import ZipFile
from io import BytesIO
from django.template import Template, Context, Engine

def metadata(title=None, description=None, og_image=None, twitter_image=None):
    meta = {
        "og": {},
        "twitter": {}
    }

    if title:
        meta["title"] = title
        meta["og"]["title"] = title
        meta["twitter"]["title"] = title

    if description:
        meta["description"] = description
        meta["og"]["description"] = description
        meta["twitter"]["description"] = description

    if og_image:
        meta["og"]["image"] = og_image

    if twitter_image:
        meta["twitter"]["image"] = twitter_image

    return meta


def format_signature(type, name, parameters):
    if type == "function" or type == "macro":
        plist = [e['name'] for e in parameters]
        pstr = ', '.join(plist)
        return '%s(%s)' % (name, pstr)

    if type == 'message':
        if len(parameters) > 0:
            plist = []
            for e in parameters:
                p = e['name']
                if p[-1] == ']':
                    plist.append(p[0:-1] + '=&hellip;' + ']')
                else:
                    plist.append(p + '=&hellip;')

            pstr = ', '.join(plist)
            return '"%s", { %s }' % (name, pstr)
        else:
            return '"%s"' % (name)

    return "unknown"


def render_page(index, ref):
    document_name = "http"
    document_url_name = document_name
    document_name = document_name.replace("-", "_")

    # Create function, method, macro and message signatures
    for item in ref['functions']:
        item['signature'] = format_signature('function', item['name'], item['parameters'])
        item['display_name'] = format_signature('function', item['name'], item['parameters'])

    for item in ref['macros']:
        item['signature'] = format_signature('macro', item['name'], item['parameters'])
        item['display_name'] = format_signature('macro', item['name'], item['parameters'])

    for item in ref['messages']:
        item['signature'] = format_signature('message', item['name'], item['parameters'])

    refdocgroups = [
        {
            "group": "SYSTEM",
            "namespaces": "crash,gui,go,profiler,render,resource,sys,window,engine,physics"
        },
        {
            "group": "COMPONENTS",
            "namespaces": "camera,collectionproxy,collectionfactory,collisionobject,factory,label,model,particlefx,sound,spine,sprite,tilemap"
        },
        {
            "group": "SCRIPT",
            "namespaces": "buffer,builtins,html5,http,image,json,msg,timer,vmath,zlib"
        },
        {
            "group": "EXTENSIONS",
            "namespaces": "facebook,iap,iac,push,webview"
        },
        {
            "group": "DEFOLD SDK",
            "namespaces": "dmAlign,dmArray,dmBuffer,dmConditionVariable,dmConfigFile,dmExtension,dmGraphics,dmHash,dmJson,dmLog,dmMutex,dmScript,sharedlibrary"
        },
        {
            "group": "LUA STANDARD LIBS",
            "namespaces": "base,bit,coroutine,debug,io,socket,math,os,package,string,table"
        },
    ]
    menu = []
    for rgroup in refdocgroups:
        section = {}
        section['name'] = rgroup["group"]
        section['items'] = []
        for namespace in rgroup["namespaces"].split(","):
            if namespace in index:
                item = {}
                item['name'] = index[namespace]['name']
                item['path'] = namespace
                section['items'].append(item)
                # Remove from index since we have put it in menu
                index.pop(namespace, None)
        menu.append(section)

    # Add any rest index entries to the menu
    if len(index) > 0:
        section = {}
        section['name'] = 'Unspecified'
        section['items'] = []
        for rest in index:
            item = {}
            item['name'] = index[rest]['name']
            item['path'] = rest
            section['items'].append(item)
        menu.append(section)

    # Meta data set in the base template
    title = ""
    description = 'Defold API reference documentation.'
    for sect in menu:
        for item in sect['items']:
            if item['path'] == document_name:
                title = item['name'] + ' reference'
                break

    page_meta = metadata(title=title, description=description)

    query_string = ''
    context = {"ref": ref, "menu": menu, "document_name": document_name, "document_url_name": document_url_name, "query_string": query_string, "meta": page_meta}

    dirs = ["./templates/"]
    libraries = {
        "basic_filters": "templatetags.basic_filters",
        "documentation_filters": "templatetags.documentation_filters",
    }
    e = Engine(dirs = dirs, libraries = libraries)
    t = e.get_template("ref/ref.html")
    c = Context(context)
    return t.render(c)


def transform_refdoc(doc):
    functions = []
    macros = []
    messages = []
    constants = []
    properties = []
    structs = []
    enums = []
    typedefs = []
    methods = []
    for e in doc['elements']:
        if e['type'] == 'FUNCTION':
            functions.append(e)
        if e['type'] == 'MACRO':
            macros.append(e)
        elif e['type'] == 'MESSAGE':
            messages.append(e)
        elif e['type'] == 'VARIABLE':
            constants.append(e)
        elif e['type'] == 'PROPERTY':
            properties.append(e)
        elif e['type'] == 'STRUCT':
            structs.append(e)
        elif e['type'] == 'ENUM':
            enums.append(e)
        elif e['type'] == 'TYPEDEF':
            typedefs.append(e)
        elif e['type'] == 'METHOD':
            methods.append(e)

    t = {}
    t['functions'] = functions
    t['methods'] = methods
    t['macros'] = macros
    t['messages'] = messages
    t['constants'] = constants
    t['properties'] = properties
    t['structs'] = structs
    t['enums'] = enums
    t['typedefs'] = typedefs
    t['info'] = doc['info']
    return t


def merge_refdocs(doc1, doc2):
    if doc1['info']['name'] == '':
        doc1['info']['name'] = doc2['info']['name']
    if doc1['info']['brief'] == '':
        doc1['info']['brief'] = doc2['info']['brief']
    if doc1['info']['description'] == '':
        doc1['info']['description'] = doc2['info']['description']
    doc1['functions'].extend(doc2['functions'])
    doc1['methods'].extend(doc2['methods'])
    doc1['macros'].extend(doc2['macros'])
    doc1['messages'].extend(doc2['messages'])
    doc1['constants'].extend(doc2['constants'])
    doc1['properties'].extend(doc2['properties'])
    doc1['structs'].extend(doc2['structs'])
    doc1['enums'].extend(doc2['enums'])
    doc1['typedefs'].extend(doc2['typedefs'])
    return doc1


# Fetch zip file with refdoc jsons from the specified (sha1) build
def fetch_refdoczip(sha1):
    print("Fetching refdoc for %s" % (sha1))
    archive_url = 'https://d.defold.com/archive/%s/engine/share/ref-doc.zip' % (sha1)
    result = requests.get(archive_url)
    return ZipFile(BytesIO(result.content))


# Grab a new api docs package from the d-servers, unpack and prep for presentation.
def generate(sha1_or_latest):
    try:
        sha1 = sha1_or_latest
        version = sha1_or_latest
        latest = False
        if sha1_or_latest == '':
            print("No argument found. Provide either a SHA1 hash or the string 'latest'")
            return

        if sha1_or_latest == 'latest':
            # Update latest ref doc set
            print("Downloading info.json")
            latest_info = 'https://d.defold.com/stable/info.json'
            response = requests.get(latest_info)
            info = response.json()
            sha1 = info['sha1']
            version = info['version']
            latest = True

        zipdata = fetch_refdoczip(sha1)
        jsondata = {}
        # Transform and merge namespaces
        for filename in zipdata.namelist():
            if re.match('.*[.]json', filename):
                raw_json = json.loads(zipdata.read(filename))
                namespace = raw_json['info']['namespace']
                if namespace in jsondata:
                    # If namespace is saved - merge
                    a = jsondata[namespace]
                    b = transform_refdoc(raw_json)
                    jsondata[namespace] = merge_refdocs(a, b)
                else:
                    jsondata[namespace] = transform_refdoc(raw_json)
                    jsondata[namespace]['info']['version'] = version

        # Save index
        index = {}
        for namespace in jsondata:
            index[namespace] = jsondata[namespace]['info']

        directory = os.path.join("out", sha1, "ref")
        if not os.path.exists(directory):
            os.makedirs(directory)

        for namespace in jsondata:
            filename = os.path.join(directory, namespace + ".html")
            with open(filename, "w") as file:
                print("Rendering page '%s' to '%s'" % (namespace, filename))
                page = render_page(index.copy(), jsondata[namespace])
                file.write(page)

    except Exception as ex:
        print("Error: " + str(ex))


generate("latest")
