from django.shortcuts import render, redirect
from django.http import HttpResponse
from http import HTTPStatus
from . import tasks

def task(request):

    result = tasks.add.delay(4,4)
    result.get(timeout=15)
    resp = HttpResponse(result)
    resp.status_code = HTTPStatus.OK
    return resp
