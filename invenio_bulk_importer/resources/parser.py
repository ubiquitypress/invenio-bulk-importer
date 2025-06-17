from flask import request


class RequestFileNameAndStreamParser:
    """Parse the request body."""

    def parse(self):
        """Parse the request body."""
        return {
            "request_filename": request.headers.get('X-Filename'),
            "request_stream": request.stream,
            "request_content_length": request.content_length,
        }
