from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Produto, Categoria
from decimal import Decimal
from django.contrib import messages
from .models import Produto
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Produto, Pedido, ItemPedido, Usuario
from .forms import CheckoutForm
import secrets
import re


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


def checkout(request):
    # 1) Verifica carrinho
    cart = request.session.get("cart", {})
    if not cart:
        messages.info(request, "Seu carrinho está vazio.")
        return redirect("ver_carrinho")

    # 2) Monta itens para exibir e somar
    itens, total = [], Decimal("0.00")
    produto_ids = [int(pid) for pid in cart.keys()]
    produtos_qs = Produto.objects.filter(pk__in=produto_ids)
    produtos_map = {p.id: p for p in produtos_qs}

    for pid_str, data in cart.items():
        pid = int(pid_str)
        p = produtos_map.get(pid)
        if not p:
            # produto foi removido do catálogo; ignora no resumo e limpa do carrinho
            continue
        preco = Decimal(data["preco"])
        qtd = int(data.get("quantidade", 1))
        subtotal = preco * qtd
        total += subtotal
        itens.append({
            "produto": p,
            "produto_id": pid,
            "nome": p.nome,
            "preco": preco,
            "quantidade": qtd,
            "subtotal": subtotal,
            "imagem": data.get("imagem"),
            "estoque": p.estoque,
        })

    if request.method == "GET":
        form = CheckoutForm()
        return render(request, "checkout/checkout.html", {"itens": itens, "total": total, "form": form})

    # POST - valida form
    form = CheckoutForm(request.POST)
    if not form.is_valid():
        return render(request, "checkout/checkout.html", {"itens": itens, "total": total, "form": form})

    nome = form.cleaned_data["nome"].strip()
    email = form.cleaned_data["email"].strip().lower()
    telefone_raw = (form.cleaned_data.get("telefone") or "").strip()
    endereco = form.cleaned_data["endereco"].strip()
    observacoes = form.cleaned_data.get("observacoes") or ""

    # Normaliza telefone para números apenas; se vazio, usa 0 (ajuste se seu campo permitir null/blank)
    telefone_digits = re.sub(r"\D", "", telefone_raw)
    telefone_int = int(telefone_digits) if telefone_digits else 0

    # 3) Transação: trava estoque, valida, cria pedido e itens
    with transaction.atomic():
        # Trava linhas dos produtos
        produtos_locked = Produto.objects.select_for_update().filter(pk__in=produto_ids)
        produtos_lock_map = {p.id: p for p in produtos_locked}

        # Valida estoque
        sem_estoque = []
        for item in itens:
            p = produtos_lock_map.get(item["produto_id"])
            qtd = item["quantidade"]
            if not p or p.estoque < qtd:
                sem_estoque.append((item["nome"], p.estoque if p else 0, qtd))

        if sem_estoque:
            msg_lines = ["Alguns itens não têm estoque suficiente:"]
            for nome_p, disponivel, solicitado in sem_estoque:
                msg_lines.append(f"• {nome_p}: disponível {disponivel}, solicitado {solicitado}")
            messages.error(request, "\n".join(msg_lines))
            return redirect("ver_carrinho")

        # Cria/atualiza "Usuario" (checkout convidado)
        usuario, _created = Usuario.objects.get_or_create(
            email=email,
            defaults={
                "nome": nome,
                "senha": secrets.token_hex(8)[:20],  # sua model é CharField simples
                "is_admin": False,
                "endereco": endereco,
                "telefone": telefone_int,
            },
        )
        # Se já existia, atualiza dados básicos (sem tocar em is_admin)
        usuario.nome = nome or usuario.nome
        usuario.endereco = endereco or usuario.endereco
        try:
            usuario.telefone = telefone_int
        except Exception:
            pass
        usuario.save()

        # Cria Pedido e ItemPedido
        pedido = Pedido.objects.create(usuario=usuario, status="pendente", valor_total=Decimal("0.00"))
        total_final = Decimal("0.00")

        for item in itens:
            p = produtos_lock_map[item["produto_id"]]
            qtd = item["quantidade"]
            preco_unit = item["preco"]

            ItemPedido.objects.create(
                pedido=pedido,
                produto=p,
                quantidade=qtd,
                preco_unitario=preco_unit,
            )

            # Debita estoque
            p.estoque = F("estoque") - qtd
            p.save(update_fields=["estoque"])

            total_final += preco_unit * qtd

        # Atualiza total do pedido
        pedido.valor_total = total_final
        pedido.save(update_fields=["valor_total"])

    # 4) Limpa carrinho e redireciona
    request.session["cart"] = {}
    request.session.modified = True
    messages.success(request, "Pedido criado com sucesso!")
    return redirect("pedido_sucesso", pedido_id=pedido.id)


def pedido_sucesso(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    itens = ItemPedido.objects.filter(pedido=pedido).select_related("produto")
    return render(request, "checkout/sucesso.html", {"pedido": pedido, "itens": itens})
