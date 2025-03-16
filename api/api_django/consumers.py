import json

from channels.generic.websocket import AsyncWebsocketConsumer


class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "orders_group"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_order_details(self, event):
        # Преобразуем Decimal в число или строку
        order_details = event["order_details"]
        order_details["total_price"] = float(
            order_details["total_price"]
        )  # Преобразуем в float
        for product in order_details["products"]:
            product["price"] = float(
                product["price"]
            )  # Преобразуем цену продукта в float

        # Отправляем заказ в WebSocket
        await self.send(text_data=json.dumps({"order_details": order_details}))

class CategoryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "category_group"
            # Подключаемся к группе
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
            # Отсоединяемся от группы при закрытии соединения
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_category_details(self, event):
        category_details = event["category_details"]
        await self.send(text_data=json.dumps({
            "category_details": category_details
        }))

class ProductConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "product_group"
            # Подключаемся к группе
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
            # Отсоединяемся от группы при закрытии соединения
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_product_details(self, event):
        product_details = event["product_details"]
        
        # Преобразуем Decimal в float
        product_details["price"] = float(product_details["price"])
        product_details["stock"] = float(product_details["stock"])  # Если stock - это Decimal

        # Если у тебя есть другие числовые поля, их тоже можно преобразовать аналогично:
        if "quantity" in product_details:
            product_details["quantity"] = float(product_details["quantity"])

        await self.send(text_data=json.dumps({
            "product_details": product_details
        }))