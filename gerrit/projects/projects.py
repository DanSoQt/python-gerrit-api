#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.projects.project import GerritProject
from gerrit.utils.common import check
from gerrit.utils.exceptions import UnknownProject


class GerritProjects:
    def __init__(self, gerrit):
        self.gerrit = gerrit

    def list(self) -> list:
        """
        Lists the projects accessible by the caller.

        :return:
        """
        endpoint = '/projects/?all'
        response = self.gerrit.make_call('get', endpoint)
        result = self.gerrit.decode_response(response)
        return GerritProject.parse_list(list(result.values()), gerrit=self.gerrit)

    def search(self, query: str) -> list:
        """
        Queries projects visible to the caller. The query string must be provided by the query parameter.
        The start and limit parameters can be used to skip/limit results.

        query parameter
          * name:'NAME' Matches projects that have exactly the name 'NAME'.
          * parent:'PARENT' Matches projects that have 'PARENT' as parent project.
          * inname:'NAME' Matches projects that a name part that starts with 'NAME' (case insensitive).
          * description:'DESCRIPTION' Matches projects whose description contains 'DESCRIPTION', using a full-text search.
          * state:'STATE' Matches project’s state. Can be either 'active' or 'read-only'.

        :param query:
        :return:
        """
        endpoint = '/projects/?query=%s' % query
        response = self.gerrit.make_call('get', endpoint)
        result = self.gerrit.decode_response(response)
        return GerritProject.parse_list(result, gerrit=self.gerrit)

    def get(self, project_name: str) -> GerritProject:
        """
        Retrieves a project.

        :param project_name: the name of the project
        :return:
        """
        endpoint = '/projects/%s' % project_name
        response = self.gerrit.make_call('get', endpoint)

        if response.status_code < 300:
            result = self.gerrit.decode_response(response)
            return GerritProject.parse(result, gerrit=self.gerrit)
        else:
            raise UnknownProject(project_name)

    @check
    def create(self, project_name: str, ProjectInput: dict) -> GerritProject:
        """
        Creates a new project.

        :param project_name: the name of the project
        :param ProjectInput: the ProjectInput entity
        :return:
        """
        endpoint = '/projects/%s' % project_name
        response = self.gerrit.make_call('put', endpoint, **ProjectInput)
        result = self.gerrit.decode_response(response)
        return GerritProject(json=result, gerrit=self.gerrit)
