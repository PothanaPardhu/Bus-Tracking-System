import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class BusTrackingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time bus tracking"""
    
    async def connect(self):
        try:
            self.bus_id = self.scope['url_route']['kwargs']['bus_id']
            self.room_group_name = f'bus_{self.bus_id}'

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            logger.info(f"Bus {self.bus_id} WebSocket connected")
        except Exception as e:
            logger.error(f"Connection error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"Bus {self.bus_id} WebSocket disconnected")
        except Exception as e:
            logger.error(f"Disconnection error: {e}")

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'location_update':
                await self.handle_location_update(data)
            elif message_type == 'status_update':
                await self.handle_status_update(data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Receive error: {e}")

    async def handle_location_update(self, data):
        """Handle location update from conductor's device"""
        try:
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            speed = data.get('speed', 0)
            heading = data.get('heading')

            # Save to database
            location = await self.save_location(
                self.bus_id, latitude, longitude, speed, heading
            )

            # Broadcast to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'location_update',
                    'data': location
                }
            )
        except Exception as e:
            logger.error(f"Location update error: {e}")

    async def handle_status_update(self, data):
        """Handle bus status update"""
        try:
            status = data.get('status')
            await self.update_bus_status(self.bus_id, status)

            # Broadcast to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'status_update',
                    'status': status
                }
            )
        except Exception as e:
            logger.error(f"Status update error: {e}")

    # Receive message from room group
    async def location_update(self, event):
        """Send location update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'data': event['data']
        }))

    async def status_update(self, event):
        """Send status update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': event['status']
        }))

    @database_sync_to_async
    def save_location(self, bus_id, latitude, longitude, speed, heading):
        """Save location to database"""
        try:
            from conductorapp.models import BusModels, BusLocationModels
            
            bus = BusModels.objects.get(bus_id=bus_id)
            location = BusLocationModels.objects.create(
                bus=bus,
                latitude=latitude,
                longitude=longitude,
                speed=speed,
                heading=heading
            )
            return {
                'location_id': location.location_id,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'speed': location.speed,
                'heading': location.heading,
                'timestamp': location.timestamp.isoformat() if location.timestamp else None,
                'bus_number': bus.bus_number
            }
        except Exception as e:
            logger.error(f"Error saving location: {e}")
            return None

    @database_sync_to_async
    def update_bus_status(self, bus_id, status):
        """Update bus status in database"""
        try:
            from conductorapp.models import BusModels
            
            bus = BusModels.objects.get(bus_id=bus_id)
            bus.bus_status = status
            bus.save()
            return True
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return False


class AdminDashboardConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for admin dashboard real-time updates"""
    
    async def connect(self):
        try:
            self.room_group_name = 'admin_dashboard'

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            logger.info("Admin dashboard WebSocket connected")
            
            # Send initial data
            await self.send_initial_data()
        except Exception as e:
            logger.error(f"Admin connection error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info("Admin dashboard WebSocket disconnected")
        except Exception as e:
            logger.error(f"Admin disconnection error: {e}")

    async def send_initial_data(self):
        """Send initial data about all active buses"""
        try:
            buses = await self.get_active_buses()
            await self.send(text_data=json.dumps({
                'type': 'initial_data',
                'buses': buses
            }))
        except Exception as e:
            logger.error(f"Error sending initial data: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'request_update':
                await self.send_initial_data()
        except Exception as e:
            logger.error(f"Admin receive error: {e}")

    async def bus_location_update(self, event):
        """Send bus location update to admin"""
        await self.send(text_data=json.dumps({
            'type': 'bus_location_update',
            'data': event['data']
        }))

    async def bus_status_change(self, event):
        """Send bus status change to admin"""
        await self.send(text_data=json.dumps({
            'type': 'bus_status_change',
            'bus_id': event['bus_id'],
            'status': event['status']
        }))

    @database_sync_to_async
    def get_active_buses(self):
        """Get all active buses"""
        try:
            from conductorapp.models import BusModels
            
            buses = BusModels.objects.filter(
                bus_status__in=['active', 'idle']
            ).values(
                'bus_id', 'bus_number', 'bus_route', 'bus_status'
            )
            return list(buses)
        except Exception as e:
            logger.error(f"Error getting buses: {e}")
            return []


        if message_type == 'location_update':
            await self.handle_location_update(data)
        elif message_type == 'status_update':
            await self.handle_status_update(data)

    async def handle_location_update(self, data):
        """Handle location update from conductor's device"""
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        speed = data.get('speed', 0)
        heading = data.get('heading')

        # Save to database
        location = await self.save_location(
            self.bus_id, latitude, longitude, speed, heading
        )

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'location_update',
                'data': location
            }
        )

    async def handle_status_update(self, data):
        """Handle bus status update"""
        status = data.get('status')
        await self.update_bus_status(self.bus_id, status)

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'status_update',
                'status': status
            }
        )

    # Receive message from room group
    async def location_update(self, event):
        """Send location update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'data': event['data']
        }))

    async def status_update(self, event):
        """Send status update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': event['status']
        }))

    @database_sync_to_async
    def save_location(self, bus_id, latitude, longitude, speed, heading):
        try:
            bus = BusModels.objects.get(bus_id=bus_id)
            location = BusLocationModels.objects.create(
                bus=bus,
                latitude=latitude,
                longitude=longitude,
                speed=speed,
                heading=heading
            )
            serializer = BusLocationSerializer(location)
            return serializer.data
        except Exception as e:
            print(f"Error saving location: {e}")
            return None

    @database_sync_to_async
    def update_bus_status(self, bus_id, status):
        try:
            bus = BusModels.objects.get(bus_id=bus_id)
            bus.bus_status = status
            bus.save()
            return True
        except Exception as e:
            print(f"Error updating status: {e}")
            return False


class AdminDashboardConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for admin dashboard real-time updates"""
    
    async def connect(self):
        self.room_group_name = 'admin_dashboard'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Send initial data
        await self.send_initial_data()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_initial_data(self):
        """Send initial data about all active buses"""
        buses = await self.get_active_buses()
        await self.send(text_data=json.dumps({
            'type': 'initial_data',
            'buses': buses
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'request_update':
            await self.send_initial_data()

    async def bus_location_update(self, event):
        """Send bus location update to admin"""
        await self.send(text_data=json.dumps({
            'type': 'bus_location_update',
            'data': event['data']
        }))

    async def bus_status_change(self, event):
        """Send bus status change to admin"""
        await self.send(text_data=json.dumps({
            'type': 'bus_status_change',
            'bus_id': event['bus_id'],
            'status': event['status']
        }))

    @database_sync_to_async
    def get_active_buses(self):
        try:
            buses = BusModels.objects.filter(bus_status__in=['active', 'idle'])
            serializer = BusSerializer(buses, many=True)
            return serializer.data
        except Exception as e:
            print(f"Error getting buses: {e}")
            return []
