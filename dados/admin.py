from django.contrib import admin

from dados.models import Customer, Translator, Service, ServiceModalities
from dados.models import Document, Budget, Seller, Comment, ContaAzulToken
# Register your models here.
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Tipo de Usuário', {'fields': ('user_type',)}),
    )
    list_display = ['username', 'email', 'user_type']

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Customer)

class ClienteAdmin(admin.ModelAdmin):
    list_display = ("cliente_id", "nome", "telefone", "cpf_cnpj")
    search_fields = ("cliente_id", "nome")

@admin.register(Translator)
class TradutorAdmin(admin.ModelAdmin):
    list_display = ("tradutor_id", "nome", "email", "ativo")
    search_fields = ("tradutor_id", "nome")
@admin.register(Service)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ("servico_id", "ordem_de_servico", "data_entrada", "data_envio", "modalidade", "status", "tradutor")
    search_fields = ("servico_id", "ordem_de_servico")

@admin.register(ServiceModalities)
class ModalidadeAdmin(admin.ModelAdmin):
    list_display = ("modalidade_id", "nome", "prazo")
    search_fields = ("modalidade_id", "nome")

@admin.register(Document)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("documento_id", "nome", "tipo_documento")
    search_fields = ("documento_id", "nome")

@admin.register(Budget)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ("budget_id", "valor", "origem", "cliente")
    search_fields = ("budget_id", "cliente")

@admin.register(Seller)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ("vendedor_id", "nome")
    search_fields = ("vendedor_id", "nome")

@admin.register(Comment)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("comentario_id", "comentario")
    search_fields = ("comentario_id", "comentario")

@admin.register(ContaAzulToken)
class ContaAzulTokenAdmin(admin.ModelAdmin):
    list_display = ("access_token", "refresh_token", "expires_in")
    search_fields = ("access_token", "refresh_token")