from rest_framework.compat import INDENT_SEPARATORS, LONG_SEPARATORS, SHORT_SEPARATORS
from rest_framework.renderers import JSONRenderer
from rest_framework.utils import json


class PotokJSONRenderer(JSONRenderer):
    """
        Renderer which serializes to JSON.

        Modification of JSONRenderer
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `data` into JSON, returning a bytestring.
        """
        if data is None:
            return b''

        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)

        if indent is None:
            separators = SHORT_SEPARATORS if self.compact else LONG_SEPARATORS
        else:
            separators = INDENT_SEPARATORS

        status_code = renderer_context["response"].status_code

        response = {
            "status": status_code,
        }

        for exception_header in ["detail", "non_field_errors"]:
            if exception_header in data:
                response["detail"] = data[exception_header]
                del data[exception_header]

        response["content"] = data or None

        ret = json.dumps(
            response, cls=self.encoder_class,
            indent=indent, ensure_ascii=self.ensure_ascii,
            allow_nan=not self.strict, separators=separators
        )

        # We always fully escape \u2028 and \u2029 to ensure we output JSON
        # that is a strict javascript subset.
        # See: http://timelessrepo.com/json-isnt-a-javascript-subset
        ret = ret.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
        return ret.encode()


def prerender_data(content=None, message=None):
    return {
        "content": content,
        "message": message,
    }
