from decimal import Decimal
from django.conf import settings
from products.models import Product

class Cart:
    def __init__(self, request):
        '''inicializa o carrinho.'''
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # salva um carrinho vazio na sessão
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        '''adiciona um produto ao carrinho ou atualiza a quantidade.'''  
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id]['quantity'] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        '''aplica a sessão como modificada.'''
        self.session.modified = True

    def remove(self, product):
        '''remove um produto do carrinho'''
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        '''itera pelos itens do carrinho e obtém os produtos do banco de dados.'''
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']    
            yield item

    def __len__(self):
        '''conta o número total de itens nocarrinho.'''
        return sum(item['quantity'] for item in self.cart.values())   

    def get_total_price(self):
        '''calculao preço total dos itens no carrinho.'''
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        '''esvazia o carrinho.'''
        del self.session[settings.CART_SESSION_ID]
        self.save()    