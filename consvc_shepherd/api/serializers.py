from rest_framework import serializers
from consvc_shepherd.models import BoostrProduct

class BoostrProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoostrProduct
        fields = '__all__'
