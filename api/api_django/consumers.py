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
