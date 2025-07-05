from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Budget, ServiceDocument, Document, CustomUser
import time
from django.db.models import Q



def enviar_email_ao_criar_budget(budget, vendedor, servicos_documentos, documentos):
    from django.utils.html import format_html
    from django.conf import settings
    from django.core.mail import send_mail
    from django.db.models import Q

    # Coleta os e-mails dos admins e gerentes
    emails = CustomUser.objects.filter(Q(user_type='admin') | Q(user_type='gerencia')).values_list('email', flat=True)

    # Carrega o orçamento completo
    budget = Budget.objects.get(budget_id=budget.budget_id)

    # Documentos
    documentos_todos = budget.lista_documentos.all()

    # Serviços
    servicos_documentos = ServiceDocument.objects.filter(budget=budget)

    # Responsável fiscal
    responsavel_fiscal = budget.responsaveis_fiscais.first()
    responsavel_fiscal_info = f"{responsavel_fiscal.nome} - {responsavel_fiscal.cpf}" if responsavel_fiscal else 'Nenhum'

    # HTML dinâmico de documentos
    html_documentos = ""
    for doc in documentos_todos:
        html_documentos += f"""
        <tr>
            <td style="padding: 6px; border: 1px solid #ddd;">{doc.nome}</td>
            <td style="padding: 6px; border: 1px solid #ddd;">{doc.tipo_documento}</td>
            <td style="padding: 6px; border: 1px solid #ddd;">{doc.idioma_da_traducao or '-'}</td>
            <td style="padding: 6px; border: 1px solid #ddd;">{doc.tipo_de_assinatura or '-'}</td>
        </tr>
        """

    # HTML dinâmico de serviços
    html_servicos = ""
    for servico in servicos_documentos:
        html_servicos += f"""
        <tr>
            <td style="padding: 6px; border: 1px solid #ddd;">{servico.tipo_servico}</td>
            <td style="padding: 6px; border: 1px solid #ddd;">{servico.quantidade}</td>
            <td style="padding: 6px; border: 1px solid #ddd;">R$ {servico.valor_unitario}</td>
            <td style="padding: 6px; border: 1px solid #ddd;">R$ {servico.valor_total}</td>
        </tr>
        """

    assunto = f'Orçamento: {budget.familia.nome_da_familia} - nº: {budget.budget_id}'
    mensagem = f'Um novo Budget foi criado no sistema:\n\nID: {budget.budget_id}\nValor: {budget.valor}'

    mensagem_html = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Orçamento - Detalhes</title>
    </head>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="width: 100%; max-width: 800px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9; font-size:13px;">
            <h2 style="text-align:center; color: #0073aa;">Detalhes do Orçamento</h2>
            <table style="width: 100%; margin-bottom: 20px;">
                <tr><td><strong>Nome da Família:</strong></td><td>{budget.familia.nome_da_familia}</td></tr>
                <tr><td><strong>Cliente:</strong></td><td>{budget.cliente.nome}</td></tr>
                <tr><td><strong>Vendedor:</strong></td><td>{budget.vendedor.nome}</td></tr>
                <tr><td><strong>Data de Entrada:</strong></td><td>{budget.data_criacao}</td></tr>
                <tr><td><strong>Forma de Pagamento:</strong></td><td>{budget.forma_de_pagamento}</td></tr>
                <tr><td><strong>Valor Total:</strong></td><td>R$ {budget.valor}</td></tr>
            </table>

            <h3 style="color: #0073aa;">Documentos</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th style="padding: 8px; border: 1px solid #ccc; background-color: #eee;">Nome</th>
                        <th style="padding: 8px; border: 1px solid #ccc; background-color: #eee;">Tipo</th>
                        <th style="padding: 8px; border: 1px solid #ccc; background-color: #eee;">Idioma</th>
                        <th style="padding: 8px; border: 1px solid #ccc; background-color: #eee;">Assinatura</th>
                    </tr>
                </thead>
                <tbody>
                    {html_documentos}
                </tbody>
            </table>

            <h3 style="color: #0073aa; margin-top: 30px;">Serviços</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th style="padding: 8px; border: 1px solid #ccc; background-color: #eee;">Tipo</th>
                        <th style="padding: 8px; border: 1px solid #ccc; background-color: #eee;">Quantidade</th>
                        <th style="padding: 8px; border: 1px solid #ccc; background-color: #eee;">Valor Unitário</th>
                        <th style="padding: 8px; border: 1px solid #ccc; background-color: #eee;">Valor Total</th>
                    </tr>
                </thead>
                <tbody>
                    {html_servicos}
                </tbody>
            </table>

            <h3 style="color: #0073aa; margin-top: 30px;">Responsável Fiscal</h3>
            <p>{responsavel_fiscal_info}</p>

            <h3 style="color: #0073aa;">Observações</h3>
            <p>{budget.observacoes or "Nenhuma observação."}</p>

            <div style="margin-top: 30px;">
                <a href="https://cliente.pro/dashboard-2/" style="text-decoration: none; color: white; background-color: #0073aa; padding: 10px 20px; border-radius: 4px;">Acesse os Orçamentos</a>
            </div>
        </div>
    </body>
    </html>
    """

    send_mail(
        assunto,
        mensagem,
        settings.EMAIL_HOST_USER,
        emails,
        fail_silently=False,
        html_message=mensagem_html
    )

