import csv
import io
import json

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from accounts.views import is_system_admin

from .forms import ObjetoLaboratorioForm
from .models import ObjetoLaboratorio


MAX_LIST_ITEMS = 50
MAX_EXPORT_ITEMS = 500


def _lab_objects_queryset(search=''):
    queryset = ObjetoLaboratorio.objects.only(
        'id',
        'nome',
        'condicao',
        'quantidade',
        'descricao',
        'created_at',
    )

    if search:
        queryset = queryset.filter(nome__icontains=search)

    return queryset.order_by('-id')


def _serialize_object(obj):
    return {
        'id': obj.id,
        'nome': obj.nome,
        'condicao': obj.condicao,
        'condicao_label': obj.get_condicao_display(),
        'quantidade': obj.quantidade,
        'descricao': obj.descricao,
        'created_at': obj.created_at.strftime('%d/%m/%Y %H:%M'),
    }


def _request_data(request):
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return {}

    return request.POST


def _form_errors(form):
    return {
        field: [str(error) for error in errors]
        for field, errors in form.errors.items()
    }


def _build_lab_objects_pdf(objects):
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        pageCompression=0,
        rightMargin=24,
        leftMargin=24,
        topMargin=24,
        bottomMargin=24,
        title='Objetos de Laboratorio',
    )
    styles = getSampleStyleSheet()
    normal_style = styles['BodyText']
    elements = [
        Paragraph('Objetos de Laboratorio', styles['Title']),
        Spacer(1, 12),
    ]
    table_data = [['ID', 'Nome', 'Condicao', 'Quantidade', 'Descricao']]

    for obj in objects:
        table_data.append([
            str(obj.id),
            Paragraph(obj.nome, normal_style),
            obj.get_condicao_display(),
            str(obj.quantidade),
            Paragraph(obj.descricao or '-', normal_style),
        ])

    table = Table(table_data, repeatRows=1, colWidths=[42, 170, 90, 82, 360])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#12395b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    document.build(elements)
    return buffer.getvalue()


@user_passes_test(is_system_admin, login_url='login')
def manage_lab_objects(request):
    return render(request, 'admin_config/manage_lab_objects.html', {
        'condicao_choices': ObjetoLaboratorio.Condicao.choices,
    })


@user_passes_test(is_system_admin, login_url='login')
@require_http_methods(['GET', 'POST'])
def lab_objects_api(request):
    if request.method == 'GET':
        search = request.GET.get('q', '').strip()
        objects = _lab_objects_queryset(search)[:MAX_LIST_ITEMS]
        return JsonResponse({
            'objects': [_serialize_object(obj) for obj in objects],
        })

    form = ObjetoLaboratorioForm(_request_data(request))
    if not form.is_valid():
        return JsonResponse({'errors': _form_errors(form)}, status=400)

    obj = form.save()
    return JsonResponse({'object': _serialize_object(obj)}, status=201)


@user_passes_test(is_system_admin, login_url='login')
@require_http_methods(['GET', 'POST', 'DELETE'])
def lab_object_detail_api(request, object_id):
    obj = get_object_or_404(ObjetoLaboratorio, pk=object_id)

    if request.method == 'GET':
        return JsonResponse({'object': _serialize_object(obj)})

    if request.method == 'DELETE':
        obj.delete()
        return JsonResponse({'deleted': True})

    form = ObjetoLaboratorioForm(_request_data(request), instance=obj)
    if not form.is_valid():
        return JsonResponse({'errors': _form_errors(form)}, status=400)

    obj = form.save()
    return JsonResponse({'object': _serialize_object(obj)})


@user_passes_test(is_system_admin, login_url='login')
def export_lab_objects_csv(request):
    search = request.GET.get('q', '').strip()
    objects = _lab_objects_queryset(search)[:MAX_EXPORT_ITEMS]

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="objetos_laboratorio.csv"'

    writer = csv.writer(response)
    writer.writerow(['id', 'nome', 'condicao', 'quantidade', 'descricao'])

    for obj in objects:
        writer.writerow([obj.id, obj.nome, obj.get_condicao_display(), obj.quantidade, obj.descricao])

    return response


@user_passes_test(is_system_admin, login_url='login')
def export_lab_objects_pdf(request):
    search = request.GET.get('q', '').strip()
    objects = _lab_objects_queryset(search)[:MAX_EXPORT_ITEMS]

    response = HttpResponse(_build_lab_objects_pdf(objects), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="objetos_laboratorio.pdf"'
    return response
