from rest_framework import serializers
from dados.models import Customer, Translator, Service, ServiceModalities, Family, Seller, Document, Budget, ResponsibleTax, ServiceDocument, CustomUser, Comment
from dados.signals import enviar_email_ao_criar_budget
import threading
from rest_framework.response import Response




class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    customer = serializers.SerializerMethodField()
    seller = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id','username', 'email', 'password', 'first_name', 'last_name', 'user_type', 'is_active', 'customer', 'seller']

    # Sobrescrever para criar ou atualizar senha
    def create(self, validated_data):
        # Criptografar a senha antes de salvar
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        user.set_password(password)  # Criptografa a senha
        user.save()

        return user

    def update(self, instance, validated_data):
        # Atualiza a senha se a senha for fornecida
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))

        # Atualiza todos os outros campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()  # Salva as alterações
        return instance
    
    def get_customer(self, obj):
        if obj.user_type == 'cliente':
            try:
                customer = Customer.objects.get(usuario=obj)
                return CustomerSerializer(customer).data
            except Customer.DoesNotExist:
                return None
        return None

    def get_seller(self, obj):
        if obj.user_type == 'comercial':
            try:
                seller = Seller.objects.get(user=obj)
                return SellerSerializer(seller).data
            except Seller.DoesNotExist:
                return None
        return None

class CommentReadSerializer(serializers.ModelSerializer):
    usuario = CustomUserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = '__all__'

class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class TranslatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translator
        fields = '__all__'

class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = '__all__'

class ServiceModalitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceModalities
        fields = '__all__'

class ServiceReadSerializer(serializers.ModelSerializer):
    familia = serializers.SerializerMethodField()
    tradutor = serializers.SerializerMethodField()
    comentarios = serializers.SerializerMethodField()
    class Meta:
        model = Service
        fields = '__all__'

    def get_familia(self, obj):
        famlia = Family.objects.get(familia_id=obj.familia.familia_id)
        serializer = FamilySerializer(famlia)
        return serializer.data
    
    def get_tradutor(self, obj):
        tradutor = Translator.objects.get(tradutor_id=obj.tradutor.tradutor_id)
        serializer = TranslatorSerializer(tradutor)
        return serializer.data
    def get_comentarios(self, obj):
        comentarios = Comment.objects.filter(servico=obj)
        serializer = CommentReadSerializer(comentarios, many=True)
        return serializer.data

class ServiceWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'

class DocumentReadSerializer(serializers.ModelSerializer):
    tradutor = TranslatorSerializer(read_only=True)

    class Meta:
        model = Document
        fields = '__all__'
        extra_kwargs = {
            'budget': {'required': False}
        }

class DocumentWriteSerializer(serializers.ModelSerializer):
    documento_id = serializers.IntegerField(required=False)
    tradutor = serializers.PrimaryKeyRelatedField(queryset=Translator.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Document
        fields = '__all__'
        extra_kwargs = {
            'budget': {'required': False}
        }

class ResponsibleTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponsibleTax
        fields = '__all__'
        extra_kwargs = {
            'budget': {'required': False}
        }

class ServiceDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceDocument
        fields = '__all__'
        extra_kwargs = {
            'budget': {'required': False}
        }



class BudgetReadSerializer(serializers.ModelSerializer):
    vendedor = SellerSerializer(read_only=True)
    documentos = DocumentReadSerializer(many=True, read_only=True, source='lista_documentos')
    responsaveis_fiscais = ResponsibleTaxSerializer(many=True, read_only=True, source='ResponsavelFiscal')
    familia = FamilySerializer(read_only=True)
    servicos_documentos = ServiceDocumentSerializer(many=True, read_only=True)
    cliente = CustomerSerializer(read_only=True)
    comentarios = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = '__all__'
    def get_comentarios(self, obj):
        comentarios = Comment.objects.filter(budget=obj)
        serializer = CommentReadSerializer(comentarios, many=True)
        return serializer.data

class BudgetCreateSerializer(serializers.ModelSerializer):
    vendedor = SellerSerializer(required=False, allow_null=True)
    documentos = DocumentWriteSerializer(many=True)
    responsaveis_fiscais = ResponsibleTaxSerializer(many=True)
    familia = FamilySerializer()
    servicos_documentos = ServiceDocumentSerializer(many=True, required=False)

    class Meta:
        model = Budget
        fields = '__all__'

    def create(self, validated_data):
        vendedor_data = validated_data.pop('vendedor', None)
        documentos_data = validated_data.pop('documentos')
        responsaveis_fiscais_data = validated_data.pop('responsaveis_fiscais')
        familia_data = validated_data.pop('familia')
        servicos_documentos_data = validated_data.pop('servicos_documentos', [])

        vendedor = None
        if vendedor_data:
            vendedor, created = Seller.objects.get_or_create(
                nome=vendedor_data['nome'], defaults=vendedor_data
            )

        familia, created = Family.objects.get_or_create(nome_da_familia=familia_data['nome_da_familia'])

        budget = Budget.objects.create(vendedor=vendedor, familia=familia, **validated_data)
        items = []
        for documento_data in documentos_data:
            documento = Document.objects.create(budget=budget, **documento_data)
            budget.documentos.add(documento)


        for responsavel_fiscal_data in responsaveis_fiscais_data:
            responsavel = ResponsibleTax.objects.create(budget=budget, **responsavel_fiscal_data)
            budget.responsaveis_fiscais.add(responsavel)

        for servico_documento_data in servicos_documentos_data:
            servico = ServiceDocument.objects.create(budget=budget, **servico_documento_data)
        budget.save()



        return budget

    def update(self, instance, validated_data):
        documentos_data = validated_data.pop('documentos', None)
        familia = validated_data.pop('familia', None)

        # Atualização dos documentos relacionados
        if familia:
            familia_instance, created = Family.objects.get_or_create(nome_da_familia=familia['nome_da_familia'])
            instance.familia = familia_instance


        if documentos_data:
            for documento_data in documentos_data:
                documento_id = documento_data.get('documento_id')
                if documento_id:
                    documento = Document.objects.get(documento_id=documento_id, budget=instance)
                    for attr, value in documento_data.items():
                        setattr(documento, attr, value)
                    documento.save()

        # Atualização dos outros campos do orçamento
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance