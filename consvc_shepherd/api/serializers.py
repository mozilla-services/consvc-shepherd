"""Serializers for the json API that drives the dashboard"""

from rest_framework import serializers

from consvc_shepherd.models import BoostrDeal, BoostrProduct, Campaign


class BoostrProductSerializer(serializers.ModelSerializer):
    """Turns BoostrProduct in-memory objects into json string"""

    class Meta:
        """Metadata to specify the way BoostrProduct is serialized"""

        model = BoostrProduct
        fields = "__all__"


class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for Campaign model"""

    campaign_fields = serializers.ListSerializer(
        child=serializers.DictField(), write_only=True
    )

    class Meta:
        """Metadata to specify the way Campaign is serialized"""

        model = Campaign
        fields = "__all__"

    def validate(self, data):
        """Validate campaign data, ensuring the deal exists and total net spend matches the deal amount."""
        deal = data.get("deal")
        if deal is None:
            raise serializers.ValidationError("Deal must be provided.")

        try:
            deal_data = BoostrDeal.objects.get(id=deal.id)
            deal_amount = deal_data.amount
        except BoostrDeal.DoesNotExist:
            raise serializers.ValidationError(f"Deal with name {deal} does not exist.")

        campaign_fields_data = data.get("campaign_fields", [])
        total_net_spend = sum(
            field.get("net_spend", 0) for field in campaign_fields_data
        ) + data.get("net_spend", 0)

        if total_net_spend != deal_amount:
            raise serializers.ValidationError(
                f"Total net spend ({total_net_spend}) from campaigns must equal the deal amount ({deal_amount})."
            )

        return data

    def create(self, validated_data):
        """Create a new campaign and update existing campaign fields based on validated data."""
        campaign_fields_data = validated_data.pop("campaign_fields", [])
        campaign = Campaign.objects.create(**validated_data)

        for field_data in campaign_fields_data:
            try:
                campaign_id = field_data.get("campaign_id")
                existing_campaign = Campaign.objects.get(id=campaign_id)
                existing_campaign.impressions_sold = field_data.get(
                    "impressions_sold", existing_campaign.impressions_sold
                )
                existing_campaign.net_spend = field_data.get(
                    "net_spend", existing_campaign.net_spend
                )
                existing_campaign.save()
            except Campaign.DoesNotExist:
                continue

        return campaign


class BoostrDealSerializer(serializers.ModelSerializer):
    """Serializer for BoostrDeal model"""

    class Meta:
        """Metadata for BoostrDealSerializer"""

        model = BoostrDeal
        fields = "__all__"
