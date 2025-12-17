# Final migration: Remove old user types and add TeamInvitation model

from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone
from datetime import timedelta


class Migration(migrations.Migration):

    dependencies = [
        ('peeldb', '0064_migrate_to_employer_type'),
    ]

    operations = [
        # Update user_type choices to only JS and EM (remove old types)
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(
                choices=[
                    ('JS', 'Job Seeker'),
                    ('EM', 'Employer'),
                ],
                max_length=10
            ),
        ),

        # Create TeamInvitation model
        migrations.CreateModel(
            name='TeamInvitation',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('email', models.EmailField(
                    max_length=254,
                    help_text='Email address of person to invite'
                )),
                ('token', models.CharField(
                    max_length=100,
                    unique=True,
                    help_text='Unique token for invitation link'
                )),
                ('role_title', models.CharField(
                    blank=True,
                    max_length=100,
                    help_text="Job title/role of invitee (e.g., 'Senior Recruiter', 'HR Manager')"
                )),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('accepted', 'Accepted'),
                        ('expired', 'Expired'),
                        ('cancelled', 'Cancelled'),
                    ],
                    default='pending',
                    max_length=20
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(
                    help_text='Invitation expires after 7 days'
                )),
                ('accepted_at', models.DateTimeField(
                    blank=True,
                    null=True
                )),
                ('company', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='team_invitations',
                    to='peeldb.company'
                )),
                ('invited_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sent_invitations',
                    to='peeldb.user'
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),

        # Add unique constraint for company + email combination
        migrations.AddConstraint(
            model_name='teaminvitation',
            constraint=models.UniqueConstraint(
                fields=['company', 'email'],
                name='unique_company_email_invitation'
            ),
        ),

        # Add index on token field for faster lookups
        migrations.AddIndex(
            model_name='teaminvitation',
            index=models.Index(
                fields=['token'],
                name='teaminv_token_idx'
            ),
        ),

        # Add index on email + status for faster filtering
        migrations.AddIndex(
            model_name='teaminvitation',
            index=models.Index(
                fields=['email', 'status'],
                name='teaminv_email_status_idx'
            ),
        ),
    ]
