# -*- coding: utf-8 -*-
#
# This file is part of Aggregator.
#
# Copyright (c) 2013 <ahref Foundation -- All rights reserved.
# Author Santosh Singh <santosh@incaendo.com>
#
#This file can not be copied and/or distributed without the express permission of <ahref Foundation. # NOQA
##############################################################################


"""
Aggregator
======================
"""

from flask import Blueprint, request
import re
import urllib
from aggregator.models import Entry  # NOQA
from aggregator import db, app
from aggregator.manage import requires_auth, api_response
import datetime
from mongokit import *  # NOQA
from flask import json
from tag import TagManager
import error_codes

entry = Blueprint('entry', __name__, template_folder='templates')

# EntryManager
#
# This class is responsible for handling the saving and retrieving of entries


class EntryManager:
    def __init__(self):
        self.collection = db.entry
        self.sortingTagSlug = ''
        self.sortingDirection = 1
    # parseSchemeUri
    #
    # This method parses scheme Uri from the tag string passed by user

    def parseSchemeUri(self, tagString):
        schemeUri = ''
        result = re.search('^(\w+)(\{(.*)\})', tagString)
        if result:
            schemeUri = result.group[1]
        return schemeUri
# parseSchemeName
#
# This method parses scheme Name from the tag string passed by user

    def parseSchemeName(self, tagString):
        schemeName = ''
        result = re.search('^(\w+)(\[(.*)\])', tagString)
        if result:
            schemeName = result.group[1]
        return schemeName

# parseIndividualTagForScheme
#
# This methid parses indiviual tags against the given scheme and URI from tagString #  # NOQA
    def parseIndividualTagForScheme(self, tagString):
        tagDetail = {}
        result = re.search('^(\w+)(\{(.*)\})*(\[(.*)\])*', tagString)
        if result:
            tagDetail['slug'] = result.group(1)
        if result.group(2) and result.group(3):
            tagDetail['scheme'] = result.group(3)
        if result.group(4) and result.group(5):
            tagDetail['scheme_name'] = result.group(5)
        return tagDetail

  # parseTags
  #
  # This method parses tags from the tag string passed by user.
    def parseTags(self, tag):
        explodedTag = tag.split(',')
        tagsAnd = []
        tagsOr = []
        for t in explodedTag:
            if t.find('|'):
                explodeForOr = t.split('|')
                tagDetail = self.parseIndividualTagForScheme(explodeForOr[0])
                tagsAnd.append(tagDetail)
                for i in range(1, len(explodeForOr)):
                    tagDetail = self.parseIndividualTagForScheme(explodeForOr[i])   # NOQA
                    tagsOr.append(tagDetail)
            else:
                tagDetail = self.parseIndividualTagForScheme(t)
                tagsAnd.append(tagDetail)
        return {'and': tagsAnd, 'or': tagsOr}

# prepareEntry
# This method prepares entries for returning them as a result of user query
    def prepareEntry(self, entry, user_data):
        if 'enclosures' in user_data:
            links = ''
            if int(user_data['enclosures']) == 0:
                links = entry['links']
                del links['enclosures']
        if 'return_content' in user_data:
            content = entry['content']
            return_content = user_data['return_content'].split(',')
            final_content = []
            for i, value in enumerate(content):
                keys = value.keys()
                if keys[0] in return_content:
                    final_content.append(value)
            if len(final_content) > 0:
                entry['content'] = final_content
        entry['id'] = str(entry['_id'])
        if 'tags' in entry:
            for tags in entry['tags']:
                if 'id' in tags:
                    tags['id'] = str(tags['id'])
        if 'creation_date' in entry and entry['creation_date'] != '':
            entry['creation_date'] = datetime.datetime.fromtimestamp(float(entry['creation_date'])).strftime('%Y-%m-%d %H:%M:%S')  # NOQA
        if 'modification_date' in entry and entry['modification_date'] != '':
            entry['modification_date'] = datetime.datetime.fromtimestamp(float(entry['modification_date'])).strftime('%Y-%m-%d %H:%M:%S')  # NOQA
        if 'publication_date' in entry and entry['publication_date'] != '':
            entry['publication_date'] = datetime.datetime.fromtimestamp(float(entry['publication_date'])).strftime('%Y-%m-%d %H:%M:%S')  # NOQA
        entry.pop('_id')
        return entry

    # getTagsOfEntry
    #
    # This function is used to get the tags of
    # entry from the entry collection
    #
    # It returns a list of tags
    #
    ##########################################################################
    def getTagsOfEntry(self, id):
        existing_tags = []
        tags = db.entry.find({'_id': ObjectId(id)}, {'tags': 1, '_id': 0})
        for tag in tags:
            if ('tags' in tag):
                tags = tag['tags']
        for tag in tags:
            tags = TagManager()
            tags.remove(tag)
            existing_tags.append(tag['slug'])
        return existing_tags

    # delete
    #
    # This function is used to delete entry from the entry collection
    #
    # It returns a message
    #
    ##########################################################################
    def delete(self, id):
        db.entry.remove({'_id': ObjectId(id)})
        return 'Entry Deleted'

    #
    #deleteByRelated
    #
    # This function is used to delete entries by related type and id.
    #
    def deleteByRelated(self, related):
        message = ''
        flag = True
        if 'type' not in related:
            message = 'Type can not be empty in related'
            flag = False
        if flag and 'id' not in related:
            message = 'ID can not be empty in related'
            flag = False
        if flag is True:
            condition = {}
            condition['$and'] = [{'related.type': related['type']},
                                 {'related.id': related['id']}]
            db.entry.remove(condition)
            message = 'Entries deleted successfully'
        return message

    # update
    #
    # This function is used to update entry in the entry collection.
    #
    # It returns a Message
    #
    ##########################################################################
    def update(self, entry_data):
        id = entry_data['_id']
        entry_data.pop('_id')
        if 'removed_tags' in entry_data:
            for tag in entry_data['removed_tags']:
                tags = TagManager()
                tags.remove(tag)
            entry_data.pop('removed_tags')
        db.entry.update({'_id': ObjectId(id)}, {'$set': entry_data})
        return 'Entry updated'

    # save
    #
    # This function is used to save entry in the entry collection.
    #
    # It returns a Message
    #
    ##########################################################################
    def save(self, entry_data):
        if 'tags' in entry_data:
            for tag in entry_data['tags']:
                tags = TagManager()
                tag_id = tags.save(tag)
                tag['id'] = tag_id
        id = db.entry.insert(entry_data)
        return json.dumps({'entryID': str(id)})

    # get
    #
    # This function is used to get the records from the document entry.
    # It takes user_data (array) as input. user_data can have title,guid,tags,
    # status, sort, limit and interval
    #
    # It returns an array of records
    #
    ##########################################################################
    def get(self, user_data):
        sort = '_id'
        offset = 0
        conditions = {}
        count = 0

        # We provide support for filtering on the basis of id.
        if 'id' in user_data:
            conditions['_id'] = ObjectId(user_data['id'])

        # Support for filtering on the basis of source
        if 'source' in user_data:
            conditions['source'] = user_data['source']

        # We provide support for filtering on the basis of title.
        if 'title' in user_data:
            conditions['title'] = {'$regex': user_data['title']}

        # Limit can be imposed on number of results to return. If no limit is
        # mentioned, only 1 result is returned.
        if 'limit' in user_data:
            limit = int(user_data['limit'])
        else:
            limit = 1

        # We provide support for filtering of results on the basis of their
        # status. By default, entries with status active are returned in
        # results
        if 'status' in user_data:
            conditions['status'] = user_data['status']
        else:
            conditions['status'] = 'active'

        # We provide support for filtering of results on the basis of their guid   # NOQA
        if 'guid' in user_data:
            guidList = user_data['guid'].split(',@#,')
            guidCondition = []
            for gid in guidList:
                guidCondition.append({'guid': gid})
            conditions['$or'] = guidCondition

        # We provide support for returning results between two dates.
        if 'interval' in user_data:
            interval = user_data['interval'].split(',')
            start = interval[0]
            end = interval[1]
            conditions['publication_date'] = {'$gte': start, '$lte': end}

        # We provide support for filtering of results on the basis of their
        # tags, tagSchemea, tagschemeUri, tagweight
        if 'tags' in user_data:
            andtags = []
            ortags = []
            tagString = user_data['tags']
            result = self.parseTags(tagString)
            if len(result['and']) > 0:
                for tag in result['and']:
                    if 'scheme' in tag:
                        andtags.append({'tags.slug': tag['slug'], 'tags.scheme': tag['scheme']})  # NOQA
                    else:
                        andtags.append({'tags.slug': tag['slug']})
            if len(result['or']) > 0:
                for tag in result['or']:
                    if 'scheme' in tag:
                        ortags.append({'tags.slug': tag['slug'], 'tags.scheme': tag['scheme']})  # NOQA
                    else:
                        ortags.append({'tags.slug': tag['slug']})
                conditions['$or'] = ortags
                for andtag in andtags:
                    conditions['$or'].append(andtag)
            elif len(result['and']) > 0:
                conditions['$and'] = andtags
        return_fields = []

        if 'related' in user_data:
            related = {}
            related = user_data['related'].split(',')
            conditions['related'] = {'type': related[0], 'id': related[1]}   # NOQA

        # User can define which fields do they want in the results returned.
        # By default, only id is returned.
        if 'return_fields' in user_data:
            return_fields = user_data['return_fields'].split(',')
            for i in return_fields:
                i = i.strip()
                if i not in self.collection.Entry() and i != '*':
                    if i != 'id' and i not in return_fields_list:
                        return_fields.remove(i)

        # Sorting is also supported.
        if 'sort' in user_data:
            if '-' == user_data['sort'][0]:
                user_data['sort'] = user_data['sort'].replace("-", "", 1)
                sort = self.manageSorting(user_data['sort'], -1)
            else:
                sort = self.manageSorting(user_data['sort'], 1)

        if 'offset' in user_data:
            offset = int(user_data['offset'])

        # Results can be filtered on the basis of author also
        if 'author' in user_data:
            conditions['author.slug'] = user_data['author']

        if 'range' in user_data:
            rangeCondition = {}
            return_column = {'creation_date': 1}
            sort = 'creation_date'
            date = 0
            range = user_data['range'].split(':')
            rangeCondition['_id'] = ObjectId(range[0])
            limit = int(range[1])
            data1 = db.entry.find(rangeCondition, return_column)
            for entry in data1:
                date = entry['creation_date']
            conditions['creation_date'] = {'$gt': date}
            data = db.entry.find(conditions).limit(limit).sort(sort)
            entries = {'before': [], 'after': []}
            for entry in data:
                entry = self.prepareEntry(entry, user_data)
                outputEntry = {}
                if (len(return_fields) > 0):
                    if return_fields[0] == '*':
                        outputEntry = entry
                    else:
                        for return_field in return_fields:
                            return_field = return_field.strip()
                            outputEntry[return_field] = entry[return_field]
                else:
                    outputEntry['id'] = entry['id']
                entries['after'].append(outputEntry)
            conditions['creation_date'] = {'$lt': date}
            sort = [('creation_date', -1)]
            data = db.entry.find(conditions).limit(limit).sort(sort)
            for entry in data:
                entry = self.prepareEntry(entry, user_data)
                outputEntry = {}
                if (len(return_fields) > 0):
                    if return_fields[0] == '*':
                        return entry
                    else:
                        for return_field in return_fields:
                            return_field = return_field.strip()
                            if return_field in entry:
                                outputEntry[return_field] = entry[return_field]
                else:
                    outputEntry['id'] = entry['id']
                entries['before'].append(outputEntry)
            return entries
        # offset are expensive operation on IO for large collection
        # Only use when explicitly required
        ####
        if offset > 0:
            if sort and sort[0][0] == '':
                data = db.entry.find(conditions).limit(limit).skip(offset)   # NOQA
            else:
                data = db.entry.find(conditions).sort(sort).limit(limit).skip(offset)   # NOQA
        else:
            if sort and sort[0][0] == 'tags.weight':
                data = list(db.entry.find(conditions))
                data.sort(self.tagWeightSort)
                #no apply limit
            else:
                if sort and sort[0][0] == '':
                    data = db.entry.find(conditions).limit(limit)
                else:
                    data = db.entry.find(conditions).sort(sort).limit(limit)

        entries = []
        if 'count' in user_data:
            count = data.count()
            if int(user_data['count']) == 2:
                entries.append({'count': count})
                return entries
        for entry in data:
            entry = self.prepareEntry(entry, user_data)
            outputEntry = {}
            if (len(return_fields) > 0):
                if return_fields[0] == '*':
                    outputEntry = entry
                else:
                    for return_field in return_fields:
                        return_field = return_field.strip()
                        if return_field in entry:
                            outputEntry[return_field] = entry[return_field]
            else:
                outputEntry['id'] = entry['id']
            entries.append(outputEntry)
        if 'count' in user_data:
            count = data.count()
            if int(user_data['count']) == 1:
                entries.append({'count': count})
        return entries

    #
    #Function is used to prepare sorting of entries according to API specs
    #
    ######################
    def manageSorting(self, sortby, direction):
        """
         Function used to check the sortby and decide the sort query
         TODO: for tag weight we should also support tag slug
        """
        validSortBy = ''
        if sortby == 'creation_date' or sortby == 'publication_date' or sortby == 'modification_date':  # NOQA
            validSortBy = sortby
        elif sortby == 'author':
            validSortBy = 'author.name'
        elif sortby.find('tag') != -1:
            tagArray = sortby.split(':')
            if len(tagArray) == 2:
                self.sortingTagSlug = tagArray[1]
                self.sortingDirection = direction
                validSortBy = 'tags.weight'
        return [(validSortBy, direction)]

    def tagWeightSort(self, doc1, doc2):
        sorttag1 = {}
        sorttag2 = {}
        if 'tags' not in doc1:
            return -(self.sortingDirection)
        if 'tags' not in doc2:
            return self.sortingDirection
        for tag in doc1['tags']:
            if tag['slug'] == self.sortingTagSlug:
                sorttag1 = tag
                break
        for tag in doc2['tags']:
            if tag['slug'] == self.sortingTagSlug:
                sorttag2 = tag
                break
        if len(sorttag1) == 0:
            return -(self.sortingDirection)
        if len(sorttag2) == 0:
            return self.sortingDirection
        if 'slug' in sorttag2 and 'slug' in sorttag1:
            if sorttag1['slug'] == '' or sorttag2['slug'] == '':
                return 0
            if int(sorttag1['weight']) > int(sorttag2['weight']):
                return self.sortingDirection
            else:
                return -(self.sortingDirection)
        else:
            return 0


# This is the entry ponit for entry API.  From here, it is decided from here
# that which method is called according to the requset method.

@app.route('/api/v1/<api_key>/<format>/entry', methods=['GET', 'POST', 'PUT', 'DELETE'])   # NOQA
@requires_auth
def entryHandler(api_key, format):
    if request.method == 'GET':
        resp = entries_get()
        return resp
    elif request.method == 'POST':
        return entries_post()
    elif request.method == 'PUT':
        return entries_put()
    elif request.method == 'DELETE':
        return entries_delete()


 # entries_get
 #
 # This method is called when a get request is made via API. It parses all the
 # parameters passed by user and sends them to the get method for preparing results # NOQA
 # on the basis of conditions.
 # Parameters :
 # offset: the first entry to return (defaults to 1)
 # limit: the number of entries to return (defaults to 1)
 # id=n1,n2,n3: entries whose id matches any in n1,n2,n3...:
 # guid=URI: entries whose guid matches URI
 # tag=t1,t2,t3|t4{schemeURI}[schemeNAME]
 # interval=timestamp1,timestamp2
 # timestamp1 and timestamp 2 must be valid timestamps of the start and ed of the requested date interval, entries falling in the interval will be returned # NOQA
 # enclosures=0, if assigned 0 as value enclosures won't be included in the feed (defaults to 1) # NOQA
 # sort=sortOrder, allows to sort either by any field of entries:
 # date_published, author, date_changed, url, guid, day_parsed
 # the sorting order defaults to ascending, to switch to descending prepend a minus to field name or tag: # NOQA
 # source=string. Allows to load entries of a particular source
 #

def entries_get():
    entry_manager = EntryManager()
    # This dict keeps all the conditions
    user_data = {}
    if(not request.query_string):
        resp = api_response('true', [])
        return resp
    if (request.args.get('id')):
        user_data['id'] = request.args.get('id')
    if (request.args.get('title')):
        user_data['title'] = request.args.get('title')
    if (request.args.get('limit')):
        user_data['limit'] = request.args.get('limit')
    if (request.args.get('status')):
        user_data['status'] = request.args.get('status')
    if (request.args.get('guid')):
        user_data['guid'] = urllib.unquote(request.args.get('guid'))
    if (request.args.get('tags')):
        user_data['tags'] = urllib.unquote(request.args.get('tags'))
    if (request.args.get('interval')):
        user_data['interval'] = urllib.unquote(request.args.get('interval'))
    if (request.args.get('count')):
        user_data['count'] = request.args.get('count')
    if (request.args.get('return_fields')):
        user_data['return_fields'] = urllib.unquote(request.args.get('return_fields'))   # NOQA
    if (request.args.get('sort')):
        user_data['sort'] = request.args.get('sort')
    if (request.args.get('enclosures')):
        user_data['enclosures'] = request.args.get('enclosures')
    if (request.args.get('author')):
        user_data['author'] = request.args.get('author')
    if (request.args.get('offset')):
        user_data['offset'] = request.args.get('offset')
    if (request.args.get('count')):
        user_data['count'] = request.args.get('count')
    if (request.args.get('return_content')):
        user_data['return_content'] = urllib.unquote(request.args.get('return_content'))   # NOQA
    if (request.args.get('range')):
        user_data['range'] = urllib.unquote(request.args.get('range'))
    if (request.args.get('related')):
        user_data['related'] = request.args.get('related')
    if (request.args.get('source')):
        user_data['source'] = request.args.get('source')
    entries = entry_manager.get(user_data)
    resp = api_response('true', entries)
    return resp

 # entries_post
 #
 # This method is called when a POST request is made via API.
 # Parameters :
 # GUID: String Can be a URI
 # status: active|deleted|hidden|draft
 # source: string not mandatory
 # links: Type
 #          Format
 #          URI
 # related
 #   Type
 #   id
 # publication_date date time
 # title String
 # author
 #    Name
 #    Slug
 # content content is a mandatory element
 # tags
 #   scheme tag name (string), tag slug (sanitized string), tag value (integer)
 # longitude float
 # latitude  float
 # publication_date datetime
 # modification_date datetime
 # return_fields comma separated name of fields


def entries_post():
    entry_manager = EntryManager()
    entry_data = {}
    error_code = ''
    #content is mandatory. If not sent , return an error message
    entry = json.loads(request.form['entry'])
    if 'content' not in entry:
        error_code = error_codes.CONTENT_IS_MANDATORY
        data = {'message': error_code}
        resp = api_response('true', data)
        return resp
    else:
        entry_data['content'] = entry['content']
    if ('creation_date' in entry):
        entry_data['creation_date'] = entry['creation_date']
    if 'publication_date' in entry:
        entry_data['publication_date'] = entry['publication_date']
    if 'modification_date' in entry:
        entry_data['modification_date'] = entry['modification_date']
    if ('author' in entry):
        author_info = {}
        if ('name' in entry['author']):
            if(isinstance(entry['author']['name'], basestring)):
                author_info['name'] = entry["author"]["name"]
            else:
                error_code = error_codes.INVALID_AUTHOR_NAME
        if ('slug' in entry['author']):
            if(isinstance(entry['author']['slug'], basestring)):
                author_info['slug'] = entry["author"]["slug"]
            else:
                error_code = error_codes.INVALID_AUTHOR_SLUG
        entry_data['author'] = author_info
    if ('tags' in entry):
        entry_data['tags'] = []
        for tag in entry['tags']:
            tags = {}
            if ('name' in tag):
                if(isinstance(tag['name'], basestring)):
                    tags['name'] = tag["name"]
                else:
                    error_code = error_codes.INVALID_TAG_NAME
            if ('slug' in tag):
                if(isinstance(tag['slug'], basestring)):
                    tags['slug'] = tag["slug"]
                else:
                    error_code = error_codes.INVALID_TAG_SLUG
            if ('scheme_name' in tags):
                if(isinstance(tag['scheme_name'], basestring)):
                    tags['scheme_name'] = tag["scheme_name"]
            if ('scheme' in tag):
                if(isinstance(tag['scheme'], basestring)):
                    tags['scheme'] = tag["scheme"]
                else:
                    error_code = error_codes.INVALID_TAG_SCHEME
            if ('weight' in tag):
                tags['weight'] = tag["weight"]
            entry_data['tags'].append(tags)
    if ('guid' in entry):
        if(isinstance(entry['guid'], basestring)):
            entry_data['guid'] = entry['guid']
        else:
            error_code = error_codes.INVALID_GUID
    if ('title' in entry):
        if(isinstance(entry['title'], basestring)):
            entry_data['title'] = entry['title']
        else:
            error_code = error_codes.INVALID_TITLE
    if ('status' in entry):
        if(isinstance(entry['status'], basestring)):
            entry_data['status'] = entry['status']
        else:
            error_code = error_codes.INVALID_STATUS
    if ('links' in entry):
        entry_data['links'] = []
        alternates = []
        enclosures = []
        if 'enclosures' in entry['links']:
            for enclosur in entry['links']['enclosures']:
                enclosure = {}
                enclosure['type'] = enclosur['type']
                enclosure['uri'] = enclosur['uri']
                enclosures.append(enclosure)
        if 'alternates' in entry['links']:
            for alternat in entry['links']['alternates']:
                alternate = {}
                alternate['type'] = alternat['type']
                alternate['uri'] = alternat['uri']
                alternates.append(alternate)
        entry_data['links'] = {'alternates': alternates, 'enclosures': enclosures}  # NOQA
    if ('latitude' in entry):
        if(isinstance(entry['latitude'], float)):
            entry_data['latitude'] = entry['latitude']
    if ('longitude' in entry):
        if(isinstance(entry['longitude'], float)):
            entry_data['longitude'] = entry['longitude']
    if ('related' in entry):
        related = {}
        if 'type' in entry['related']:
            related['type'] = entry["related"]["type"]
        if 'id' in entry['related']:
            related['id'] = entry['related']['id']
        entry_data['related'] = related
    if ('source' in entry):
        if(isinstance(entry['source'], basestring)):
            entry_data['source'] = entry['source']
        else:
            entry_data['source'] = ''
    if (error_code != ''):
        data = {'message': error_code}
        resp = api_response('true', data)
        return resp
    else:
        response = entry_manager.save(entry_data)
        resp = api_response('true', response)
        return resp

 # entries_put
 #
 # This method is called when a PUT request is made via API.
 # Parameters :
 # status: active|deleted|hidden|draft
 # source: Source in not supported in put API, as it does not make sense to
 #         update source info
 # links: Type
 #          Format
 #          URI
 # related
 #   Type
 #   id
 # publication_date date time
 # title String
 # author
 #    Name
 #    Slug
 # content content is a mandatory element
 # tags
 #   scheme tag name (string), tag slug (sanitized string), tag value (integer)
 # longitude float
 # latitude  float
 # return_fields comma separated name of fields


def entries_put():
    entry_manager = EntryManager()
    entry_data = {}
    entry = json.loads(request.form['entry'])
    if 'id' not in entry:
        error_code = error_codes.ID_IS_MANDATORY
        data = {'message': error_code}
        resp = api_response('true', data)
        return resp
    else:
        entry_data['_id'] = entry['id']
    if ('author' in entry):
        if ('name' in entry['author']):
            if(isinstance(entry['author']['name'], basestring)):
                entry_data['author.name'] = entry['author']['name']
            else:
                error_code = error_codes.INVALID_AUTHOR_NAME
        if ('slug' in entry['author']):
            if(isinstance(entry['author']['slug'], basestring)):
                entry_data['author.slug'] = entry['author']['slug']
            else:
                error_code = error_codes.INVALID_AUTHOR_SLUG
    if ('title' in entry):
        if(isinstance(entry['title'], basestring)):
            entry_data['title'] = entry['title']
        else:
            error_code = error_codes.INVALID_TITLE
    if ('status' in entry):
        if(isinstance(entry['status'], basestring)):
            entry_data['status'] = entry['status']
        else:
            error_code = error_codes.INVALID_STATUS
    if ('tags' in entry):
        existing_tags = entry_manager.getTagsOfEntry(entry_data['_id'])
        removed_tags = []
        entry_data['tags'] = []
        for tag in entry['tags']:
            tags = {}
            if ('name' in tag):
                if(isinstance(tag['name'], basestring)):
                    tags['name'] = tag["name"]
                else:
                    error_code = error_codes.INVALID_TAG_NAME
            if ('slug' in tag):
                if(isinstance(tag['slug'], basestring)):
                    tags['slug'] = tag["slug"]
                else:
                    error_code = error_codes.INVALID_TAG_SLUG
            if ('scheme_name' in tags):
                if(isinstance(tag['scheme_name'], basestring)):
                    tags['scheme_name'] = tag["scheme_name"]
            if ('scheme' in tag):
                if(isinstance(tag['scheme'], basestring)):
                    tags['scheme'] = tag["scheme"]
                else:
                    error_code = error_codes.INVALID_TAG_SCHEME
            if ('weight' in tag):
                tags['weight'] = tag["weight"]
            entry_data['tags'].append(tags)
        for tag in existing_tags:
            removed_tags.append(tag)
            for i in entry_data['tags']:
                if tag == i['slug']:
                    removed_tags.remove(tag)
                    break
        entry_data['removed_tags'] = removed_tags
    if ('links' in entry):
        entry_data['links'] = []
        alternates = []
        enclosures = []
        if 'enclosures' in entry['links']:
            for enclosur in entry['links']['enclosures']:
                enclosure = {}
                enclosure['type'] = enclosur['type']
                enclosure['uri'] = enclosur['uri']
                enclosures.append(enclosure)
        if 'alternates' in entry['links']:
            for alternat in entry['links']['alternates']:
                alternate = {}
                alternate['type'] = alternat['type']
                alternate['uri'] = alternat['uri']
                alternates.append(alternate)
        entry_data['links'] = {'alternates': alternates, 'enclosures': enclosures}  # NOQA
    if ('latitude' in entry):
        if(isinstance(entry['latitude'], float)):
            entry_data['latitude'] = entry['latitude']
    if('longitude' in entry):
        if(isinstance(entry['longitude'], float)):
            entry_data['longitude'] = entry['longitude']
    if ('related' in entry):
        related = {}
        if 'type' in entry['related']:
            related['type'] = entry["related"]["type"]
        if 'id' in entry['related']:
            related['id'] = entry['related']['id']
        entry_data['related'] = related
    if 'content' in entry:
        entry_data['content'] = entry['content']
    response = entry_manager.update(entry_data)
    resp = api_response('true', response)
    return resp


# entreis_delete
#
# This method is used to delete an entry
#
# _id: String
#
#returns a success message
#########################################################################
def entries_delete():
    entry_manager = EntryManager()
    entry = json.loads(request.data)
    if 'id' not in entry and 'related' not in entry:
        error_code = error_codes.ID_IS_MANDATORY
        data = {'message': error_code}
        resp = api_response('false', data)
        return resp
    if 'id' in entry:
        response = entry_manager.delete(entry['id'])
    if 'related' in entry:
        response = entry_manager.deleteByRelated(entry['related'])
    resp = api_response('true', response)
    return resp
