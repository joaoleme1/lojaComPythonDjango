from .models import Categoria

def categorias(request):
    # Carrega as categorias para mostrar na navbar (ordenadas)
    return {'categorias_navbar': Categoria.objects.order_by('nome')}
