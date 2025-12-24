from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from peeldb.models import (
    Question,
    Skill,
    Solution,
)

from ..forms import (
    QuestionForm,
    SkillForm,
    SolutionForm,
)
from ..utils import get_paginated_results


# Functions to move here from main views.py:

def assessment_skills(request):
    """
    Manage assessment skills
    """
    pass


def new_question(request):
    """
    Create new assessment question
    """
    pass


def skill_questions(request, skill_id):
    """
    List questions for a skill
    """
    pass


def view_question(request, question_id):
    """
    View question details
    """
    pass
