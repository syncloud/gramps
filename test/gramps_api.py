import time

import requests


class GrampsApi:
    def __init__(self, app_domain, user, password):
        self.url = 'https://{0}/api'.format(app_domain)
        self.user = user
        self.password = password
        self.access_token = None

    def token(self):
        for attempt in range(20):
            response = requests.post('{0}/token/'.format(self.url),
                                     json={'username': self.user, 'password': self.password}, verify=False)
            if response.status_code != 429:
                break
            time.sleep(5)
        assert response.status_code == 200, response.text
        self.access_token = response.json()['access_token']
        return self.access_token

    def request(self, method, path, **kwargs):
        if not self.access_token:
            self.token()
        for attempt in range(20):
            headers = {'Authorization': 'Bearer {0}'.format(self.access_token)}
            response = requests.request(method, '{0}{1}'.format(self.url, path), headers=headers, verify=False, **kwargs)
            if response.status_code in (401, 422):
                self.token()
            elif response.status_code == 429:
                time.sleep(5)
            else:
                return response
        return response

    def people_count(self):
        response = self.request('GET', '/metadata/')
        assert response.status_code == 200, response.text
        return response.json()['object_counts']['people']

    def add_person(self, first_name, surname):
        person = {
            '_class': 'Person',
            'primary_name': {
                '_class': 'Name',
                'first_name': first_name,
                'surname_list': [{'_class': 'Surname', 'surname': surname}],
            },
        }
        response = self.request('POST', '/people/', json=person)
        assert response.status_code == 201, response.text
