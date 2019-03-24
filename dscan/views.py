from django.contrib import messages
from django.db.models import Count
from django.views import View
from django.shortcuts import get_object_or_404, render, redirect

from sde.models import Type, Group

from . import constants
from .exceptions import DscanParseException
from .models import Dscan
from .utils import DscanParser


class DscanSubmit(View):
    """Submit a new dscan"""
    def get(self, request):
        return render(request, "dscan/submit.html")

    def post(self, request):
        if 'dscan' not in request.POST:
            messages.error(request, "Invalid form submission")
            return self.get(request)

        try:
            parser = DscanParser(request.POST['dscan'])
            accepted, rejected = parser.parse()
        except DscanParseException as ex:
            messages.error(request, str(ex))
            return self.get(request)

        return redirect("dscan:view", key=parser.dscan.key)


class DscanView(View):
    """View a dscan"""
    

    def get(self, request, key):
        dscan = get_object_or_404(Dscan, key=key)

        context = {
            'dscan': dscan,
            'ships_count': self._get_ships(dscan).count(),
            'ships': self.get_ships(dscan),
            'subcaps': self.get_subcaps(dscan),
            'caps': self.get_caps(dscan)
        }
        return render(request, "dscan/view.html", context)


    def _get_ships(self, dscan):
        return Type.objects.filter(
            dscan_objects__scan=dscan,
            group__category_id=6,
            ).annotate(
                count=Count('dscan_objects')
            ).order_by('-count', 'name')

    def get_ships(self, dscan):
        logistics = set(constants.logistics.values_list('id', flat=True))
        support = set(constants.support.values_list('id', flat=True))

        for type in self._get_ships(dscan):
            if type.id in constants.super_groups:
                yield ("table-danger", type)
            elif type.id in constants.cap_groups:
                yield ("table-warning", type)
            elif type.id in logistics:
                yield ("table-success", type)
            elif type.id in support:
                yield ("table-info", type)
            else:
                yield("table-active", type)


    def get_subcaps(self, dscan):
        return Group.objects.filter(
            types__dscan_objects__scan=dscan,
            category_id=6
        ).exclude(
            id__in=constants.super_groups + constants.cap_groups
        ).annotate(
            count=Count('types__dscan_objects')
        ).order_by('-count', 'name')


    def get_caps(self, dscan):
        return Group.objects.filter(
            types__dscan_objects__scan=dscan,
            category_id=6,
            id__in=constants.super_groups + constants.cap_groups
        ).annotate(
            count=Count('types__dscan_objects')
        ).order_by('-count', 'name')