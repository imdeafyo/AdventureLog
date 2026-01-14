from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from adventures.models import Location


@receiver(m2m_changed, sender=Location.collections.through)
def update_adventure_publicity(sender, instance, action, **kwargs):
    """
    Signal handler to update adventure publicity when collections are added/removed
    This function checks if the adventure's collections contain any public collection.
    """
    if not isinstance(instance, Location):
        return
    # Only process when collections are added or removed
    if action in ('post_add', 'post_remove', 'post_clear'):
        collections = instance.collections.all()
        
        if collections.exists():
            # If any collection is public, make the adventure public
            has_public_collection = collections.filter(is_public=True).exists()
            
            if has_public_collection and not instance.is_public:
                instance.is_public = True
                instance.save(update_fields=['is_public'])
            elif not has_public_collection and instance.is_public:
                instance.is_public = False
                instance.save(update_fields=['is_public'])


@receiver(post_delete)
def _remove_collection_itinerary_items_on_object_delete(sender, instance, **kwargs):
    """
    When any model instance is deleted, remove any CollectionItineraryItem that
    refers to it via the GenericForeignKey (matches by ContentType and object_id).

    This ensures that if a referenced item (e.g. a `Location`, `Visit`, `Transportation`,
    `Note`, etc.) is deleted, the itinerary entry that pointed to it is also removed.
    """
    # Avoid acting when a CollectionItineraryItem itself is deleted
    # to prevent needless extra queries.
    if sender.__name__ == 'CollectionItineraryItem':
        return

    # Resolve the content type for the model that was deleted
    try:
        ct = ContentType.objects.get_for_model(sender)
    except Exception:
        return

    # Import here to avoid circular import problems at module import time
    from adventures.models import CollectionItineraryItem

    # Try matching the primary key in its native form first, then as a string.
    # CollectionItineraryItem.object_id is a UUIDField in the model, but some
    # senders might have different PK representations; handle both safely.
    pk = instance.pk
    deleted = False
    try:
        qs = CollectionItineraryItem.objects.filter(content_type=ct, object_id=pk)
        if qs.exists():
            qs.delete()
            deleted = True
    except Exception:
        pass

    if not deleted:
        try:
            CollectionItineraryItem.objects.filter(content_type=ct, object_id=str(pk)).delete()
        except Exception:
            # If deletion fails for any reason, do nothing; we don't want to
            # raise errors during another model's delete.
            pass
