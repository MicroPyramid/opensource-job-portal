"""
Contact API Views
Handles contact form submissions from frontend
"""
from django.conf import settings
from django.template import loader
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample

from dashboard.tasks import send_email
from .serializers import ContactSerializer, ContactResponseSerializer


@extend_schema(
    tags=["Contact"],
    summary="Submit contact form",
    description="""
    Submit a contact inquiry form. This endpoint accepts contact information and sends
    email notifications to the support team. All contact submissions are stored in the
    database for review in the admin panel.

    **No authentication required** - this is a public endpoint.
    """,
    request=ContactSerializer,
    responses={
        201: ContactResponseSerializer,
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string"},
                "details": {"type": "object"},
            },
        },
    },
    examples=[
        OpenApiExample(
            "General Inquiry",
            value={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": 9876543210,
                "category": "general",
                "subject": "Question about job postings",
                "comment": "I would like to know more about posting jobs on PeelJobs.",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Job Seeker Help",
            value={
                "first_name": "Jane",
                "email": "jane@example.com",
                "category": "job_seeker",
                "subject": "Help with profile",
                "comment": "I am having trouble updating my profile information.",
            },
            request_only=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def submit_contact_form(request):
    """
    Submit a contact inquiry form

    **Request Body:**
    ```json
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": 9876543210,
        "category": "general",
        "subject": "Question about job postings",
        "comment": "I would like to know more about posting jobs."
    }
    ```

    **Response:**
    ```json
    {
        "id": 123,
        "message": "Thank you for contacting us! We'll get back to you within 24 hours."
    }
    ```

    **Categories:**
    - `general` - General Inquiry
    - `support` - Technical Support
    - `job_seeker` - Job Seeker Help
    - `employer` - Employer/Recruiter
    - `partnership` - Partnership Opportunities
    - `feedback` - Feedback & Suggestions
    """
    serializer = ContactSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"error": "Validation failed", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Save the contact inquiry
    contact = serializer.save()

    # Prepare email context
    email_context = {
        "email": contact.email,
        "first_name": contact.first_name,
        "last_name": contact.last_name or "",
        "subject": contact.subject,
        "mobile": contact.phone or "Not provided",
        "enquiry_type": contact.get_enquery_type_display(),
        "comment": contact.comment,
    }

    # Send email notification to support team
    try:
        subject = f"New Contact Inquiry: {contact.get_enquery_type_display()} | PeelJobs"
        support_emails = getattr(settings, 'SUPPORT_EMAILS', ['peeljobs@micropyramid.com'])

        # Email to support team with Reply-To set to user's email
        template = loader.get_template("email/contactus_email.html")
        rendered = template.render(email_context)
        send_email.delay(support_emails, subject, rendered, reply_to=contact.email)

        # Confirmation email to user (no reply-to needed as it goes to the user)
        user_subject = "Thank you for contacting PeelJobs"
        user_template = loader.get_template("email/user_contactus.html")
        user_rendered = user_template.render(email_context)
        send_email.delay([contact.email], user_subject, user_rendered)
    except Exception as e:
        # Log the error but don't fail the request
        # The contact is already saved in the database
        print(f"Email send error: {e}")

    response_data = {
        "id": contact.id,
        "message": "Thank you for contacting us! We'll get back to you within 24 hours."
    }

    return Response(response_data, status=status.HTTP_201_CREATED)
