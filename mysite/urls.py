"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views  # 👈 suas views estão em mysite/views.py

urlpatterns = [
    path("admin/", admin.site.urls),

    # Catálogo público
    path("", views.lista_produtos, name="home"),
    path("produtos/", views.lista_produtos, name="lista_produtos"),
    path("produtos/categoria/<int:categoria_id>/", views.produtos_por_categoria, name="produtos_por_categoria"),
    path("produtos/<int:produto_id>/", views.detalhe_produto, name="detalhe_produto"),
    path("carrinho/", views.ver_carrinho, name="ver_carrinho"),
    path("carrinho/adicionar/<int:produto_id>/", views.adicionar_ao_carrinho, name="adicionar_ao_carrinho"),
    path("carrinho/remover/<int:produto_id>/", views.remover_do_carrinho, name="remover_do_carrinho"),
    path("carrinho/atualizar/<int:produto_id>/", views.atualizar_quantidade, name="atualizar_quantidade"),
    path("carrinho/limpar/", views.limpar_carrinho, name="limpar_carrinho"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
