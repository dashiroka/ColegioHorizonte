"""Diez reportes financieros en vivo (datos exclusivamente desde el ORM)."""
from io import BytesIO
from decimal import Decimal
from django.http import HttpResponse
from django.db.models import Sum
from django.utils import timezone
from .models import Estudiante, Matricula, Obligacion, Pago

DEFINICIONES={
 'matriculados':'1. Estudiantes matriculados por período',
 'matriculas_pendientes':'2. Matrículas pendientes de pago',
 'mensualidades':'3. Mensualidades generadas',
 'pagos_fecha':'4. Pagos realizados por fecha',
 'pagos_pendientes':'5. Estudiantes con pagos pendientes',
 'mora':'6. Estudiantes en mora',
 'estado_cuenta':'7. Estado de cuenta individual',
 'recaudado':'8. Total recaudado por período',
 'cartera':'9. Total de cartera pendiente',
 'ingresos':'10. Resumen de ingresos por concepto',
}

def obtener_reporte(tipo, periodo='', estudiante='', estado='', grado=''):
    qs=Obligacion.objects.select_related('matricula__estudiante','matricula__grupo__grado','matricula__periodo','concepto').filter(anulada=False)
    ms=Matricula.objects.select_related('estudiante','grupo__grado','periodo')
    if periodo:
        qs=qs.filter(matricula__periodo__nombre__icontains=periodo)
        ms=ms.filter(periodo__nombre__icontains=periodo)
    if estudiante:
        from django.db.models import Q
        filtro=Q(matricula__estudiante__documento__icontains=estudiante)|Q(matricula__estudiante__nombres__icontains=estudiante)|Q(matricula__estudiante__apellidos__icontains=estudiante)
        qs=qs.filter(filtro)
        ms=ms.filter(Q(estudiante__documento__icontains=estudiante)|Q(estudiante__nombres__icontains=estudiante)|Q(estudiante__apellidos__icontains=estudiante))
    if grado:
        qs=qs.filter(matricula__grupo__grado__nombre__icontains=grado)
        ms=ms.filter(grupo__grado__nombre__icontains=grado)
    resultado=[]
    if tipo=='matriculados':
        cols=['Matrícula','Estudiante','Documento','Grado','Período','Estado']
        resultado=[[m.numero,f'{m.estudiante.nombres} {m.estudiante.apellidos}',m.estudiante.documento,m.grupo.grado.nombre,m.periodo.nombre,m.estado] for m in ms]
    elif tipo=='pagos_fecha':
        cols=['Fecha','Referencia','Usuario','Valor','Estado']
        pagos=Pago.objects.select_related('registrado_por').order_by('-fecha')
        if periodo: pagos=pagos.filter(detalles__obligacion__matricula__periodo__nombre__icontains=periodo).distinct()
        if estudiante: pagos=pagos.filter(detalles__obligacion__matricula__estudiante__documento__icontains=estudiante).distinct()
        resultado=[[p.fecha.strftime('%Y-%m-%d'),p.referencia,p.registrado_por.username,str(p.total),p.estado] for p in pagos]
    elif tipo=='recaudado':
        cols=['Período','Total recaudado']
        # Recaudo asignado a obligaciones; abonos confirmados sin duplicar pagos
        from .models import DetallePago
        abonos=DetallePago.objects.filter(pago__estado='Confirmado')
        if periodo: abonos=abonos.filter(obligacion__matricula__periodo__nombre__icontains=periodo)
        if estudiante: abonos=abonos.filter(obligacion__matricula__estudiante__documento__icontains=estudiante)
        data=abonos.values('obligacion__matricula__periodo__nombre').annotate(total=Sum('valor')).order_by('obligacion__matricula__periodo__nombre')
        resultado=[[d['obligacion__matricula__periodo__nombre'],str(d['total'])] for d in data]
    elif tipo=='ingresos':
        cols=['Concepto','Total recaudado']
        from .models import DetallePago
        abonos=DetallePago.objects.filter(pago__estado='Confirmado')
        if periodo: abonos=abonos.filter(obligacion__matricula__periodo__nombre__icontains=periodo)
        if estudiante: abonos=abonos.filter(obligacion__matricula__estudiante__documento__icontains=estudiante)
        data=abonos.values('obligacion__concepto__nombre').annotate(total=Sum('valor')).order_by('obligacion__concepto__nombre')
        resultado=[[d['obligacion__concepto__nombre'],str(d['total'])] for d in data]
    elif tipo=='cartera':
        cols=['Indicador','Saldo (COP)']
        resultado=[['Total cartera pendiente',str(sum((o.saldo for o in qs if o.saldo>0),Decimal('0.00')))],['Obligaciones pendientes',str(sum(1 for o in qs if o.saldo>0))]]
    else:
        cols=['Estudiante','Matrícula','Concepto','Vencimiento','Valor','Abonado','Saldo','Estado']
        for o in qs:
            if tipo=='mensualidades' and o.concepto.tipo!='PENSION': continue
            if tipo=='matriculas_pendientes' and (o.concepto.tipo!='MATRICULA' or o.saldo<=0): continue
            if tipo=='pagos_pendientes' and o.saldo<=0: continue
            if tipo=='mora' and (o.saldo<=0 or o.vencimiento >= timezone.localdate()): continue
            if tipo=='estado_cuenta' and not estudiante: continue  # requiere selección de estudiante
            if estado and o.estado.lower()!=estado.lower(): continue
            resultado.append([str(o.matricula.estudiante),o.matricula.numero,o.descripcion,str(o.vencimiento),str(o.valor),str(o.abonado()),str(o.saldo),o.estado])
    return cols,resultado

def generar_excel(codigo,columnas,filas):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    wb=Workbook(); ws=wb.active; ws.title='Reporte'
    ws.append([DEFINICIONES[codigo]]); ws.append(columnas)
    for fila in filas: ws.append([str(v) for v in fila])
    for cell in ws[2]: cell.font=Font(bold=True,color='FFFFFF'); cell.fill=PatternFill('solid',fgColor='19334E')
    ws.freeze_panes='A3'
    for col in ws.columns:
        letter=col[0].column_letter
        ws.column_dimensions[letter].width=min(48,max(14,max(len(str(c.value or '')) for c in col)+2))
    buffer=BytesIO(); wb.save(buffer)
    response=HttpResponse(buffer.getvalue(),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition']=f'attachment; filename="reporte_{codigo}.xlsx"'
    return response

def generar_pdf(codigo,columnas,filas):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4,landscape
    buffer=BytesIO(); c=canvas.Canvas(buffer,pagesize=landscape(A4))
    w,h=landscape(A4); y=h-55
    c.setFont('Helvetica-Bold',15); c.drawString(36,y,DEFINICIONES[codigo][:90]); y-=30
    # representación tabular abreviada para conservar legibilidad
    def safe(x,n=35):
        s=str(x).replace('\n',' ')
        return (s[:n-2]+'..') if len(s)>n else s
    c.setFont('Helvetica-Bold',8); c.drawString(36,y,' | '.join(safe(x,20) for x in columnas)[:150]); y-=17
    c.setFont('Helvetica',7)
    for fila in filas:
        text=' | '.join(safe(x,21) for x in fila)[:160]
        c.drawString(36,y,text); y-=13
        if y<35:
            c.showPage(); y=h-42;c.setFont('Helvetica',7)
    c.save()
    response=HttpResponse(buffer.getvalue(),content_type='application/pdf')
    response['Content-Disposition']=f'attachment; filename="reporte_{codigo}.pdf"'
    return response
