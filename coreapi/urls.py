from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from dados.views import CustomerViewSet ,CustomerServicesViewSet, LoginView, LogoutView, VerifyTokenView, TranslatorViewSet, ServiceViewSet, ModalidadeViewSet, FamilyViewSet, BudgetViewSet,CustomUserViewSet, CommentViewSet, SellerViewSet
schema_view = get_schema_view(
   openapi.Info(
      title="Papello API",
      default_version='v1',
      description="API feita par manipular dados da Papello",
      terms_of_service="",
      contact=openapi.Contact(email="automacao@papello.com.br"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
pedido_swagger_parameters = [
    openapi.Parameter('status', openapi.IN_QUERY, description="Status do pedido", type=openapi.TYPE_STRING),
    openapi.Parameter('data_inicial', openapi.IN_QUERY, description="Data inicial do período de consulta", type=openapi.TYPE_STRING, format="date"),
    openapi.Parameter('data_final', openapi.IN_QUERY, description="Data final do período de consulta", type=openapi.TYPE_STRING, format="date"),
]

router = routers.DefaultRouter()
router.register('tradutores', TranslatorViewSet , basename='Tradutores')
router.register('clientes', CustomerViewSet , basename='Clientes')
router.register('servicos', ServiceViewSet , basename='Servicos')
router.register('modalidades-servicos', ModalidadeViewSet , basename='Modalidades de Servicos')
router.register('familias', FamilyViewSet , basename='Familias')
router.register('vendedores', SellerViewSet, basename='vendedores')
router.register(r'orcamentos', BudgetViewSet)
router.register(r'usuarios', CustomUserViewSet, basename='customuser')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('verify-token/', VerifyTokenView.as_view(), name='verify_token'),
    path('comentarios/',CommentViewSet.as_view(), name='comentarios'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('clientes/<int:cliente_id>/servicos', CustomerServicesViewSet.as_view({'get': "list"}), name='cliente_orcamentos'),

]
