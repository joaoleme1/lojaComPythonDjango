from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Produto, Categoria

def lista_produtos(request):
    q = (request.GET.get('q') or "").strip()
    produtos_qs = Produto.objects.all().select_related('categoria')

    if q:
        produtos_qs = produtos_qs.filter(
            Q(nome__icontains=q) | Q(descricao__icontains=q)
        )

    produtos_qs = produtos_qs.order_by('nome')

    paginator = Paginator(produtos_qs, 12)  # 12 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    contexto = {
        'page_obj': page_obj,
        'q': q,
        'total': produtos_qs.count(),
        'categoria': None,  # para reaproveitar o mesmo template
    }
    return render(request, 'produtos/lista.html', contexto)


def produtos_por_categoria(request, categoria_id: int):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    q = (request.GET.get('q') or "").strip()

    produtos_qs = Produto.objects.filter(categoria=categoria).select_related('categoria')
    if q:
        produtos_qs = produtos_qs.filter(
            Q(nome__icontains=q) | Q(descricao__icontains=q)
        )

    produtos_qs = produtos_qs.order_by('nome')

    paginator = Paginator(produtos_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    contexto = {
        'page_obj': page_obj,
        'q': q,
        'total': produtos_qs.count(),
        'categoria': categoria,  # para o título/estado do template
    }
    return render(request, 'produtos/lista.html', contexto)


def detalhe_produto(request, produto_id: int):
    produto = get_object_or_404(Produto, id=produto_id)
    return render(request, 'produtos/detalhe.html', {'produto': produto})
