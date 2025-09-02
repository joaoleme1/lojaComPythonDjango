from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Produto, Categoria
from decimal import Decimal
from django.contrib import messages
from .models import Produto

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


def _get_cart(session):
    cart = session.get("cart")
    if cart is None:
        cart = {}
        session["cart"] = cart
    return cart

def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    cart = request.session.get("cart", {})
    pid = str(produto_id)
    try:
        qty = int(request.POST.get("quantidade", 1))
    except (TypeError, ValueError):
        qty = 1
    if qty < 1:
        qty = 1

    if pid in cart:
        cart[pid]["quantidade"] += qty
    else:
        cart[pid] = {
            "nome": produto.nome,
            "preco": str(produto.preco),            
            "quantidade": qty,
            "imagem": produto.imagem.url if getattr(produto, "imagem", None) else None,
        }
    request.session["cart"] = cart
    request.session.modified = True
    messages.success(request, f"Adicionado {qty}× {produto.nome} ao carrinho.")
    return redirect(request.POST.get("next") or request.META.get("HTTP_REFERER") or "lista_produtos")

def ver_carrinho(request):
    cart = request.session.get("cart", {})
    itens, total = [], Decimal("0.00")
    for pid, data in cart.items():
        produto = Produto.objects.filter(pk=pid).first()
        preco = Decimal(data["preco"])
        qtd = int(data.get("quantidade", 1))
        subtotal = preco * qtd
        total += subtotal
        itens.append({
            "produto": produto,
            "produto_id": int(pid),
            "nome": data["nome"],
            "preco": preco,
            "quantidade": qtd,
            "subtotal": subtotal,
            "imagem": data.get("imagem"),
        })
    return render(request, "carrinho/ver.html", {"itens": itens, "total": total})

def remover_do_carrinho(request, produto_id):
    cart = request.session.get("cart", {})
    pid = str(produto_id)
    if pid in cart:
        del cart[pid]
        request.session["cart"] = cart
        request.session.modified = True
        messages.info(request, "Item removido do carrinho.")
    return redirect("ver_carrinho")

def atualizar_quantidade(request, produto_id):
    if request.method != "POST":
        return redirect("ver_carrinho")
    try:
        qty = int(request.POST.get("quantidade", 1))
    except (TypeError, ValueError):
        qty = 1
    if qty < 1:
        qty = 1

    cart = request.session.get("cart", {})
    pid = str(produto_id)
    if pid in cart:
        cart[pid]["quantidade"] = qty
        request.session["cart"] = cart
        request.session.modified = True
        messages.success(request, "Quantidade atualizada.")
    return redirect("ver_carrinho")

def limpar_carrinho(request):
    request.session["cart"] = {}
    request.session.modified = True
    messages.info(request, "Carrinho limpo.")
    return redirect("ver_carrinho")
