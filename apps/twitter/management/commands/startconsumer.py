from django.core.management.base import BaseCommand
from app_libs.rabbitmq_utils import consume_message
from app_libs.rabbitmq_utils import callback  # Ensure this is defined somewhere

class Command(BaseCommand):
    help = 'Starts the RabbitMQ consumer'

    def handle(self, *args, **options):
        consume_message('my_queue', callback)