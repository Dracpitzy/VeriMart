from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from config.command_safety import check_override
from cart.models import CartItem


class Command(BaseCommand):
  help = 'Removes cart items that were added more than the allowed number of days ago'
  
  
  def add_arguments(self, parser):
    parser.add_argument(
      '--days',
      type=int,
      default=None, help='Days before a cart item is removed (defaults to the STALE_CART_DAYS settings)'
    )
    
    parser.add_argument(
      '--dry-run', action='store_true',
      help='Show how many cart items would be removed without deleting anything'
    )
    
    parser.add_argument(
      '--force',
      action='store_true',
      help='Allow a value below the configured one (only when DEBUG is on)'
    )
    
  
  def handle(self, *args, **options):
    days = options['days'] if options['days'] is None else settings.STALE_CART_DAYS
    
    if not options['dry_run']:
      check_override(days, settings.STALE_CART_DAYS, options['force'], '--days')
      
    cutoff = timezone.now() - timedelta(days=days)
    
    stale_items = CartItem.objects.filter(added_at__lte=cutoff)
    
    if options['dry_run']:
      self.stdout.write(f'Would remove {stale_items.count()} cart item(s)')
      return
    
    deleted, _ = stale_items.delete()
    self.stdout.write(self.style.SUCCESS(f'{deleted} cart item(s) removed'))