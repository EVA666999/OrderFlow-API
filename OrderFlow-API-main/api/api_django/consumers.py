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
        order_details = event["order_details"]
        order_details["total_price"] = float(order_details["total_price"])
        order_details["products"] = [
            {
                "id": product.get("product__id"),
                "name": product.get("product__name"),
                "price": float(product.get("product__price", 0)),
                "quantity": int(product.get("product__quantity", 0)),
            }
            for product in order_details["products"]
        ]

        await self.send(text_data=json.dumps({"order_details": order_details}))


class CategoryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "category_group"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_category_details(self, event):
        category_details = event["category_details"]
        await self.send(text_data=json.dumps({"category_details": category_details}))


class ProductConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "product_group"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_product_details(self, event):
        product_details = event["product_details"]
        product_details["price"] = float(product_details["price"])
        product_details["stock"] = float(product_details["stock"])

        if "quantity" in product_details:
            product_details["quantity"] = float(product_details["quantity"])

        await self.send(text_data=json.dumps({"product_details": product_details}))


class ReviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "review_group"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_review_details(self, event):
        review_details = event["review_details"]
        await self.send(text_data=json.dumps({"review_details": review_details}))
