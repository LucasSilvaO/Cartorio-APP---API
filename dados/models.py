from django.db import models
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from rest_framework import serializers
# Create your models here.

class Family(models.Model):
    familia_id = models.AutoField(primary_key=True)
    nome_da_familia = models.CharField(max_length=255 ,null=False)
    def __str__(self):
        return f"{self.nome_da_familia}"

class Customer(models.Model):
    TIPO_CLIENTE_CHOICES = [
        ('CLIENTE A VISTA', 'Cliente a vista'),
        ('MENSALISTA', 'Mensalista'),
        # Adicione outras opções de produtos conforme necessário
    ]
    cliente_id = models.AutoField(primary_key=True)
    nome_do_representante = models.CharField(max_length=255 ,null=True)
    nome = models.CharField(max_length=255 ,null=False)
    email = models.CharField(max_length=255, null=False, blank=False)
    telefone = models.CharField(max_length=55, null=False, blank=False)
    tipo_do_cliente = models.CharField(max_length=50, choices=TIPO_CLIENTE_CHOICES)
    cpf_cnpj = models.CharField(max_length=255, null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    cidade = models.CharField(max_length=255, null=True, blank=True)
    estado = models.CharField(max_length=255, null=True, blank=True)
    cep = models.CharField(max_length=255, null=True, blank=True)
    ativo = models.BooleanField(default=True)
    usuario = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='Usuario', null=True, blank=True)

    def __str__(self):
        return f"{self.nome}"

class Translator(models.Model):
    tradutor_id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    prazo_em_dias = models.IntegerField(default=1)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome}"

class Seller(models.Model):
    vendedor_id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    ativo = models.BooleanField(default=True)
    id_conta_azul = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='UsuarioVendedor', null=True, blank=True)

    def __str__(self):
        return f"{self.nome}"

class ResponsibleTax(models.Model):
    responsavel_fiscal_id = models.AutoField(primary_key=True)
    budget = models.ForeignKey('Budget', on_delete=models.CASCADE, related_name='ResponsavelFiscal')
    nome = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    telefone = models.CharField(max_length=55)
    cpf_cnpj = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)
    cep = models.CharField(max_length=255)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome}"

class Comment(models.Model):
    comentario_id = models.AutoField(primary_key=True)
    comentario = models.TextField()
    data = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='UsuarioComentario')
    budget = models.ForeignKey('Budget', on_delete=models.CASCADE, related_name='Comentarios')

    def __str__(self):
        return f"{self.comentario}"

class ServiceDocument(models.Model):
    TIPO_SERVICO_CHOICES = [
        ('APOSTILAMENTO', 'Apostilamento'),
        ('POSTAGEMENVIO', 'Postagem/Envio'),
    ]
    servico_id = models.AutoField(primary_key=True)
    tipo_servico = models.CharField(max_length=255, choices=TIPO_SERVICO_CHOICES)
    descricao = models.CharField(max_length=255, null=True, blank=True)
    quantidade = models.IntegerField(default=1, null=True, blank=True)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    budget = models.ForeignKey('Budget', on_delete=models.CASCADE, related_name='servicos_documentos')

    def __str__(self):
        return f"{self.tipo_servico}"

class Document(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('CRC', 'CRC'),
        ('TRADUCAO', 'Tradução'),
    ]
    IDIOMA_DA_TRADUCAO_CHOICES = [
        ('INGLES', 'Inglês'),
        ('ESPANHOL', 'Espanhol'),
        ('FRANCES', 'Francês'),
        ('ALEMAO', 'Alemão'),
        ('ITALIANO', 'Italiano'),
    ]
    MODALIDADE_CHOICES = [
        ('NORMAL', 'Normal'),
        ('EXPRESSO', 'Expresso'),

        # Adicione outras opções de produtos conforme necessário
        ]
    FINALIZACAO_CHOICES = [
        ('CARTORIO', 'Cartório'),
        ('CLIENTE', 'Cliente'),
    ]
    documento_id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    budget = models.ForeignKey('Budget', on_delete=models.CASCADE, related_name='lista_documentos')
    tipo_documento = models.CharField(max_length=255, choices=TIPO_DOCUMENTO_CHOICES, null=True)
    descricao = models.CharField(max_length=255)
    idioma_da_traducao = models.CharField(max_length=255, choices=IDIOMA_DA_TRADUCAO_CHOICES, null=True)
    tipo_de_assinatura = models.CharField(max_length=255, null=True, blank=True, default='N/A')
    quantidade = models.IntegerField(default=1, null=True, blank=True)
    tradutor = models.ForeignKey(Translator, on_delete=models.CASCADE, related_name='TradutorDocument', null=True , blank=True)
    data_devolucao = models.DateField(null=True, blank=True)
    data_entrada_tradutor = models.DateField(null=True, blank=True)
    data_envio_tradutor = models.DateField(null=True, blank=True)
    data_devolucao_tradutor = models.DateField(null=True, blank=True)
    finalizacao = models.CharField(max_length=255, null=True, blank=True)
    data_envio_cartorio = models.DateField(null=True, blank=True)
    modalidade = models.CharField(max_length=255, null=True, blank=True, choices=MODALIDADE_CHOICES)
    prazo = models.DateField(null=True, blank=True)
    valor= models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nome}"

class Budget(models.Model):
    FORMA_DE_PAPGAMENTO_CHOICES = [
        ('A VISTA', 'A vista'),
        ('FATURADO', 'Faturado'),
    ]
    STATUS_CHOICES = [
        ('ORCAMENTO', 'Orçamento'),
        ('EM ANDAMENTO', 'Em Andamento'),
        ('PENDENTE', 'Pendente'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]
    budget_id = models.AutoField(primary_key=True)
    origem = models.CharField(max_length=255, null=True, blank=True)
    cliente = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='ClienteOrcamento')
    familia = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='FamiliaOrcamento')
    prazo = models.DateField()
    comprovante_pagamento = models.CharField(max_length=500, null=True, blank=True)
    vendedor = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='Vendedor', null=True, blank=True)
    forma_de_pagamento = models.CharField(max_length=255, choices=FORMA_DE_PAPGAMENTO_CHOICES, null=True, blank=True)
    quantidade_de_documentos = models.IntegerField()
    numero_de_parcelas = models.IntegerField(null=True, blank=True)
    valor_de_entrada = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_restante = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    documentos = models.ManyToManyField(Document, related_name='DocumentosBudget')
    data_segunda_parcela = models.DateField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    responsaveis_fiscais = models.ManyToManyField(ResponsibleTax, related_name='ResponsaveisFiscaisBudget')
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_criacao = models.DateField(auto_now_add=True)
    arquivado = models.BooleanField(default=False)
    numero_ca = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True , choices=STATUS_CHOICES, default='ORCAMENTO')
    usuario = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='UsuarioOrcamento', null=True, blank=True)

    def clean(self):
        errors = {}
        if self.forma_de_pagamento == 'A VISTA':
            if self.numero_de_parcelas is None:
                errors['numero_de_parcelas'] = 'Número de parcelas é obrigatório para pagamento a vista.'
            if self.valor_de_entrada is None and self.numero_de_parcelas > 1:
                errors['valor_de_entrada'] = 'Valor de entrada é obrigatório para pagamento a vista.'
            if self.valor_restante is None and self.numero_de_parcelas > 1:
                errors['valor_restante'] = 'Valor restante é obrigatório para pagamento a vista.'
            if self.data_segunda_parcela is None and self.numero_de_parcelas > 1:
                errors['data_segunda_parcela'] = 'Data da segunda parcela é obrigatória para pagamento a vista.'
        else:
            if self.numero_de_parcelas is not None:
                errors['numero_de_parcelas'] = 'Número de parcelas deve ser nulo para pagamento faturado.'
            if self.valor_de_entrada is not None:
                errors['valor_de_entrada'] = 'Valor de entrada deve ser nulo para pagamento faturado.'
            if self.valor_restante is not None:
                errors['valor_restante'] = 'Valor restante deve ser nulo para pagamento faturado.'
            if self.data_segunda_parcela is not None:
                errors['data_segunda_parcela'] = 'Data da segunda parcela deve ser nulo para pagamento faturado.'
        
        if errors:
            raise serializers.ValidationError(errors)
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.budget_id}"
    
class Service(models.Model):
    MODALIDADE_CHOICES = [
        ('NORMAL', 'Normal'),
        ('EXPRESSO', 'Expresso'),

        # Adicione outras opções de produtos conforme necessário
        ]
    STATUS_CHOICES = [
        ('ETAPA 1', 'Entrada de Serviço'),
        ('ETAPA 2', 'Assinatura do Tradutor'),
        ('ETAPA 3', 'Entrada do Tradutor'),
        ('ETAPA 4', 'Entrada Cartório'),

        # Adicione outras opções de produtos conforme necessário
        ]
    servico_id = models.AutoField(primary_key=True)
    ordem_de_servico = models.CharField(max_length=255)
    data_entrada = models.DateField()
    data_envio = models.DateField()
    cliente = models.ForeignKey(Customer, on_delete=models.CASCADE,  related_name='Cliente')
    familia = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='FamiliaServiço')
    modalidade = models.CharField(max_length=255, choices=MODALIDADE_CHOICES) 
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, null=True)
    tradutor = models.ForeignKey(Translator, on_delete=models.CASCADE, related_name= "Tradutor")
     
    def __str__(self):
        return f"{self.ordem_de_servico}"

class ServiceModalities(models.Model):
    modalidade_id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    prazo = models.IntegerField()
    def __str__(self):
        return f"{self.nome}"
    
class CustomUser(AbstractUser):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('cliente', 'Cliente'),
        ('colaborador', 'Colaborador'),
        ('comercial', 'Comercial'),
        ('vendedor', 'Vendedor'),
        ('financeiro', 'Financeiro'),
        ('gerencia', 'Gerência'),    
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='cliente')

    def __str__(self):
        return f"{self.username}"
    
class ContaAzulToken(models.Model):
    access_token = models.TextField(max_length=2550)
    refresh_token = models.TextField(max_length=2550)
    expires_in = models.DateTimeField()  # Guarda o momento em que o token expira

    def __str__(self):
        return f"Conta Azul Token"