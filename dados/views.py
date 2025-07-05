from rest_framework import viewsets, status
from dados.models import Customer, Translator, ServiceModalities, Family, Budget, CustomUser, Comment, ContaAzulToken, Document, ServiceDocument,Seller
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authtoken.models import Token
from dados.serializer import CustomerSerializer, CustomUserSerializer,TranslatorSerializer, ServiceWriteSerializer, ServiceModalitiesSerializer, FamilySerializer , ServiceReadSerializer, BudgetCreateSerializer, BudgetReadSerializer, CommentReadSerializer, CommentPostSerializer, SellerSerializer
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, IsAdminUser
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.db.models import Q, Max, Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

class CustomPagination(PageNumberPagination):
    page_size = 200  # Número padrão de itens por página
    page_size_query_param = 'page_size'
    max_page_size = 100

class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para listar, criar, editar e excluir usuários.
    """
    queryset = CustomUser.objects.filter(is_active=True).exclude(user_type='cliente')
    serializer_class = CustomUserSerializer
    authentication_classes = [TokenAuthentication]  # Autenticação por Token
    permission_classes = [IsAuthenticated]  # Apenas usuários autenticados podem acessar
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        queryset = CustomUser.objects.filter(is_active=True).exclude(user_type='cliente')
        # Se o usuário não for admin, exclua os usuários do tipo admin
        if user.user_type != 'admin':
            queryset = queryset.exclude(user_type='admin')

        user_type = self.request.query_params.get('user_type')
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        return queryset

class LoginView(APIView):
    def post(self, request, format=None):
        user = request.user  # Já autenticado pelo Basic Authentication
        print(user)
        if not user.is_active:
            return Response({'error': 'User is not active'}, status=400)

        if user.is_authenticated:
            token, created = Token.objects.get_or_create(user=user)
    #        translator = Translator.objects.filter(user=user).first()
            response_data = {
                    'token': token.key,
                    'username': user.username,
                    'user_id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'is_active': user.is_active,
                    'last_name': user.last_name,
                    'user_type': user.user_type,
                }
            if user.user_type == 'cliente':
                    try:
                        customer = Customer.objects.get(usuario=user)
                        response_data['cliente'] = CustomerSerializer(customer).data
                    except Customer.DoesNotExist:
                        response_data['cliente'] = None

            return Response(response_data)
        else:
            return Response({'error': 'Invalid credentials'}, status=400)
        
class LogoutView(APIView):
    def post(self, request, format=None):
        user = request.user  # Já autenticado pelo Basic Authentication
      
        if user.is_authenticated:
            token, created = Token.objects.get(user=user).delete()
            return Response({'token': f'Token deletado, logout efetuado.'})
        else:
            return Response({'error': 'Invalid credentials'}, status=400)

class VerifyTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        token = request.auth    

        if user and token:
            # Verifique se o token fornecido corresponde ao token do usuário no banco de dados
            if str(user.auth_token.key) == str(token):
                return Response({'message': 'Token is valid'}, status=200)
            else:
                return Response({'error': 'Token is not valid'}, status=400)
        else:
            return Response({'error': 'Invalid credentials'}, status=400)

class TranslatorViewSet(viewsets.ModelViewSet):
    queryset = Translator.objects.filter(ativo=True)
    serializer_class = TranslatorSerializer
    http_method_names = ['get', 'post', 'put', 'delete', 'update', 'patch']
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

# class ServiceViewSet(viewsets.ModelViewSet):
#     queryset = Service.objects.all()
#     http_method_names = ['get', 'post', 'put', 'delete', 'update']
#     pagination_class = CustomPagination
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     def get_serializer_class(self):
#         if self.action in ['create', 'update', 'partial_update']:
#             return ServiceWriteSerializer
#         return ServiceReadSerializer

class FamilyViewSet(viewsets.ModelViewSet):
    queryset = Family.objects.all()
    serializer_class = FamilySerializer
    http_method_names = ['get', 'post', 'put', 'delete', 'update']
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        family_name = self.request.query_params.get('family_name')
        if family_name:
            queryset = Family.objects.filter(nome_da_familia__contains=family_name)
        return queryset
        

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['nome', 'cpf']
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    """Consulta clientes com base no cpf ou cpf"""
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        nome_da_familia = data.pop('nome_da_familia', None)

        if nome_da_familia:
            familia, created = Family.objects.get_or_create(nome_da_familia=nome_da_familia)
            data['nome_da_familia'] = familia.familia_id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)
    
    def get_queryset(self):
        queryset = Customer.objects.filter(ativo=True)  # Consulta padrão
        
        nome =  self.request.query_params.get('nome')
        cpf_cnpj = self.request.query_params.get('cpf_cnpj')
        email = self.request.query_params.get('email')
        tipo_do_cliente = self.request.query_params.get('tipo_do_cliente')

        if tipo_do_cliente:
            queryset = queryset.filter(tipo_do_cliente=tipo_do_cliente)

        if nome:
            queryset = queryset.filter(nome__contains=nome) 
        
        if cpf_cnpj:
            queryset = queryset.filter(cpf_cnpj=cpf_cnpj) 
        
        if email:
            queryset = queryset.filter(email=email) 

        return queryset

class ModalidadeViewSet(viewsets.ModelViewSet):
    queryset = ServiceModalities.objects.all()
    serializer_class = ServiceModalitiesSerializer
    http_method_names = ['get', 'post', 'put', 'delete', 'update']
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class CustomerServicesViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BudgetCreateSerializer
        return BudgetReadSerializer

    def get_queryset(self):
        cliente_id = self.kwargs.get('cliente_id')
        queryset = Budget.objects.filter(cliente_id=cliente_id, arquivado=False, numero_ca__isnull=False).order_by('-data_criacao')
        data_criacao__gte = self.request.query_params.get('data_criacao__gte')
        data_criacao__lte = self.request.query_params.get('data_criacao__lte')
        cliente = self.request.query_params.get('cliente')
        arquivado = self.request.query_params.get('arquivado')
        familia = self.request.query_params.get('familia')
        numero_ca = self.request.query_params.get('numero_ca')
        tipo_de_servico = self.request.query_params.get('tipo_de_servico')
        finalizado = self.request.query_params.get('finalizado')
        prazo_vencimento = self.request.query_params.get('prazo_vencimento')
        tradutor = self.request.query_params.get('tradutor')
        cliente_id = self.request.query_params.get('cliente_id')

        if arquivado == 'true':
            arquivado = True
        elif arquivado == 'false':
            arquivado = False
        else:
            arquivado = False

        queryset = queryset.filter(arquivado=arquivado)

        if data_criacao__gte and data_criacao__lte:
            queryset = queryset.filter(data_criacao__gte=data_criacao__gte, data_criacao__lte=data_criacao__lte)

        if cliente:
            queryset = queryset.filter(cliente__nome__icontains=cliente)
        
        if familia:
            queryset = queryset.filter(familia__nome_da_familia__icontains=familia)
        
        if numero_ca:
            queryset = queryset.filter(numero_ca=numero_ca)
        
        if tipo_de_servico:
            queryset = queryset.filter(
                Q(lista_documentos__tipo_documento__icontains=tipo_de_servico) |
                Q(servicos_documentos__tipo_servico__icontains=tipo_de_servico)
            ).distinct()

        if prazo_vencimento:
            today = timezone.now().date()
            if prazo_vencimento == "Falta 3 dias":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo__gte=today, max_prazo__lte=today + timedelta(days=3))
            elif prazo_vencimento == "Falta 2 dias":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo__gte=today, max_prazo__lte=today + timedelta(days=2))
            elif prazo_vencimento == "Falta 1 dia":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo__gte=today, max_prazo__lte=today + timedelta(days=1))
            elif prazo_vencimento == "Vence hoje":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo=today)
            elif prazo_vencimento == "Venceu 1 dia":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo=today - timedelta(days=1))
            elif prazo_vencimento == "Venceu 2 dias":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo=today - timedelta(days=2))
            elif prazo_vencimento == "Venceu 3 dias":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo=today - timedelta(days=3))
            elif prazo_vencimento == "Venceu mais de 3 dias":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo__lt=today - timedelta(days=3))
        if tradutor:
            queryset = queryset.filter(lista_documentos__tradutor=tradutor).distinct()

        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)

        if finalizado == 'true':
            queryset = queryset.filter(status='FINALIZADO')
        elif finalizado == 'false':
            queryset = queryset.exclude(status='FINALIZADO')

        return queryset
         
"""São considerados serviços os orçamentos que possuem número de CA"""
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.filter(arquivado=False, numero_ca__isnull=False).order_by('-data_criacao')
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'put', 'delete', 'patch']
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BudgetCreateSerializer  # Caso os serviços usem o mesmo serializer
        return BudgetReadSerializer

    def get_queryset(self):
        queryset = Budget.objects.filter(arquivado=False, numero_ca__isnull=False).order_by('-data_criacao')
        data_criacao__gte = self.request.query_params.get('data_criacao__gte')
        data_criacao__lte = self.request.query_params.get('data_criacao__lte')
        cliente = self.request.query_params.get('cliente')
        arquivado = self.request.query_params.get('arquivado')
        familia = self.request.query_params.get('familia')
        numero_ca = self.request.query_params.get('numero_ca')
        tipo_de_servico = self.request.query_params.get('tipo_de_servico')
        finalizado = self.request.query_params.get('finalizado')
        prazo_vencimento = self.request.query_params.get('prazo_vencimento')
        tradutor = self.request.query_params.get('tradutor')
        cliente_id = self.request.query_params.get('cliente_id')
        apenas_meus_servicos = self.request.query_params.get('apenas_meus_servicos')

        if arquivado == 'true':
            arquivado = True
        elif arquivado == 'false':
            arquivado = False
        else:
            arquivado = False

        queryset = queryset.filter(arquivado=arquivado)

        if data_criacao__gte and data_criacao__lte:
            queryset = queryset.filter(data_criacao__gte=data_criacao__gte, data_criacao__lte=data_criacao__lte)

        if cliente:
            queryset = queryset.filter(cliente__nome__icontains=cliente)
        
        if familia:
            queryset = queryset.filter(familia__nome_da_familia__icontains=familia)
        
        if numero_ca:
            queryset = queryset.filter(numero_ca=numero_ca)
        
        if tipo_de_servico:
            queryset = queryset.filter(
                Q(lista_documentos__tipo_documento__icontains=tipo_de_servico) |
                Q(servicos_documentos__tipo_servico__icontains=tipo_de_servico)
            ).distinct()

        if prazo_vencimento:
            today = timezone.now().date()
            if prazo_vencimento == "Falta 3 dias":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo__gte=today, max_prazo__lte=today + timedelta(days=3))
            elif prazo_vencimento == "Falta 2 dias":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo__gte=today, max_prazo__lte=today + timedelta(days=2))
            elif prazo_vencimento == "Falta 1 dia":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo__gte=today, max_prazo__lte=today + timedelta(days=1))
            elif prazo_vencimento == "Vence hoje":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo=today)
            elif prazo_vencimento == "Venceu 1 dia":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo=today - timedelta(days=1))
            elif prazo_vencimento == "Venceu 2 dias":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo=today - timedelta(days=2))
            elif prazo_vencimento == "Venceu 3 dias":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo=today - timedelta(days=3))
            elif prazo_vencimento == "Venceu mais de 3 dias":
                queryset = queryset.annotate(max_prazo=Max('lista_documentos__prazo')).filter(max_prazo__lt=today - timedelta(days=3))
        if tradutor:
            queryset = queryset.filter(lista_documentos__tradutor=tradutor).distinct()

        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)

        if finalizado == 'true':
            queryset = queryset.filter(status='FINALIZADO')
        elif finalizado == 'false':
            queryset = queryset.exclude(status='FINALIZADO')
        
        if apenas_meus_servicos:
            user = self.request.user
            queryset = queryset.filter(vendedor__user=user)

        return queryset


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.filter(arquivado=False, numero_ca__isnull=True).order_by('-budget_id')
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'put', 'delete', 'patch']
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BudgetCreateSerializer
        return BudgetReadSerializer
    def get_queryset(self):
        queryset = Budget.objects.filter(arquivado=False, numero_ca__isnull=True).order_by('-budget_id')
        data_criacao__gte = self.request.query_params.get('data_criacao__gte')
        data_criacao__lte = self.request.query_params.get('data_criacao__lte')
        cliente = self.request.query_params.get('cliente')
        arquivado = self.request.query_params.get('arquivado')
        

        if arquivado == 'true':
            arquivado = True
        elif arquivado == 'false':
            arquivado = False
        else:
            arquivado = False

        if data_criacao__gte and data_criacao__lte:
            queryset = queryset.filter(data_criacao__gte=data_criacao__gte, data_criacao__lte=data_criacao__lte, arquivado=arquivado)
        
        if cliente:
            queryset = queryset.filter(cliente__nome__contains=cliente, arquivado=arquivado)

        
        return queryset
    

class SellerViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    http_method_names = ['get', 'post', 'put', 'delete', 'update', 'patch']
    permission_classes = [IsAuthenticated]
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer

class CommentViewSet(APIView):
    queryset = Comment.objects.all()
    http_method_names = ['post', 'put', 'delete', 'update', 'patch']
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = CommentPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk, format=None):
        comment = Comment.objects.get(pk=pk)
        comment.delete()
        return Response(status=204)
    
    def put(self, request, pk, format=None):
        comment = Comment.objects.get(pk=pk)
        serializer = CommentPostSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    
    def patch(self, request, pk, format=None):
        comment = Comment.objects.get(pk=pk)
        serializer = CommentPostSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    