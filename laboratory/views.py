import csv
import io
import json

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods, require_POST

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


def _pdf_escape(value):
    return str(value).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def _build_simple_pdf(lines):
    y = 790
    commands = ['BT', '/F1 11 Tf', '40 810 Td', '(Objetos de Laboratorio) Tj']

    for line in lines:
        if y < 45:
            break

        commands.append(f'40 {y} Td ({_pdf_escape(line[:105])}) Tj')
        y -= 16

    commands.append('ET')
    stream = '\n'.join(commands).encode('latin-1', errors='replace')

    objects = [
        b'1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n',
        b'2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n',
        b'3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n',
        b'4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n',
        b'5 0 obj << /Length ' + str(len(stream)).encode('ascii') + b' >> stream\n' + stream + b'\nendstream endobj\n',
    ]

    pdf = io.BytesIO()
    pdf.write(b'%PDF-1.4\n')
    offsets = []

    for obj in objects:
        offsets.append(pdf.tell())
        pdf.write(obj)

    xref_position = pdf.tell()
    pdf.write(f'xref\n0 {len(objects) + 1}\n'.encode('ascii'))
    pdf.write(b'0000000000 65535 f \n')

    for offset in offsets:
        pdf.write(f'{offset:010d} 00000 n \n'.encode('ascii'))

    pdf.write(
        f'trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n'
        f'startxref\n{xref_position}\n%%EOF'.encode('ascii')
    )
    return pdf.getvalue()


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
    lines = [
        f'#{obj.id} | {obj.nome} | {obj.get_condicao_display()} | qtd: {obj.quantidade} | {obj.descricao}'
        for obj in objects
    ]

    response = HttpResponse(_build_simple_pdf(lines), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="objetos_laboratorio.pdf"'
    return response
