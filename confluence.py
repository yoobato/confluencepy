import requests

REQUEST_TIMEOUT_IN_SECS = 10


class Confluence:
    '''A class holds many methods which send HTTP requests to Confluence and return the response.

    Args:
        base_url (str): Confluence Base URL
        account (str, str): Confluence Account(ID, PW)
    
    Attributes:
        _api_base_url (str) : Confluence REST API Base URL (concat with base_url argument)
        _session (requests.Session): Authenticaed Confluence Sesison using HTTP Basic Authentication
    '''

    def __init__(self, base_url: str, account: tuple[str, str]):
        self._api_base_url = base_url + '/rest/api'

        self._session = requests.Session()
        self._session.auth = account


    def get_pages(self, space_key: str) -> list:
        '''Get all Confluence pages in the given space

        Args:
            space_key (str): Space's key where pages belong

        Returns:
            list: Pages
        '''

        results = []
        start_index = 0

        while True:
            params = {
                'spaceKey' : space_key,
                'type': 'page',
                'limit': 25,
                'start': start_index
            }

            response = self._session.get(
                f'{self._api_base_url}/content', 
                params=params, 
                timeout=REQUEST_TIMEOUT_IN_SECS).json()
            if response['size'] == 0:
                break

            results.extend(list(response['results']))

            start_index = int(response['start']) + int(response['size'])

        return results


    def get_content(self, content_id: str) -> dict:
        '''Get a Confluence content bt the given Content ID

        Args:
            content_id (str): Content's ID to fetch
        
        Returns:
            dict: Content
        '''

        return self._session.get(
            f'{self._api_base_url}/content/{content_id}',
            timeout=REQUEST_TIMEOUT_IN_SECS).json()


    def create_page(self,
                    space_key: str,
                    title: str,
                    body: str,
                    parent_page_id: str = None) -> dict:
        '''Create a new Confluence page

        Args:
            space_key (str): Space's key where page will be created
            title (str): Page title (must UNIQUE in a space)
            body (str): Storage Formatted Body
            parent_page_id (str): (Optional) Parent page's ID
                                  (new page will be child of the parent page)
        
        Returns:
            dict: Newly created content
        '''

        req_data = {
            'space': { 'key': space_key },
            'type': 'page',
            'title': title,
            'body': {
                'storage': {
                    'value': body,
                    'representation': 'storage'
                }
            }
        }
        if parent_page_id:
            req_data['ancestors'] = []
            req_data['ancestors'].append({ 'id': parent_page_id })

        return self._session.post(
            f'{self._api_base_url}/content',
            json=req_data,
            timeout=REQUEST_TIMEOUT_IN_SECS).json()

