"""
TestCases verifying proper behavior of custom DRF request parsers.
"""

from collections import namedtuple
from io import BytesIO

from rest_framework import exceptions
from rest_framework.test import APITestCase, APIRequestFactory

from openedx.core.lib.api import parsers


class TestTypedFileUploadParser(APITestCase):
    """
    Tests that verify the behavior of TypedFileUploadParser
    """
    def setUp(self):
        super(TestTypedFileUploadParser, self).setUp()
        self.parser = parsers.TypedFileUploadParser()
        self.request_factory = APIRequestFactory()
        upload_media_types = {'image/png', 'image/jpeg', 'application/octet-stream'}
        self.view = namedtuple('view', ('upload_media_types',))(upload_media_types)

    def test_parse_supported_type(self):
        """
        Test that TypedFileUploadParser returns empty data and content stored in
        files['file'].
        """
        request = self.request_factory.post(
            '/',
            content_type='image/png',
            HTTP_CONTENT_DISPOSITION='attachment; filename="file.PNG"',
        )
        context = {'view': self.view, 'request': request}
        result = self.parser.parse(stream=BytesIO('abcdefgh'), media_type='image/png', parser_context=context)
        self.assertEqual(result.data, {})
        self.assertIn('file', result.files)
        self.assertEqual(result.files['file'].read(), 'abcdefgh')

    def test_parse_unsupported_type(self):
        """
        Test that TypedFileUploadParser raises an exception when parsing an
        unsupported image format.
        """
        request = self.request_factory.post(
            '/',
            content_type='image/tiff',
            HTTP_CONTENT_DISPOSITION='attachment; filename="file.tiff"',
        )
        context = {'view': self.view, 'request': request}
        with self.assertRaises(exceptions.UnsupportedMediaType):
            self.parser.parse(stream=BytesIO('abcdefgh'), media_type='image/tiff', parser_context=context)

    def test_parse_unconstrained_type(self):
        """
        Test that TypedFileUploader allows any extension for mimetypes without
        specified extensions
        """
        request = self.request_factory.post(
            '/',
            content_type='application/octet-stream',
            HTTP_CONTENT_DISPOSITION='attachment; filename="VIRUS.EXE',
        )
        context = {'view': self.view, 'request': request}
        result = self.parser.parse(
            stream=BytesIO('abcdefgh'), media_type='application/octet-stream', parser_context=context
        )
        self.assertEqual(result.data, {})
        self.assertIn('file', result.files)
        self.assertEqual(result.files['file'].read(), 'abcdefgh')

    def test_parse_mismatched_filename_and_mimetype(self):
        """
        Test that TypedFileUploadParser raises an exception when the specified
        content-type doesn't match the filename extension in the
        content-disposition header.
        """
        request = self.request_factory.post(
            '/',
            content_type='image/png',
            HTTP_CONTENT_DISPOSITION='attachment; filename="file.jpg"',
        )
        context = {'view': self.view, 'request': request}
        with self.assertRaises(exceptions.ParseError) as err:
            self.parser.parse(stream=BytesIO('abcdefgh'), media_type='image/png', parser_context=context)
            self.assertIn('developer_message', err.detail)
            self.assertNotIn('user_message', err.detail)

    def test_parse_any_type(self):
        """
        The view does not have to specify supported types.
        """
        view = object()
        self.assertFalse(hasattr(view, 'upload_media_types'))

        request = self.request_factory.post(
            '/',
            content_type='image/png',
            HTTP_CONTENT_DISPOSITION='attachment; filename="file.png"',
        )
        context = {'view': view, 'request': request}
        result = self.parser.parse(stream=BytesIO('abcdefgh'), media_type='image/png', parser_context=context)
        self.assertEqual(result.data, {})
        self.assertIn('file', result.files)
        self.assertEqual(result.files['file'].read(), 'abcdefgh')

    def test_parse_any_type_with_mismatched_extension(self):
        """
        When the view doesn't specify a set of supported types, the
        TypedFileUploadParser will still check that the extension
        and content-type match.
        """
        view = object()
        self.assertFalse(hasattr(view, 'upload_media_types'))
        request = self.request_factory.post(
            '/',
            content_type='image/png',
            HTTP_CONTENT_DISPOSITION='attachment; filename="file.jpg"',
        )
        context = {'view': view, 'request': request}
        with self.assertRaises(exceptions.ParseError):
            self.parser.parse(stream=BytesIO('abcdefgh'), media_type='image/png', parser_context=context)

    def test_parse_all_types_with_unknown_type(self):
        """
        If the view doesn't specify the set of supported types,
        and the content-type is unknown, accept any file extension.
        """
        view = object()
        self.assertFalse(hasattr(view, 'upload_media_types'))
        request = self.request_factory.post(
            '/',
            content_type='application/json',
            HTTP_CONTENT_DISPOSITION='attachment; filename="file.xyz"',
        )
        context = {'view': view, 'request': request}
        result = self.parser.parse(stream=BytesIO('abcdefgh'), media_type='application/json', parser_context=context)
        self.assertNotIn('application/json', self.parser.file_extensions)
        self.assertEqual(result.data, {})
        self.assertIn('file', result.files)
        self.assertEqual(result.files['file'].read(), 'abcdefgh')
