"""
Custom DRF request parsers.  These can be used by views to handle different
content types, as specified by `<Parser>.media_type`.

To use these in an APIView, set `<View>.parser_classes` to a list including the
desired parsers.  See http://www.django-rest-framework.org/api-guide/parsers/
for details.
"""

from rest_framework.exceptions import ParseError, UnsupportedMediaType
from rest_framework.parsers import FileUploadParser, JSONParser


class TypedFileUploadParser(FileUploadParser):
    """
    Handles upload of files, ensuring that the media type is supported, and
    that the uploaded filename matches the Content-type.

    Requirements:
        * The view must have a View.supported_media_types attribute whose keys
          are the mimetypes of the supported media formats, and whose values
          are lists of acceptable file extensions for each content type.

          Example:

              supported_media_types = {'image/jpeg': ['.jpeg', '.jpg']}

        * Content-type must be set to a supported type (as
          defined in View.supported_media_types above).

          Example:

              Content-type: image/jpeg

        * Content-disposition must include a filename with a valid extension
          for the specified Content-type.

          Example:

              Content-disposition: attachment; filename="profile.jpg"
    """

    media_type = '*/*'

    # TODO: Consider getting file extensions from an authoritative source.
    # http://www.stdicon.com/mimetypes is one option, but it assumes one
    # mimetype per extension, and image/pjpeg (for example) is not listed.

    file_extensions = {
        'image/gif': ['.gif'],
        'image/jpeg': ['.jpeg', '.jpg'],
        'image/pjpeg': ['.jpeg', '.jpg'],
        'image/png': ['.png'],
        'image/svg': ['.svg'],
    }

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parse the request, returning a DataAndFiles object with the data dict
        left empty, and the body of the request placed in files['file'].
        """

        supported_media_types = getattr(parser_context['view'], 'upload_media_types', None)
        if supported_media_types is not None and media_type not in supported_media_types:
            raise UnsupportedMediaType(media_type)

        filename = self.get_filename(stream, media_type, parser_context)
        if media_type in self.file_extensions:
            ext = '.{}'.format(filename.rsplit('.', 1)[1])
            if ext.lower() not in self.file_extensions[media_type]:
                msg = "Filename does not match requested content-type. Filename: {}, Content-type: {}"
                raise ParseError(msg.format(filename, media_type))
        return super(TypedFileUploadParser, self).parse(stream, media_type, parser_context)


class MergePatchParser(JSONParser):
    """
    Custom parser to be used with the "merge patch" implementation (https://tools.ietf.org/html/rfc7396).
    """
    media_type = 'application/merge-patch+json'
