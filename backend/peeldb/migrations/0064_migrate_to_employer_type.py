# Data migration to convert all recruiter types to EM

from django.db import migrations


def migrate_user_types_forward(apps, schema_editor):
    """
    Convert all recruiter types (RR, RA, AA, AR) to EM (Employer)
    Preserves existing company and is_admin fields
    """
    User = apps.get_model('peeldb', 'User')

    # Get count before migration
    old_types = User.objects.filter(user_type__in=['RR', 'RA', 'AA', 'AR'])
    count = old_types.count()

    if count > 0:
        # Migrate all recruiter types to EM
        updated = old_types.update(user_type='EM')
        print(f"✅ Migrated {updated} users from old recruiter types to EM")
        print(f"   - Company admins (RA/AA): Now EM with is_admin=True")
        print(f"   - Recruiters (RR/AR): Now EM with is_admin=False")
    else:
        print("ℹ️  No users to migrate (no old recruiter types found)")

    # Log summary
    em_count = User.objects.filter(user_type='EM').count()
    js_count = User.objects.filter(user_type='JS').count()
    print(f"📊 Final counts: {em_count} Employers, {js_count} Job Seekers")


def migrate_user_types_reverse(apps, schema_editor):
    """
    Reverse migration - convert EM back to old types

    NOTE: This is a LOSSY reverse - we can't perfectly restore which
    specific old type (RR/RA/AA/AR) each user was, so we use best guesses:
    - EM + is_admin=True + has company → RA (Recruiter Admin)
    - EM + is_admin=False + has company → RR (Recruiter)
    - EM + no company → RR (Independent Recruiter)
    """
    User = apps.get_model('peeldb', 'User')

    # Company admins become RA
    ra_count = User.objects.filter(
        user_type='EM',
        is_admin=True,
        company__isnull=False
    ).update(user_type='RA')
    print(f"↩️  Converted {ra_count} company admins to RA")

    # Company members become RR
    rr_company_count = User.objects.filter(
        user_type='EM',
        is_admin=False,
        company__isnull=False
    ).update(user_type='RR')
    print(f"↩️  Converted {rr_company_count} company members to RR")

    # Independent recruiters become RR
    rr_indie_count = User.objects.filter(
        user_type='EM',
        company__isnull=True
    ).update(user_type='RR')
    print(f"↩️  Converted {rr_indie_count} independent recruiters to RR")

    total = ra_count + rr_company_count + rr_indie_count
    print(f"⚠️  Warning: Reverse migration is lossy. {total} users migrated back to best-guess types.")


class Migration(migrations.Migration):

    dependencies = [
        ('peeldb', '0063_add_employer_type_and_job_title'),
    ]

    operations = [
        migrations.RunPython(
            migrate_user_types_forward,
            reverse_code=migrate_user_types_reverse
        ),
    ]
