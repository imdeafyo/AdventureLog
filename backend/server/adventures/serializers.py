class CollectionInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionInvite
        fields = [
            'id',
            'collection',
            'created_at',
            'name',
            'collection_owner_username',
            'collection_user_first_name',
            'collection_user_last_name',
        ]
        read_only_fields = ['id', 'created_at']


class UltraSlimCollectionSerializer(serializers.ModelSerializer):
    location_images = serializers.SerializerMethodField()
    location_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            'id', 'user', 'name', 'description', 'is_public', 'start_date', 'end_date',
            'is_archived', 'link', 'created_at', 'updated_at', 'location_images',
            'location_count', 'shared_with'
        ]
        read_only_fields = fields  # All fields are read-only for listing

    def get_location_images(self, obj):
        """Get primary images from locations in this collection, optimized with select_related"""
        images = ContentImage.objects.filter(
            location__collections=obj
        ).select_related('user').prefetch_related('location')

        return ContentImageSerializer(
            images,
            many=True,
            context={'request': self.context.get('request')}
        ).data

    def get_location_count(self, obj):
        """Get count of locations in this collection"""
        return obj.locations.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # show the uuid instead of the pk for the user
        representation['user'] = str(instance.user.uuid)

        # display the user uuid for the shared users instead of the PK
        shared_uuids = [str(user.uuid) for user in instance.shared_with.all()]
        representation['shared_with'] = shared_uuids
        return representation
