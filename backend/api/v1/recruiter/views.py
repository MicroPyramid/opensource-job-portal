"""
Team Management API Views
"""
from datetime import datetime
from django.conf import settings
from django.template import loader
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from dashboard.tasks import send_email

from peeldb.models import User, TeamInvitation
from .serializers import (
    TeamMemberSerializer,
    TeamMemberDetailSerializer,
    TeamInvitationSerializer,
    SendInvitationSerializer,
    UpdateTeamMemberSerializer,
    CompanyBasicSerializer
)


def is_company_admin(user):
    """Check if user is a company admin"""
    return user.user_type == 'EM' and user.is_admin and user.company is not None


def send_team_invitation_email(invitation, message=None):
    """Send team invitation email"""
    # Use recruiter UI URL for invitation
    frontend_url = settings.RECRUITER_FRONTEND_URL if hasattr(settings, 'RECRUITER_FRONTEND_URL') else 'http://localhost:5174'
    invitation_url = f"{frontend_url}/signup?invitation={invitation.token}"

    # Render email template
    template = loader.get_template('recruiter/email/team_invitation.html')
    context = {
        'invitation': invitation,
        'company': invitation.company,
        'invited_by': invitation.invited_by,
        'role_title': invitation.role_title,
        'invitation_url': invitation_url,
        'message': message,
        'current_year': datetime.now().year
    }
    html_content = template.render(context)

    # Send email via Celery task
    send_email.delay(
        mto=[invitation.email],
        msubject=f"Invitation to join {invitation.company.name} on PeelJobs",
        mbody=html_content
    )


@extend_schema(
    tags=["Team Management"],
    summary="List Team Members",
    description="Get all team members for the authenticated user's company",
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_team_members(request):
    """
    List all team members in the user's company

    Returns company info and list of team members with their stats
    """
    user = request.user

    # Check if user is part of a company
    if not user.company:
        return Response(
            {"error": "You are not part of any company"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get all team members
    members = User.objects.filter(
        company=user.company,
        user_type='EM'
    ).order_by('-is_admin', 'first_name')

    company_serializer = CompanyBasicSerializer(user.company)
    members_serializer = TeamMemberSerializer(members, many=True)

    return Response({
        "company": company_serializer.data,
        "members": members_serializer.data,
        "total_members": members.count()
    })


@extend_schema(
    tags=["Team Management"],
    summary="Get Team Member Details",
    description="Get detailed information about a specific team member",
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_team_member(request, user_id):
    """Get detailed info about a specific team member"""
    user = request.user

    if not user.company:
        return Response(
            {"error": "You are not part of any company"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get team member
    try:
        member = User.objects.get(
            id=user_id,
            company=user.company,
            user_type='EM'
        )
    except User.DoesNotExist:
        return Response(
            {"error": "User not found in your company"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = TeamMemberDetailSerializer(member)
    return Response(serializer.data)


@extend_schema(
    tags=["Team Management"],
    summary="Invite Team Member",
    description="Send invitation to join the company team (Admin only)",
    request=SendInvitationSerializer,
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_team_member(request):
    """
    Send invitation to new team member (Admin only)

    Creates a team invitation and sends email with signup link
    """
    user = request.user

    # Check if user is company admin
    if not is_company_admin(user):
        return Response(
            {"error": "Only company admins can invite team members"},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = SendInvitationSerializer(
        data=request.data,
        context={'company': user.company, 'user': user}
    )

    if serializer.is_valid():
        invitation = serializer.save()

        # Send invitation email
        message = request.data.get('message', None)
        send_team_invitation_email(invitation, message)

        return Response({
            "success": True,
            "invitation": TeamInvitationSerializer(invitation).data,
            "message": f"Invitation sent successfully to {invitation.email}"
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Team Management"],
    summary="List Pending Invitations",
    description="View all pending team invitations (Admin only)",
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_invitations(request):
    """List all team invitations for the company (Admin only)"""
    user = request.user

    if not is_company_admin(user):
        return Response(
            {"error": "Only company admins can view invitations"},
            status=status.HTTP_403_FORBIDDEN
        )

    invitations = TeamInvitation.objects.filter(company=user.company)

    serializer = TeamInvitationSerializer(invitations, many=True)

    pending_count = invitations.filter(status='pending').count()
    expired_count = invitations.filter(status='expired').count()

    return Response({
        "invitations": serializer.data,
        "total": invitations.count(),
        "pending_count": pending_count,
        "expired_count": expired_count
    })


@extend_schema(
    tags=["Team Management"],
    summary="Resend Invitation",
    description="Resend invitation email and extend expiry (Admin only)",
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_invitation(request, invitation_id):
    """Resend invitation email (Admin only)"""
    user = request.user

    if not is_company_admin(user):
        return Response(
            {"error": "Only company admins can resend invitations"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        invitation = TeamInvitation.objects.get(
            id=invitation_id,
            company=user.company
        )
    except TeamInvitation.DoesNotExist:
        return Response(
            {"error": "Invitation not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Extend expiry
    from django.utils import timezone
    from datetime import timedelta
    invitation.expires_at = timezone.now() + timedelta(days=7)
    invitation.status = 'pending'
    invitation.save()

    # Resend email
    send_team_invitation_email(invitation)

    return Response({
        "success": True,
        "invitation": TeamInvitationSerializer(invitation).data,
        "message": "Invitation resent successfully"
    })


@extend_schema(
    tags=["Team Management"],
    summary="Cancel Invitation",
    description="Cancel a pending invitation (Admin only)",
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_invitation(request, invitation_id):
    """Cancel a pending invitation (Admin only)"""
    user = request.user

    if not is_company_admin(user):
        return Response(
            {"error": "Only company admins can cancel invitations"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        invitation = TeamInvitation.objects.get(
            id=invitation_id,
            company=user.company,
            status='pending'
        )
    except TeamInvitation.DoesNotExist:
        return Response(
            {"error": "Invitation not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    invitation.status = 'cancelled'
    invitation.save()

    return Response({
        "success": True,
        "message": "Invitation cancelled"
    })


@extend_schema(
    tags=["Team Management"],
    summary="Update Team Member",
    description="Update team member details or promote to admin (Admin only)",
    request=UpdateTeamMemberSerializer,
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_team_member(request, user_id):
    """
    Update team member (Admin only)

    Can update job_title or promote/demote admin status
    """
    user = request.user

    if not is_company_admin(user):
        return Response(
            {"error": "Only company admins can update team members"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        member = User.objects.get(
            id=user_id,
            company=user.company,
            user_type='EM'
        )
    except User.DoesNotExist:
        return Response(
            {"error": "User not found in your company"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Prevent updating yourself
    if member.id == user.id:
        return Response(
            {"error": "You cannot update your own permissions"},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = UpdateTeamMemberSerializer(
        data=request.data,
        context={'user_to_update': member, 'company': user.company}
    )

    if serializer.is_valid():
        # Update fields
        if 'job_title' in serializer.validated_data:
            member.job_title = serializer.validated_data['job_title']

        if 'is_admin' in serializer.validated_data:
            member.is_admin = serializer.validated_data['is_admin']

        member.save()

        return Response({
            "success": True,
            "user": TeamMemberSerializer(member).data,
            "message": "Team member updated successfully"
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Team Management"],
    summary="Remove Team Member",
    description="Remove team member from company (Admin only)",
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_team_member(request, user_id):
    """
    Remove team member from company (Admin only)

    User becomes an independent recruiter after removal
    """
    user = request.user

    if not is_company_admin(user):
        return Response(
            {"error": "Only company admins can remove team members"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        member = User.objects.get(
            id=user_id,
            company=user.company,
            user_type='EM'
        )
    except User.DoesNotExist:
        return Response(
            {"error": "User not found in your company"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Prevent removing yourself
    if member.id == user.id:
        return Response(
            {"error": "You cannot remove yourself. Ask another admin to remove you."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check not removing last admin
    if member.is_admin:
        admin_count = User.objects.filter(
            company=user.company,
            is_admin=True,
            user_type='EM'
        ).count()

        if admin_count <= 1:
            return Response(
                {"error": "Cannot remove the last admin. Promote another member first."},
                status=status.HTTP_400_BAD_REQUEST
            )

    member_name = f"{member.first_name} {member.last_name}".strip()

    # Remove from company (becomes independent recruiter)
    member.company = None
    member.is_admin = False
    member.save()

    # TODO: Send notification email to removed user

    return Response({
        "success": True,
        "message": f"{member_name} has been removed from {user.company.name}"
    })


@extend_schema(
    tags=["Company Profile"],
    summary="Get Company Profile",
    description="Get detailed company profile for the authenticated recruiter",
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_company_profile(request):
    """
    Get company profile details for the authenticated recruiter

    Only accessible to recruiters who are part of a company
    """
    user = request.user

    # Check if user is part of a company
    if not user.company:
        return Response(
            {"error": "You are not part of any company"},
            status=status.HTTP_400_BAD_REQUEST
        )

    from .serializers import CompanyDetailSerializer
    serializer = CompanyDetailSerializer(user.company, context={'request': request})

    return Response(serializer.data)


@extend_schema(
    tags=["Company Profile"],
    summary="Update Company Profile",
    description="Update company profile (Admin only)",
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_company_profile(request):
    """
    Update company profile details

    Only company admins can update company profile
    """
    user = request.user

    # Check if user is company admin
    if not is_company_admin(user):
        return Response(
            {"error": "Only company admins can update company profile"},
            status=status.HTTP_403_FORBIDDEN
        )

    from .serializers import CompanyUpdateSerializer, CompanyDetailSerializer

    serializer = CompanyUpdateSerializer(
        user.company,
        data=request.data,
        partial=True,
        context={'request': request}
    )

    if serializer.is_valid():
        serializer.save()

        # Return updated company data
        result_serializer = CompanyDetailSerializer(user.company, context={'request': request})

        return Response({
            "success": True,
            "message": "Company profile updated successfully",
            "company": result_serializer.data
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
