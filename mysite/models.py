from django.db import models as m

class Usuario(m.Model):
    nome = m.CharField(max_length=30)
    email = m.EmailField(max_length=254, unique=True)
    senha = m.CharField(max_length=128)  # didático; em produção use AbstractUser
    is_admin = m.BooleanField(default=False)
    endereco = m.CharField(max_length=100, blank=True)
    telefone = m.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nome

class Categoria(m.Model):
    nome = m.CharField(max_length=50, unique=True)
    descricao = m.TextField(blank=True)

    def __str__(self):
        return self.nome

class Produto(m.Model):
    nome = m.CharField(max_length=100)
    descricao = m.TextField(blank=True)
    preco = m.DecimalField(max_digits=10, decimal_places=2)
    estoque = m.IntegerField(default=0)
    imagem = m.ImageField(upload_to='produtos/', blank=True, null=True)
    categoria = m.ForeignKey(Categoria, on_delete=m.CASCADE, related_name='produtos')

    def __str__(self):
        return self.nome

class Carrinho(m.Model):
    usuario = m.ForeignKey(Usuario, on_delete=m.CASCADE, related_name='carrinhos')
    data_criacao = m.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Carrinho #{self.id} de {self.usuario}'

class ItemCarrinho(m.Model):
    carrinho = m.ForeignKey(Carrinho, on_delete=m.CASCADE, related_name='itens')
    produto = m.ForeignKey(Produto, on_delete=m.CASCADE)
    quantidade = m.IntegerField(default=1)

    def __str__(self):
        return f'{self.quantidade} x {self.produto}'

class Pedido(m.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
    ]
    usuario = m.ForeignKey(Usuario, on_delete=m.CASCADE, related_name='pedidos')
    data_pedido = m.DateTimeField(auto_now_add=True)
    status = m.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    valor_total = m.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Pedido #{self.id} ({self.status})'

class ItemPedido(m.Model):
    pedido = m.ForeignKey(Pedido, on_delete=m.CASCADE, related_name='itens')
    produto = m.ForeignKey(Produto, on_delete=m.CASCADE)
    quantidade = m.IntegerField(default=1)
    preco_unitario = m.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantidade} x {self.produto} (Pedido #{self.pedido_id})'