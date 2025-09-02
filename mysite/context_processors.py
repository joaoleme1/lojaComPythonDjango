from .models import Categoria
from decimal import Decimal


def categorias(request):
    # Carrega as categorias para mostrar na navbar (ordenadas)
    return {'categorias_navbar': Categoria.objects.order_by('nome')}

def carrinho_info(request):
    cart = request.session.get("cart", {})
    total_itens = sum(item.get("quantidade", 0) for item in cart.values())
    total_valor = sum(Decimal(item.get("preco", "0")) * item.get("quantidade", 0) for item in cart.values())
    return {
        "cart_total_itens": total_itens,
        "cart_total_valor": total_valor,
    }
