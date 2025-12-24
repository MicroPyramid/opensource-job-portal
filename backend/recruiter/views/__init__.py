# Import aggregator for backward compatibility
# This ensures existing imports continue to work after the reorganization

# Note: Most recruiter views have been migrated to SvelteKit + REST API
# These remaining modules contain helper functions or legacy functionality
from .job_helpers import *
from .dashboard import *
