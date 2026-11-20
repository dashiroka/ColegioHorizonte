from decimal import Decimal
from django import forms
from .models import Estudiante,Acudiente,EstudianteAcudiente,Grado,Grupo,PeriodoAcademico,ConceptoCobro,Matricula,Obligacion
class DateInput(forms.DateInput): input_type='date'
class EstudianteForm(forms.ModelForm):
    class Meta:
        model=Estudiante
        fields='__all__'
        widgets={'fecha_nacimiento':DateInput()}
class AcudienteForm(forms.ModelForm):
    class Meta: model=Acudiente; fields='__all__'
class EstudianteAcudienteForm(forms.ModelForm):
    class Meta: model=EstudianteAcudiente; fields='__all__'
class GrupoForm(forms.ModelForm):
    class Meta: model=Grupo; fields='__all__'
class PeriodoForm(forms.ModelForm):
    class Meta:
        model=PeriodoAcademico
        fields='__all__'
        widgets={'fecha_inicio':DateInput(),'fecha_fin':DateInput()}
class ConceptoForm(forms.ModelForm):
    class Meta: model=ConceptoCobro; fields='__all__'
class MatriculaForm(forms.ModelForm):
    class Meta:
        model=Matricula
        fields=['estudiante','grupo','periodo','fecha','valor_matricula','descuento']
        widgets={'fecha':DateInput()}
    def clean(self):
        d=super().clean()
        estudiante=d.get('estudiante'); periodo=d.get('periodo'); grupo=d.get('grupo')
        if estudiante and estudiante.estado!='Activo': self.add_error('estudiante','Estudiante inactivo.')
        if periodo and not periodo.activo: self.add_error('periodo','Período inactivo.')
        if grupo and (not grupo.activo or not grupo.grado.activo): self.add_error('grupo','Grupo o grado inactivo.')
        if estudiante and periodo and Matricula.objects.filter(estudiante=estudiante,periodo=periodo).exists():
            self.add_error('estudiante','Ya existe una matrícula para este período.')
        return d
class ObligacionForm(forms.ModelForm):
    class Meta:
        model=Obligacion
        fields=['matricula','concepto','descripcion','valor','vencimiento']
        widgets={'vencimiento':DateInput()}
class PagoForm(forms.Form):
    obligacion=forms.ModelChoiceField(queryset=Obligacion.objects.filter(anulada=False),label='Obligación')
    valor=forms.DecimalField(min_value=Decimal('0.01'),max_digits=12,decimal_places=2)
    referencia=forms.CharField(max_length=45)
    def clean_referencia(self):
        from .models import Pago
        v=self.cleaned_data['referencia']
        if Pago.objects.filter(referencia=v).exists(): raise forms.ValidationError('Referencia ya registrada.')
        return v
class AnulacionForm(forms.Form):
    justificacion=forms.CharField(widget=forms.Textarea, min_length=8)
