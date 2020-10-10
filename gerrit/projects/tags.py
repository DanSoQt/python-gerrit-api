#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.utils.exceptions import UnknownTag
from gerrit.utils.common import check


class Tag:
    def __init__(self, project, json, gerrit):
        self.project = project
        self.json = json
        self.gerrit = gerrit

        self.ref = None
        self.name = None
        self.object = None
        self.message = None
        self.revision = None
        self.tagger = None

        if self.json is not None:
            self.__load__()

    def __repr__(self):
        return '%s(%s=%s)' % (self.__class__.__name__, 'ref', self.ref)

    def __load__(self):
        self.ref = self.json.get('ref')
        self.name = self.ref.replace('refs/heads/', '')
        self.object = self.json.get('object')
        self.message = self.json.get('message')
        self.revision = self.json.get('revision')
        self.tagger = self.json.get('tagger', {})


class Tags:
    def __init__(self, project, gerrit):
        self.project = project
        self.gerrit = gerrit
        self._data = self.poll()

    def poll(self):
        """

        :return:
        """
        endpoint = '/projects/%s/tags/' % self.project
        response = self.gerrit.make_call('get', endpoint)
        result = self.gerrit.decode_response(response)
        return result

    def iterkeys(self):
        """
        Iterate over the names of all available tags
        """
        for row in self._data:
            yield row['ref']

    def keys(self):
        """
        Return a list of the names of all tags
        """
        return list(self.iterkeys())

    def __len__(self):
        """

        :return:
        """
        return len(self.keys())

    def __contains__(self, ref):
        """
        True if ref exists in project
        """
        return ref in self.keys()

    def __getitem__(self, ref):
        """
        get a tag by ref

        :param ref:
        :return:
        """
        result = [row for row in self._data if row['ref'] == ref]
        if result:
            ref_date = result[0]
            return Tag(project=self.project, json=ref_date, gerrit=self.gerrit)
        else:
            raise UnknownTag(ref)

    def __setitem__(self, key, value):
        """
        create a tag by ref
        :param key:
        :param value:
        :return:
        """
        return self.create(key.replace('refs/tags/', ''), value)

    def __delitem__(self, key):
        """
        Delete a tag by ref

        :param key:
        :return:
        """
        return self.delete(key.replace('refs/tags/', ''))

    def __iter__(self):
        """

        :return:
        """
        for row in self._data:
            yield Tag(project=self.project, json=row, gerrit=self.gerrit)

    @check
    def create(self, name: str, TagInput: dict) -> Tag:
        """
        Creates a new tag on the project.

        :param name: the tag name
        :param TagInput: the TagInput entity
        :return:
        """
        ref = 'refs/tags/' + name
        if ref in self.keys():
            return self[ref]

        endpoint = '/projects/%s/tags/%s' % (self.project, name)
        response = self.gerrit.make_call('put', endpoint, **TagInput)
        result = self.gerrit.decode_response(response)
        return Tag(project=self.project, json=result, gerrit=self.gerrit)

    def delete(self, name):
        """
        Delete a tag.

        :param name: the tag name
        :return:
        """
        endpoint = '/projects/%s/tags/%s' % (self.project, name)
        self.gerrit.make_call('delete', endpoint)