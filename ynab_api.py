#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ynab_api

YNAB API class for use with YNAB tools
"""

import sys
import os
import argparse
import json
import datetime

import requests
import yaml

API_PREFIX = 'https://api.youneedabudget.com/v1'

class YNABAPIError(Exception):
    """ Used for exceptions specific to this script """

    pass


class YNABAPI:
    def __init__(self, credentials_filename):
        self.__setup_ynab(credentials_filename)
        self.__get_ynab_budget_id('My Budget')
        self.__get_ynab_budget_categories()
        self.__remove_hidden_categories()
        self.__remove_unused_category_groups()

    def __setup_ynab(self, credentials_filename):
        """ Get the user's credentials """

        #self.headers = dict()

        self.headers = {'Content-Type': 'application/json'}

        try:
            with open(os.path.expanduser(credentials_filename)) as cfile:
                credentials = json.load(cfile)

            self.headers['Authorization'] = credentials['prefix'] + ' ' + credentials['key']
        except IOError as err:
            raise YNABAPIError('Unable to open credentials file:\n{}'\
                                    .format(err))
        except json.JSONDecodeError:
            raise YNABAPIError('Unable to parse credentials file {}'\
                                    .format(credentials_filename))
        except KeyError as err:
            raise YNABAPIError('Expected key {} not found in credentials '\
                                    'file {}'.format(err, credentials_filename))


    def __check_api_result(self, result):
        """ Check the validity of the result of the API request """

        data = result.json()

        if not result.ok:
            raise YNABAPIError('Request Error: {} {}:{}'.format(result.status_code, 
                                                                       data['error']['name'],
                                                                       data['error']['detail']))

        return data

    
    def api_get(self, url):
        """ Get request from the YNAB API """

        try:
            result = requests.get(API_PREFIX + url, headers=self.headers)
        except requests.exceptions.RequestException as err:
            raise YNABAPIError('YNAB API error:\n{}'.format(err))

        return self.__check_api_result(result)


    def api_patch(self, url, data):
        """ Send patch request to the YNAB API """

        try:
            result =  requests.patch(API_PREFIX + url, json.dumps(data), headers=self.headers)
        except requests.exceptions.RequestException as err:
            raise YNABAPIError('YNAB API error:\n{}'.format(err))

        return self.__check_api_result(result)

    def __get_ynab_budget_id(self, name):
        """ Get the API id for the named budget """

        budget_summary = self.api_get('/budgets')

        # Find the named budget and retur the ID
        for budget in budget_summary['data']['budgets']:
            if budget['name'] == name:
                self.budget_id = budget['id']
                return

        # If we get here, the budget wasn't found
        raise YNABAPIError("Budget '{}' not found".format(name))


    def __get_ynab_budget_categories(self):
        """ Get the catagory names from the budget """

        categories_response = self.api_get('/budgets/{}/categories'.format(self.budget_id))

        self.category_groups = categories_response['data']['category_groups']

        self.category_ids = dict()
        for group in self.category_groups:
            for category in group['categories']:
                self.category_ids[category['name']] = category['id']


    def __remove_hidden_categories(self):
        for group in self.category_groups:
            group['categories'] = list(filter(lambda x: not x['hidden'], group['categories']))


    @staticmethod
    def __valid_category_group(group):
        #return group.categories and group.name != 'Internal Master Category'
        return len(group['categories'])


    def __remove_unused_category_groups(self):
        self.category_groups = list(filter(YNABAPI.__valid_category_group, self.category_groups))
