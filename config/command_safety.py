from django.conf import settings
from django.core.management.base import CommandError
def check_override(value, minimum, force, option_name):
  if value >= minimum:
    return
  
  if not force:
    raise CommandError(
      f'{option_name} {value} is below the configured value of {minimum}. '
      f'Use --force to override it (only allowed when DEBUG is on).'
    )
    
  if not settings.DEBUG:
    raise CommandError(
      '--force is only allowed when DEBUG is on. Change the setting instead. '
    )
  # Reaching here means the value is below the setting, but --force was given
  # and DEBUG is on, so the override is allowed.