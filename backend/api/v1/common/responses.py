"""
Shared response serializers for OpenAPI schema annotation.

These describe the response envelopes that recur across the v1 API. They exist
so that ``@extend_schema(responses=...)`` can point at a named component rather
than repeating an inline shape at every call site.

The shapes here were derived from the actual ``Response({...})`` literals in the
view modules, not invented: ``{"error": ...}`` appears 51 times, ``{"success",
"message"}`` 12 times, ``{"message"}`` and ``{"error", "detail"}` a handful each.

These are documentation-only. DRF does not run a response through the serializer
named in ``responses=``, so a drift between the annotation and the real payload
will not raise at runtime — it has to be caught by a schema contract test.
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse
from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer):
    """The single-key error envelope used for most 4xx/5xx responses."""

    error = serializers.CharField(help_text="Human-readable error message")


class DetailedErrorResponseSerializer(serializers.Serializer):
    """Error envelope carrying an extra machine- or developer-facing detail."""

    error = serializers.CharField(help_text="Human-readable error message")
    detail = serializers.CharField(
        required=False, help_text="Additional context about the failure"
    )


class MessageResponseSerializer(serializers.Serializer):
    """Bare message envelope, used where no success flag is returned."""

    message = serializers.CharField(help_text="Human-readable result message")


class SuccessMessageResponseSerializer(serializers.Serializer):
    """The ``{"success": true, "message": "..."}`` envelope."""

    success = serializers.BooleanField(help_text="Whether the operation succeeded")
    message = serializers.CharField(help_text="Human-readable result message")


# DRF's serializer-error payload: a mapping of field name to a list of error
# strings, e.g. ``{"email": ["This field is required."]}``, plus the non-field key
# ``"non_field_errors"``. Views here return ``Response(serializer.errors, 400)``
# directly, so the key set varies per endpoint and cannot be enumerated. Declared
# as a free-form object rather than as a serializer with no fields, which would
# wrongly document the body as always empty.
VALIDATION_ERROR_RESPONSE = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description="Validation failed. Keys are field names, values are lists of messages.",
    examples=[
        OpenApiExample(
            "Validation error",
            value={"email": ["Enter a valid email address."]},
            response_only=True,
        )
    ],
)
