from django.contrib import admin
from django.utils.html import format_html

from .models import Usuario, Categoria, Produto, Carrinho, ItemCarrinho, Pedido, ItemPedido


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'is_admin')
    search_fields = ('nome', 'email')
    list_filter = ('is_admin',)
    ordering = ('nome',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)
    ordering = ('nome',)
    # Se quiser slug:
    # prepopulated_fields = {'slug': ('nome',)}


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'estoque', 'categoria', 'imagem_preview')
    search_fields = ('nome', 'descricao')
    list_filter = ('categoria',)
    ordering = ('nome',)
    list_editable = ('preco', 'estoque')
    readonly_fields = ('imagem_preview',)

    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" style="max-height:200px;" />', obj.imagem.url)
        return "Nenhuma imagem"
    imagem_preview.short_description = 'Preview da Imagem'


class ItemCarrinhoInline(admin.TabularInline):
    model = ItemCarrinho
    extra = 0
    readonly_fields = ('produto', 'quantidade')
    can_delete = False
    show_change_link = True
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Carrinho)
class CarrinhoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'data_criacao')
    search_fields = ('usuario__nome', 'usuario__email')
    ordering = ('-data_criacao',)
    readonly_fields = ('data_criacao',)
    inlines = [ItemCarrinhoInline]


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('produto', 'quantidade', 'preco_unitario')
    can_delete = False
    show_change_link = True
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'data_pedido', 'status', 'valor_total')
    search_fields = ('usuario__nome', 'usuario__email')
    list_filter = ('status', 'data_pedido')
    ordering = ('-data_pedido',)
    readonly_fields = ('data_pedido', 'valor_total')
    inlines = [ItemPedidoInline]
