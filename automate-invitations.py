#!/usr/bin/env python

"""
Accept Github repository invitations if the target repositories
are listed in a whitelist file.

This whitelist file should be yaml file with a top-level array as follows:

    - org1/repo1
    - org1/repo2
    - ...

"""

import os
import sys
import logging
import argparse

import yaml
import requests

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


class GHApi(object):
    """
    Wrapper around requests lib to interface with Github
    """

    """Github base API url"""
    BASE_URL = "https://api.github.com"

    def __init__(self, token):
        self.auth_header = {'Authorization': 'token %s' % (token,)}

    def get_invitations(self):
        """
        Retrieves repository invitations

        It follows pagination and returns invitations in a list.
        """

        return self.__get_follow(self.__url('/user/repository_invitations'))

    def accept_invitation(self, invitation_id):
        """
        Accepts a repository invitation
        """

        url = self.__url('/user/repository_invitations/', invitation_id)
        return self.__patch(url)

    def __url(self, *els):
        """
        Helper method to build the Github API url

        Returns a string
        """

        urls = [str(el) for el in els]
        urls.insert(0, self.BASE_URL)

        return '/'.join(s.strip('/') for s in urls)

    def __get(self, url):
        """Calls requests.get with proper authentication"""

        res = requests.get(url, headers=self.auth_header)
        res.raise_for_status()
        return res

    def __patch(self, url):
        """Calls requests.patch with proper authentication"""

        res = requests.patch(url, headers=self.auth_header)
        res.raise_for_status()
        return res

    def __get_follow(self, url):
        """Calls requests.get and follows any pagination links"""

        res = self.__get(url)
        result = res.json()

        if not isinstance(result, list):
            return result

        elements = [element for element in result]

        while 'last' in res.links and 'next' in res.links \
                and res.links['last']['url'] != res.links['next']['url']:

            req_url = res.links['next']['url']
            res = self.__get(req_url)

            for element in res.json():
                elements.append(element)

        return elements


def main():
    try:
        g = GHApi(os.environ['GH_TOKEN'])
    except KeyError:
        print >>sys.stderr, "Please export 'GH_TOKEN' variable."
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description='Accept whitelisted invitations')

    parser.add_argument('-l', '--list', dest='list', required=True,
                        help='Yaml file with the whitelisted repos')

    args = parser.parse_args()

    with open(args.list, 'r') as f:
        whitelisted_repos = yaml.safe_load(f.read())

    for invitation in g.get_invitations():
        invitation_id = invitation["id"]
        repo = invitation["repository"]["full_name"]
        inviter = invitation["inviter"]["login"]

        if repo in whitelisted_repos:
            logging.info(['Accepting', repo, inviter, invitation_id])
            g.accept_invitation(invitation_id)
        else:
            logging.info(['Ignoring', repo, inviter, invitation_id])


if __name__ == '__main__':
    main()
