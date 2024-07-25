from rest_framework import serializers
from consvc_shepherd.models import BoostrProduct


class BoostrProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = BoostrProduct
        fields = ('boostr_id','full_name', 'campaign_type')