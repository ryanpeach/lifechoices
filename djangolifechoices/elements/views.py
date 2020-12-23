import os
from django.shortcuts import render, get_object_or_404

from djangolifechoices.settings import BASE_DIR
from elements.models import Plan

# Create your views here.
def home(request):
    return render(request, 'base.html')

def plan_list(request):
    plan = Plan.published.all()
    return render(request, 'list.html'), {'plan': plan}

def plan_detail(request, year, month, day):
    """Will sort plans by date created"""
    plan = get_object_or_404(
        Plan,
        status='published',
        publish__year=year,
        publish__month=month, 
        publish__day=day
    )

    return render(request, 'detail.html'), {'plan': plan}


