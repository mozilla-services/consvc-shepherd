"""Serializers for the json API that drives the dashboard"""

from rest_framework import serializers

from consvc_shepherd.models import BoostrProduct


class BoostrProductSerializer(serializers.ModelSerializer):
    """Turns BoostrProduct in-memory objects into json string"""

    class Meta:
        """Metadata to specify the way BoostrProduct is serialized"""

        model = BoostrProduct
        fields = "__all__"
