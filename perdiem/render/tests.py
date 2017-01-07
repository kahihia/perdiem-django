import json

from django.test import TestCase, TransactionTestCase

from rest_framework import status

from render.url.utils import add_params_to_url


class RenderTestCaseMixin(object):

    @staticmethod
    def strip_query_params(url):
        return url.split('?')[0]

    def assertResponseRenders(self, url, status_code=200, method='GET', data={}, has_form_error=False, **kwargs):
        request_method = getattr(self.client, method.lower())
        follow = status_code == 302
        response = request_method(url, data=data, follow=follow, **kwargs)

        if status_code == 302:
            redirect_url, response_status_code = response.redirect_chain[0]
        else:
            response_status_code = response.status_code
        self.assertEquals(
            response_status_code,
            status_code,
            "URL {url} returned with status code {actual_status} when {expected_status} was expected.".format(
                url=url,
                actual_status=response_status_code,
                expected_status=status_code
            )
        )

        # Check that forms submitted did not return errors (or did if it should have)
        form_error_assertion_method = self.assertIn if has_form_error else self.assertNotIn
        form_error_assertion_method('errorlist', response.content)

        return response

    def assertAPIResponseRenders(self, url, status_code=200, method='GET', data={}, **kwargs):
        api_url = add_params_to_url(url, {'format': 'json'})
        if data:
            data = json.dumps(data)
        response = self.assertResponseRenders(
            api_url,
            status_code=status_code,
            method=method,
            data=data,
            content_type='application/json',
            **kwargs
        )
        if status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_205_RESET_CONTENT]:
            return response
        return response.json()

    def assertResponseRedirects(self, url, redirect_url, status_code=200, method='GET', data={}, **kwargs):
        response = self.assertResponseRenders(url, status_code=302, method=method, data=data, **kwargs)
        redirect_url_from_response, _ = response.redirect_chain[0]
        self.assertEquals(self.strip_query_params(redirect_url_from_response), redirect_url)
        self.assertEquals(response.status_code, status_code)

    def get200s(self):
        return []

    def testRender200s(self):
        for url in self.get200s():
            self.assertResponseRenders(url)


class RenderTestCase(TestCase, RenderTestCaseMixin):
    pass


class RenderTransactionTestCase(TransactionTestCase, RenderTestCaseMixin):
    pass
