from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from config.command_safety import check_override
from orders.models import Order
from orders.services import cancel_unpaid_order

PAYMENT_GRACE_HOURS = 1


class Command(BaseCommand):
  help = 'Cancels unpaid orders older than the allowed number of hours and returns their stock'
  
  def add_arguments(self, parser):
    parser.add_argument(
      '--hours',
      type=int,
      default=None,
      help='Hours before an unpaid order expires (defaults to the UNPAID_ORDER_HOURS setting)'
    )
    
    parser.add_argument(
      '--dry-run',
      action='store_true',
      help='List the orders that would be cancelled without changing anything'
    )
    
    parser.add_argument(
      '--force',
      action='store_true',
      help='Allow a value below the configured one (only when DEBUG is on)'
    )
    
  def handle(self, *args, **options):
    hours = options['hours'] if options['hours'] is not None else settings.UNPAID_ORDER_HOURS
    
    if not options['dry_run']:
      check_override(hours, settings.UNPAID_ORDER_HOURS, options['force'], '--hours')
      
    now = timezone.now()
    cutoff = now - timedelta(hours=hours)
    grace_cutoff = now - timedelta(hours=PAYMENT_GRACE_HOURS)
    
    orders = Order.objects.filter(
      status='pending', created_at__lte=cutoff).exclude(payments__created_at__gte=grace_cutoff)
    )
    
    cancelled = 0
    failed = 0
    
    for order in orders:
      if options['dry_run']:
        self.stdout.write(f'Would cancel order #{order.id}')
        continue
      try:
        if cancel_unpaid_order(order):
          cancelled += 1
      except Exception as error:
        failed += 1
        self.stderr.write(f'Order #{order.id}: {error}')
        
    self.stdout.write(self.style.SUCCESS(f'{cancelled} order(s) cancelled, {failed} failed'))