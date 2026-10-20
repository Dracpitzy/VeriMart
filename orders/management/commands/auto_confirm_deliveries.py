from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from config.command_safety import check_override
from orders.models import Order
from orders.services import mark_order_delivered
from payment.models import SellerBalance


class Command(BaseCommand):
  help = 'Marks shipped orders as delivered once they have been shipped for longer than the allowed number of days'
  
  def add_arguments(self, parser):
    parser.add_argument(
      '--days', type=int, default=None,
      help='Days to wait after shipping (defaults to the AUTO_CONFIRM_DELIVERY_DAYS setting)'
    )
    parser.add_argument(
      '--dry-run',
      action='store_true',
      help='List the orders that would be confirmed without changing anything'
    )
    
    parser.add_argument(
      '--force',
      action='store_true',
      help='Allow a value below the configured one (only when DEBUG is on)'
    )
    
  def handle(self, *args, **options):
    days = options['days'] if options['days'] is not None else settings.AUTO_CONFIRM_DELIVERY_DAYS
    
    if not options['dry_run']:
      check_override(days, settings.AUTO_CONFIRM_DELIVERY_DAYS, options['force'], '--days')
    cutoff = timezone.now() - timedelta(days=days)
    
    orders = Order.objects.filter(
      status='shipped', shipped_at__isnull=False, shipped_at__lte=cutoff
    )
    
    confirmed = 0
    failed = 0
    
    for order in orders:
      if options['dry_run']:
        self.stdout.write(f'Would confirm order #{order.id}')
      try:
        if mark_order_delivered(order):
          confirmed += 1
      except SellerBalance.DoesNotExist:
        failed += 1
        self.stderr.write(f'Order #{order.id}: a seller balance record is missing, skipped')
        
    self.stdout.write(self.style.SUCCESS(f'{confirmed} order(s) confirmed, {failed} failed'))