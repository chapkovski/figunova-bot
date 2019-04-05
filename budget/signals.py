from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Payment
import logging
from transactions.gsheets import register_payment, delete_record, update_record
# from .config import huey  # import the "huey" object.
from .tasks import huey_update_record  # import any tasks / decorated functions

logger = logging.getLogger('budget.signals')


@receiver(post_save, sender=Payment)
def update_gsheet_record(sender, instance, created, update_fields, **kwargs):
    if created:
        logger.info(f'Payment {instance.update} has been successfully created')
        register_payment(instance)
    else:
        logger.info(f'Payment {instance.update} info has been updated')
        huey_update_record(instance).get()


@receiver(post_delete, sender=Payment)
def delete_gsheet_record(sender, instance, **kwargs):
    logger.info(f'Payment {instance.update}  has been deleted')
    delete_record(instance)
