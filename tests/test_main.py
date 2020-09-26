from unittest import TestCase

from src.main import SearchDocModule


class TestMain(TestCase):
    def test_check_str_false(self):
        result = SearchDocModule(1).check_str()
        self.assertEqual(result, False)

    def test_check_str_true(self):
        result = SearchDocModule("1").check_str()
        self.assertEqual(result, True)

    def test_check_doc_url_404(self):
        response = SearchDocModule("none").check_doc_url()
        self.assertEqual(response.status_code, 404)

    def test_check_doc_url_200(self):
        response = SearchDocModule("abc").check_doc_url()
        self.assertEqual(response.status_code, 200)

    def test_main_failure(self):
        result = SearchDocModule(1).main()
        self.assertEqual(result, "NG")

    def test_main_success(self):
        result = SearchDocModule("abc").main()
        self.assertEqual(result, "OK")
